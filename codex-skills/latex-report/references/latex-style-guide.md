# LaTeX Style Guide

Use this reference for professional report typography and layout.

## Typography

- Use a calm serif/sans pairing where possible.
- Use consistent heading hierarchy; do not fake headings with bold paragraphs.
- Keep line length comfortable with generous margins.
- Use microtypography when supported.
- Use hyperlinks with restrained colors.

## Tables

Use `booktabs`:

```latex
\begin{table}[htbp]
  \centering
  \caption{Evaluation summary}
  \begin{tabular}{lrrr}
    \toprule
    Method & Accuracy & Latency & Notes \\
    \midrule
    Baseline & 0.81 & 120 ms & Stable \\
    Proposed & 0.88 & 95 ms & Best trade-off \\
    \bottomrule
  \end{tabular}
\end{table}
```

Avoid vertical rules unless a form-like table genuinely needs them.

## Figures

- Prefer vector `.pdf` for charts and diagrams.
- Use descriptive captions that state what the reader should notice.
- Reference every figure in prose.
- Keep labels readable after PDF export.

## Callouts

Use callouts for findings, definitions, assumptions, and reproducibility notes. Do not wrap ordinary prose in boxes.

```latex
\begin{findingbox}{Key finding}
The proposed pipeline reduces manual review work by concentrating ambiguity into a small validation queue.
\end{findingbox}
```

## Code

- In the main text, show only the smallest excerpt needed to explain the idea.
- Put longer snippets in appendices.
- Avoid screenshots of code unless visual IDE state matters.

## Common Failure Modes

Fix these before delivery:

- Overfull lines in captions, URLs, and code
- Tables too wide for the page
- Floats drifting far from their explanation
- Missing CJK glyphs
- Dark callouts with low-contrast text
- Decorative diagrams that do not support the argument
- Appendix pages that become uncurated code dumps
