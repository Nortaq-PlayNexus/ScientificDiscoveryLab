# Cross-project anomaly scan task

You are one of several independent reviewers performing a second-pass audit of `C:\Users\natha\ScientificDiscoveryLab`. Do not edit historical experiment files, registries, reports, or result files. Write only below `AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_<name>/`.

Goal: find errors, contradictions, hidden assumptions, data leakage, hardcoded outputs, provenance problems, and scientifically meaningful patterns that a project-by-project audit could miss. Read the existing independent audit first, but do not assume it is complete.

Review the whole tree, including:
- all `03_INVESTIGATIONS`, `04_SHARED_ENGINE`, `src`, `tests`, root scripts, registries, reports, configs, raw/result files;
- JSON/Markdown/code cross-consistency;
- chronology, duplicate hashes, ID collisions, hardcoded result writers, synthetic data;
- statistical formulas, units, uncertainty, p-value construction, multiple testing, sample-size mismatches;
- cross-experiment reused data, labels, RNG streams, or analysis functions;
- claims that are inconsistent between registry, preregistration, code, result, and report.

For every candidate finding, provide:
1. exact file/line or JSON path;
2. observed value or quote;
3. why it is anomalous;
4. alternative benign explanation;
5. severity and confidence;
6. a minimal reproduction command;
7. whether it changes any prior claim classification.

Do not report generic best practices as discoveries. Focus on concrete, evidence-backed anomalies. Save a concise `REPORT.md`, machine-readable `findings.json`, and commands/logs. Return a short summary with the most important unexpected findings.
