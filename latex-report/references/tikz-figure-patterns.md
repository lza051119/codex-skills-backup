# TikZ Figure Patterns

Use TikZ for explanatory diagrams that benefit from crisp PDF-native rendering.

## Architecture Pipeline

```latex
\begin{figure}[htbp]
\centering
\begin{tikzpicture}[
  node distance=1.8cm,
  stage/.style={draw=Accent, rounded corners=2pt, thick, align=center,
    minimum width=2.8cm, minimum height=1.0cm, fill=Accent!6},
  arrow/.style={-{Latex[length=2.4mm]}, thick, draw=Ink!70}
]
  \node[stage] (input) {Input\\sources};
  \node[stage, right=of input] (process) {Processing\\pipeline};
  \node[stage, right=of process] (evidence) {Evidence\\objects};
  \node[stage, right=of evidence] (report) {LaTeX\\report};
  \draw[arrow] (input) -- (process);
  \draw[arrow] (process) -- (evidence);
  \draw[arrow] (evidence) -- (report);
\end{tikzpicture}
\caption{Report-generation pipeline from source material to evidence-backed PDF.}
\label{fig:report-pipeline}
\end{figure}
```

## Decision Tree

Use decision trees for routing logic, model choices, and QA gates. Keep branch labels short.

## Timeline

Use timelines for implementation phases, experiments, or project chronology. Place key milestones above and evidence artifacts below when useful.

## Rules

- Every node should encode a real entity, state, step, or decision.
- Use arrows only when direction matters.
- Keep labels short and explain nuance in the caption/prose.
- Use the same color semantics throughout the report.
- Prefer 1-2 strong diagrams per chapter over many small decorative ones.
