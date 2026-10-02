from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import sys

import numpy as np
import pytest


AREA = Path(__file__).resolve().parents[1]
RUNNER_PATH = AREA / "CODE" / "run_n001.py"
CONFIG_PATH = AREA / "CONFIG" / "n001_repair_config.json"
SPEC = importlib.util.spec_from_file_location("n001_runner_under_test", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)

# Imported after the runner module has put the shared engine on sys.path.
from engine.hypothesis_testing.prereg import freeze_config  # noqa: E402


@pytest.fixture(scope="module")
def smoke_run(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, dict]:
    output = tmp_path_factory.mktemp("n001-smoke-output") / "artifact"
    summary = runner.run_experiment(CONFIG_PATH, "smoke", output)
    return output, summary


def test_smoke_raw_round_trip_is_flat_nonempty_and_tail_exact(smoke_run: tuple[Path, dict]) -> None:
    output, _ = smoke_run
    manifest = runner.validate_artifact(output, CONFIG_PATH, "smoke")
    _, manifest_name, _ = runner.artifact_names("smoke")
    manifest_disk = json.loads((output / manifest_name).read_text(encoding="utf-8"))
    assert manifest_disk["raw_array_ndim"] == 1
    assert manifest_disk["raw_array_dtype"] == "little-endian int64"
    assert manifest_disk["largest_cluster_policy"] == "remove_one_per_realization_before_pooling"

    db_name = manifest["artifact"]["filename"]
    with runner._connect_readonly(output / db_name) as conn:
        rows = conn.execute(
            """
            SELECT L, realization_id, p_arm, full_sizes, storage_ndim,
                   n_clusters, n_tail, tail_sha256
            FROM cluster_arrays
            ORDER BY L, realization_index, p_arm
            """
        ).fetchall()
    assert rows
    total_tail = 0
    for row in rows:
        assert row["storage_ndim"] == 1
        full = np.frombuffer(bytes(row["full_sizes"]), dtype="<i8")
        assert full.ndim == 1
        assert full.size == row["n_clusters"]
        assert np.all(full > 0)
        assert np.all(np.diff(full) <= 0)
        tail = full[1:]
        assert tail.ndim == 1
        assert tail.size == row["n_tail"]
        assert runner.sha256_bytes(runner._int64_bytes(tail)) == row["tail_sha256"]
        total_tail += tail.size
    assert total_tail > 0

    tau_L = manifest["active_tau_L"]
    canonical_ids, canonical_tails = runner.load_tails(output, manifest, tau_L, "canonical")
    refined_ids, refined_tails = runner.load_tails(output, manifest, tau_L, "refined")
    assert canonical_ids == refined_ids
    assert any(tail.size > 0 for tail in canonical_tails)
    assert any(tail.size > 0 for tail in refined_tails)


