---
name: latex-report
description: Create polished native LaTeX reports and compile them to PDF with Tectonic. Use when Codex needs to produce an elegant technical, research, course, project, experiment, analysis, or thesis-style PDF report with structured chapters, figures, tables, formulas, TikZ/pgfplots diagrams, citations, appendices, or curated code excerpts. Also use when the user mentions LaTeX, .tex, TikZ, Tectonic, beautiful PDF reports, appendix code, or asks for a report PDF whose structure and narrative should be authored rather than merely converted from Markdown.
---

# LaTeX Report

## Purpose

Use this skill to build high-quality report PDFs from native LaTeX, not just to manipulate an existing PDF. The default deliverable is an editable LaTeX project plus a compiled PDF that has been visually checked.

For PDF merging, OCR, extraction, watermarks, rotation, encryption, or form filling, use the `pdf` skill instead. For Word deliverables, use the `documents` skill.

## Decision Tree

- Use **native LaTeX** for substantial technical, research, project, course, analysis, or thesis-style reports; reports needing a custom narrative; TikZ/pgfplots; appendices; formulas; references; or curated code excerpts.
- Use **Pandoc/Eisvogel only as a fast path** when the source is already Markdown, the output is lightweight, and the user does not need complex native LaTeX structure.
- Use **Python/JS chart generation plus LaTeX inclusion** for evidence charts, data plots, screenshots, image analysis, or generated figures.
- Use **TikZ/pgfplots** for architecture diagrams, workflows, conceptual models, timelines, and small data visuals that benefit from native typesetting.

## Default Workflow

1. Determine the report archetype: technical report, research report, course report, project documentation, experiment report, business/analysis report, or thesis-style report.
2. Choose an appropriate length, chapter structure, and evidence density from the task scope. Do not force a fixed page count unless the user explicitly asks for one.
3. Draft a narrative spine before writing LaTeX: thesis, audience, chapter claims, evidence objects, and appendix plan.
4. Copy `assets/elegant-report-template/` into the work area and adapt it. Keep outputs under an `outputs/<task-slug>/latex-report/` folder unless the user provides another location.
5. Put prose in `chapters/*.tex`, code excerpts in `appendices/*.tex`, figures in `figures/`, and bibliography entries in `refs.bib`.
6. Compile with `scripts/compile_report.ps1`, which uses `D:\tools\tectonic\tectonic.exe` by default.
7. Run page-count and render QA using `scripts/check_pdf_pages.py` and `scripts/render_pdf_preview.ps1`.
8. Inspect rendered preview images for broken layout: overfull boxes, missing glyphs, clipped figures, orphan headings, unreadable tables, empty pages, bad floats, and appendix bloat.
9. Iterate until the compiled PDF is clean, then return links to the final PDF and the LaTeX project root.

## Report Architecture

Before authoring, read `references/report-architecture.md` for chapter planning. Use it to decide what belongs in front matter, main chapters, evidence sections, and appendices.

Common structure:

- Title page
- Abstract or executive summary
- Table of contents
- Introduction and problem framing
- Background or related work
- Methodology / system design / data and assumptions
- Evidence chapters with figures, tables, diagrams, and analysis
- Results, discussion, limitations, and future work
- Conclusion
- Appendices for code excerpts, extended derivations, extra tables, prompts/configs, and reproducibility notes
- Bibliography

## Visual And Typographic Standards

Read `references/latex-style-guide.md` before substantial reports. Keep the result elegant and readable:

- Use a restrained palette, strong hierarchy, good margins, consistent captions, and professional tables.
- Use `booktabs` for tables; avoid dense vertical lines.
- Use `tcolorbox` sparingly for definitions, key findings, algorithms, or reproducibility notes.
- Prefer vector figures (`.pdf`) for plots and diagrams when practical.
- Keep code excerpts short in the main text. Put longer or supporting code in appendices.

## Figures, TikZ, And Evidence

Read `references/tikz-figure-patterns.md` when drawing diagrams. Every figure should support a claim in the surrounding text. Avoid decorative figures that do not clarify evidence, architecture, process, comparison, or mechanism.

Use:

- TikZ for flows, architecture, pipelines, taxonomies, timelines, and conceptual diagrams.
- pgfplots for small, polished native charts.
- Python/Matplotlib or another appropriate tool for data-heavy plots; export to PDF/PNG and include through LaTeX.

## Code Appendix Policy

Read `references/appendix-code-policy.md` when the source project has meaningful code. Do not paste entire source files into the report. Summarize implementation in prose, show only key excerpts, and put supporting snippets in appendices with enough context to be useful.

Use `scripts/extract_code_snippets.py` to build appendix-ready snippets from line ranges when helpful.

## Build Commands

Compile:

```powershell
& "C:\Users\梁子安\.codex\skills\latex-report\scripts\compile_report.ps1" `
  -ProjectDir "path\to\report" `
  -Main "main.tex" `
  -OutDir "build"
```

Check pages:

```powershell
python "C:\Users\梁子安\.codex\skills\latex-report\scripts\check_pdf_pages.py" `
  "path\to\report\build\main.pdf"
```

Render preview PNGs:

```powershell
& "C:\Users\梁子安\.codex\skills\latex-report\scripts\render_pdf_preview.ps1" `
  -PdfPath "path\to\report\build\main.pdf" `
  -OutputDir "path\to\report\preview"
```

## QA Gate

Do not deliver a report PDF just because LaTeX compiled. Before final response:

- Confirm the PDF exists and is non-empty.
- Confirm the page count matches the task scope.
- Render representative pages, and for important/final reports render all pages or a contact-sheet-style set.
- Inspect cover, table of contents, first page of each chapter, figure-heavy pages, table-heavy pages, and appendix pages.
- Fix missing references, missing citations, broken figures, bad line breaks, unreadable tables, and obvious layout defects.
- Keep build logs available while debugging, but do not return logs or preview images unless the user asks.

## Tool Paths

Default Windows tools:

- Tectonic: `D:\tools\tectonic\tectonic.exe`
- qpdf: `D:\tools\qpdf\bin\qpdf.exe`
- pdftoppm: `D:\tools\poppler\Library\bin\pdftoppm.exe`
- pdftotext: `D:\tools\poppler\Library\bin\pdftotext.exe`

If a tool is missing, first check whether an equivalent is available in the workspace dependencies before asking the user.
