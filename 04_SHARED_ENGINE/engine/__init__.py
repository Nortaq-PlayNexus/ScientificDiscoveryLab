"""engine — shared scientific-computing toolkit for the AI Scientific Discovery Lab.

Import with the 04_SHARED_ENGINE directory on sys.path:

    import engine
    from engine.statistics.testers import bh_fdr
    from engine.utilities.core import rng

Modules:
    utilities.core        deterministic RNG, sha256 hashing, experiment.json builder
    statistics.testers    BH-FDR, Welch t, Cohen's d, bootstrap CI, binomial bands
    hypothesis_testing.prereg   pre-registration helper (freeze config + log changes)
    simulation.controls  control generators: null/matched/resolution/seed ladders
    reproducibility.experiments  experiment folder scaffolding + append-only registry
    datasets.manifest    dataset hashing manifests (provenance)
    visualization.plots  matplotlib helpers with deterministic styling
"""