# Report Architecture

Use this reference when planning a substantial native LaTeX report.

## Planning Checklist

Define these before writing chapters:

- Audience: instructor, technical reviewer, client, internal team, or general reader.
- Thesis: the one-sentence point the report should prove.
- Evidence inventory: data, screenshots, logs, diagrams, source code, experiments, literature, user examples, or benchmarks.
- Chapter claims: each chapter should answer a specific question or prove a specific claim.
- Appendix boundary: what supports reproducibility but would interrupt the main read.

## Archetypes

### Technical Project Report

Use for software projects, systems, engineering builds, data pipelines, ML prototypes, or product demos.

Recommended arc:

1. Abstract / executive summary
2. Problem and objectives
3. Requirements and constraints
4. Architecture and design decisions
5. Implementation highlights
6. Evaluation / experiments / evidence
7. Limitations and risks
8. Conclusion and future work
9. Appendices: code excerpts, config, detailed logs, API references

### Research / Experiment Report

Use for empirical analysis, experiments, model comparisons, literature-backed reports, and academic-style work.

Recommended arc:

1. Abstract
2. Introduction and research question
3. Background / related work
4. Methodology
5. Dataset / materials / assumptions
6. Results
7. Discussion
8. Threats to validity / limitations
9. Conclusion
10. Appendices: extended tables, code, prompts, derivations

### Course / Thesis-Style Report

Use when the user wants a formal course design, graduation-style project, or long academic submission.

Recommended arc:

1. Title page
2. Abstract
3. Table of contents, list of figures/tables when useful
4. Introduction
5. Background and theory
6. System / method design
7. Implementation
8. Testing and evaluation
9. Summary and future work
10. Appendices and bibliography

## Length Calibration

Let scope determine length:

- Small focused report: compact chapters, few figures, short appendix.
- Medium report: full narrative, several figures/tables, moderate appendix.
- Large report: deeper background, multiple evidence chapters, reproducibility appendix, expanded discussion.

Do not pad. Add pages only when they add explanation, evidence, reproducibility, or visual clarity.

## Evidence Rhythm

Avoid long uninterrupted prose. For each major chapter, include at least one of:

- A figure or diagram
- A table
- A formula or formal definition
- A code excerpt
- A callout with key findings
- A reproducibility note

Use appendices to keep the main story readable.