def test_empty_realization_uses_zero_tail_metadata_not_negative_length(tmp_path: Path) -> None:
    config = copy.deepcopy(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
    config["p_values"]["canonical"] = 0.0
    config["p_values"]["refined"] = 0.0
    profile = copy.deepcopy(config["profiles"]["smoke"])
    profile["L_list"] = [2]
    profile["n_real"] = {"2": 1}
    profile["tau_L"] = 2
    db_path = tmp_path / "empty.sqlite3"

    runner._create_database(
        db_path,
        config,
        runner.sha256_file(CONFIG_PATH),
        "smoke",
        profile,
    )
    with runner._connect_readonly(db_path) as conn:
        row = conn.execute(
            "SELECT n_clusters, tail_start, n_tail, full_sizes FROM cluster_arrays LIMIT 1"
        ).fetchone()
    assert row["n_clusters"] == 0
    assert row["tail_start"] == 0
    assert row["n_tail"] == 0
    assert bytes(row["full_sizes"]) == b""


def test_masks_are_paired_by_common_uniform_stream(smoke_run: tuple[Path, dict]) -> None:
    output, _ = smoke_run
    manifest = runner.validate_artifact(output, CONFIG_PATH, "smoke")
    db_path = output / manifest["artifact"]["filename"]
    with runner._connect_readonly(db_path) as conn:
        rows = conn.execute(
            "SELECT L, realization_index, realization_id, uniform_sha256, canonical_mask, refined_mask FROM realizations"
        ).fetchall()
    assert rows
    differing_masks = 0
    for row in rows:
        L = int(row["L"])
        canonical = runner.unpack_mask(bytes(row["canonical_mask"]), L * L)
        refined = runner.unpack_mask(bytes(row["refined_mask"]), L * L)
        assert row["uniform_sha256"] == runner.sha256_bytes(
            runner.generate_uniforms(
                "AUDIT-N001-QP007-v1",
                "N001-QP007-CLUSTER-TAU-REPAIR",
                L,
                int(row["realization_index"]),
            ).tobytes()
        )
        # The refined threshold is lower, so its mask can only be a subset of
        # the canonical mask under this common-uniform pairing. The fixed smoke
        # stream also includes realizations for which the pair is not identical.
        assert np.all(~refined | canonical)
        differing_masks += int(not np.array_equal(canonical, refined))
    assert differing_masks > 0


def test_cumulative_estimator_uses_tau_one_minus_survival_slope() -> None:
    sizes = np.arange(1, 1001, dtype=np.int64)
    counts = np.maximum(1, np.rint(2_000_000 / sizes**2).astype(np.int64))
    synthetic_tail = np.repeat(sizes, counts)
    fit = runner.fit_tau([synthetic_tail], "cumulative", 2, 500)
    assert fit is not None
    assert fit["slope"] < 0
    assert fit["tau"] == pytest.approx(1.0 - fit["slope"], rel=0, abs=1e-12)
    assert 1.8 < fit["tau"] < 2.2


def test_bootstrap_is_paired_realization_block_not_iid_cluster(smoke_run: tuple[Path, dict]) -> None:
    _, summary = smoke_run
    assert summary["summary_schema"] == "n001-qp007-summary-v3"
    assert summary["cumulative_tau_definition"].startswith("tau = 1 - survival_slope")
    assert summary["active_tau_L"] == 16
    assert summary["scientific_result"] is None
    assert summary["status"] == "INFRASTRUCTURE_SMOKE_ONLY_NOT_A_SCIENTIFIC_RESULT"
    for window in summary["fits"].values():
        for fit in window.values():
            bootstrap = fit["bootstrap"]
            assert bootstrap["resampling_unit"] == "realization_block"
            assert bootstrap["clusters_resampled_individually"] is False
            assert bootstrap["paired_across_p_arms"] is True
            assert bootstrap["block_size"] == 1
            assert bootstrap["draws_successful"] >= bootstrap["draws_requested"] * 0.8


def test_smoke_configuration_is_bitwise_deterministic_at_raw_record_level(
    smoke_run: tuple[Path, dict], tmp_path: Path
) -> None:
    first_output, first_summary = smoke_run
    second_output = tmp_path / "deterministic-repeat"
    second_summary = runner.run_experiment(CONFIG_PATH, "smoke", second_output)
    first_manifest = runner.validate_artifact(first_output, CONFIG_PATH, "smoke")
    second_manifest = runner.validate_artifact(second_output, CONFIG_PATH, "smoke")

    def raw_fingerprints(artifact: Path, manifest: dict) -> list[tuple]:
        with runner._connect_readonly(artifact / manifest["artifact"]["filename"]) as conn:
            return [
                tuple(row)
                for row in conn.execute(
                    """
                    SELECT L, realization_index, realization_id, p_arm,
                           full_sizes_sha256, tail_sha256
                    FROM cluster_arrays
                    ORDER BY L, realization_index, p_arm
                    """
                )
            ]

    assert raw_fingerprints(first_output, first_manifest) == raw_fingerprints(second_output, second_manifest)
    assert first_summary == second_summary


def test_active_tau_l_comes_from_selected_config_profile(tmp_path: Path) -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    config["profiles"]["smoke"]["L_list"].append(32)
    config["profiles"]["smoke"]["n_real"]["32"] = 8
    config["profiles"]["smoke"]["tau_L"] = 32
    changed_config = tmp_path / "changed_smoke_config.json"
    changed_config.write_text(json.dumps(config, indent=2), encoding="utf-8")
    output = tmp_path / "tau32-artifact"
    summary = runner.run_experiment(changed_config, "smoke", output)
    manifest = runner.validate_artifact(output, changed_config, "smoke")
    assert manifest["active_tau_L"] == 32
    assert manifest["active_tau_L"] != 16
    assert summary["active_tau_L"] == 32
    assert summary["active_tau_L_source"] == "profiles.smoke.tau_L"


def test_required_missing_and_malformed_artifacts_fail_closed(
    smoke_run: tuple[Path, dict], tmp_path: Path
) -> None:
    source, _ = smoke_run
    manifest = runner.validate_artifact(source, CONFIG_PATH, "smoke")
    db_name = manifest["artifact"]["filename"]
    _, manifest_name, _ = runner.artifact_names("smoke")

    missing = tmp_path / "missing"
    shutil.copytree(source, missing)
    (missing / db_name).unlink()
    with pytest.raises(runner.ArtifactError, match="required raw binary artifact is missing"):
        runner.validate_artifact(missing, CONFIG_PATH, "smoke")

    missing_manifest = tmp_path / "missing-manifest"
    shutil.copytree(source, missing_manifest)
    (missing_manifest / manifest_name).unlink()
    with pytest.raises(runner.ArtifactError, match="expected exactly one N-001 manifest"):
        runner.validate_artifact(missing_manifest, CONFIG_PATH, "smoke")

    malformed = tmp_path / "malformed"
    shutil.copytree(source, malformed)
    with sqlite3.connect(malformed / db_name) as conn:
        conn.execute("PRAGMA ignore_check_constraints=ON")
        conn.execute("UPDATE cluster_arrays SET storage_ndim = 2")
        conn.commit()
    malformed_manifest = json.loads((malformed / manifest_name).read_text(encoding="utf-8"))
    malformed_manifest["artifact"]["sha256"] = runner.sha256_file(malformed / db_name)
    malformed_manifest["artifact"]["size_bytes"] = (malformed / db_name).stat().st_size
    (malformed / manifest_name).write_text(json.dumps(malformed_manifest, indent=2), encoding="utf-8")
    with pytest.raises(runner.ArtifactError, match="nested arrays are forbidden|storage_ndim"):
        runner.validate_artifact(malformed, CONFIG_PATH, "smoke")


def test_summary_tampering_fails_even_when_manifest_hash_is_updated(
    smoke_run: tuple[Path, dict], tmp_path: Path
) -> None:
    source, _ = smoke_run
    target = tmp_path / "summary-tampered"
    shutil.copytree(source, target)
    manifest_path = next(target.glob("*_manifest.json"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    summary_path = target / manifest["summary"]["filename"]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["fits"]["smoke_primary"]["cumulative"]["canonical"]["tau"] = 999.0
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    manifest["summary"]["sha256"] = runner.sha256_file(summary_path)
    manifest["summary"]["size_bytes"] = summary_path.stat().st_size
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    with pytest.raises(runner.ArtifactError, match="does not exactly match canonical analysis"):
        runner.validate_artifact(target, CONFIG_PATH, "smoke")


def test_runner_hash_mismatch_fails_closed(
    smoke_run: tuple[Path, dict], tmp_path: Path
) -> None:
    source, _ = smoke_run
    target = tmp_path / "runner-hash-mismatch"
    shutil.copytree(source, target)
    manifest_path = next(target.glob("*_manifest.json"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["runner"]["sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    with pytest.raises(runner.ArtifactError, match="current canonical runner"):
        runner.validate_artifact(target, CONFIG_PATH, "smoke")


def test_cluster_array_must_equal_components_of_regenerated_mask(
    smoke_run: tuple[Path, dict], tmp_path: Path
) -> None:
    source, _ = smoke_run
    target = tmp_path / "cluster-components-mismatch"
    shutil.copytree(source, target)
    manifest_path = next(target.glob("*_manifest.json"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    db_path = target / manifest["artifact"]["filename"]

    selected = None
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        for row in conn.execute(
            "SELECT L, realization_id, realization_index, p_arm, full_sizes FROM cluster_arrays ORDER BY L, realization_index, p_arm"
        ):
            sizes = np.frombuffer(bytes(row["full_sizes"]), dtype="<i8")
            if sizes.size >= 3 and int(sizes[0]) - int(sizes[1]) >= 2:
                selected = row
                break
        assert selected is not None
        original = np.frombuffer(bytes(selected["full_sizes"]), dtype="<i8").copy()
        tampered = original.copy()
        tampered[0] -= 1
        tampered[1] += 1
        full_hash = runner.sha256_bytes(runner._int64_bytes(tampered))
        tail_hash = runner.sha256_bytes(runner._int64_bytes(tampered[1:]))
        conn.execute(
            """
            UPDATE cluster_arrays
            SET full_sizes = ?, largest_size = ?, full_sizes_sha256 = ?, tail_sha256 = ?
            WHERE L = ? AND realization_id = ? AND p_arm = ?
            """,
            (
                sqlite3.Binary(runner._int64_bytes(tampered)),
                int(tampered[0]),
                full_hash,
                tail_hash,
                int(selected["L"]),
                str(selected["realization_id"]),
                str(selected["p_arm"]),
            ),
        )
        conn.commit()

    for record in manifest["realizations"]:
        if (
            int(record["L"]) == int(selected["L"])
            and record["realization_id"] == str(selected["realization_id"])
        ):
            arm_record = record["p_arms"][str(selected["p_arm"])]
            arm_record["largest_cluster_removed"] = int(tampered[0])
            arm_record["full_sizes_sha256"] = full_hash
            arm_record["tail_sha256"] = tail_hash
            break
    manifest["artifact"]["sha256"] = runner.sha256_file(db_path)
    manifest["artifact"]["size_bytes"] = db_path.stat().st_size
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    with pytest.raises(runner.ArtifactError, match="components of the regenerated mask"):
        runner.validate_artifact(target, CONFIG_PATH, "smoke")


def test_production_profile_is_guarded_before_any_expensive_run(tmp_path: Path) -> None:
    output = tmp_path / "must-not-run-production"
    with pytest.raises(runner.ConfigError, match="expensive production profile is guarded"):
        runner.run_experiment(CONFIG_PATH, "production", output)
    assert not output.exists()


def test_production_confirmation_also_requires_immutable_lock(tmp_path: Path) -> None:
    output = tmp_path / "must-not-run-without-lock"
    with pytest.raises(runner.ConfigError, match="immutable --production-prereg lock"):
        runner.run_experiment(
            CONFIG_PATH,
            "production",
            output,
            production_confirmation="N-001-PRODUCTION",
        )
    assert not output.exists()


def test_production_lock_hash_scope_is_the_canonical_payload_digest(tmp_path: Path) -> None:
    """The production lock is identified by its canonical payload digest.

    Regression test for a real blocker found on 2026-09-26: the artifact
    validator compared the recorded lock hash against the exact FILE BYTE hash,
    while validate_production_prereg() records the CANONICAL PAYLOAD hash. The
    two can never be equal, so every production run failed closed after doing
    all the measurement work. The canonical scope must be used, and a re-verified
    canonical digest must still reject a tampered lock.
    """
    lock = tmp_path / "prereg.json"
    payload = {
        "audit_finding_id": "N-001",
        "source_repair_config_sha256": runner.sha256_file(CONFIG_PATH),
        "profile_name": "production",
        "production_profile_sha256": "0" * 64,
    }
    config = runner.load_strict_json(CONFIG_PATH)
    profile = runner.validate_config(config, "production")
    payload["production_profile_sha256"] = runner.sha256_bytes(
        json.dumps(
            profile, allow_nan=False, ensure_ascii=False,
            separators=(",", ":"), sort_keys=True,
        ).encode("utf-8")
    )
    locked = freeze_config(
        experiment_id="TEST-N001-LOCK-SCOPE",
        hypothesis_id="TEST",
        question_id="Q-P007",
        seed=1,
        params=payload,
        out_path=lock,
    )
    canonical = str(locked["config_sha256"])
    byte_hash = runner.sha256_file(lock)
    assert canonical != byte_hash, "the two scopes must be distinct for this test to bite"

    # The recorded value is the canonical digest, and it re-verifies cleanly.
    assert str(runner.verify_frozen_config(lock)["config_sha256"]) == canonical

    # Tampering with the frozen document is still detected on re-verification.
    tampered = json.loads(lock.read_text(encoding="utf-8"))
    tampered["parameters"]["profile_name"] = "smoke"
    lock.write_text(json.dumps(tampered, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(Exception):
        runner.verify_frozen_config(lock)


def test_invalid_active_tau_l_is_rejected_before_run(tmp_path: Path) -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    config["profiles"]["smoke"]["tau_L"] = 12
    bad_config = tmp_path / "bad_tau_config.json"
    bad_config.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(runner.ConfigError, match="absent"):
        runner.run_experiment(bad_config, "smoke", tmp_path / "must-not-exist")
    assert not (tmp_path / "must-not-exist").exists()
