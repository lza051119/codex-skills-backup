# Appendix Code Policy

Use this reference when the source project has code.

## Main Text

In the main chapters, code should be brief and explanatory:

- Show only the function, class, query, configuration, or algorithm fragment that proves the point.
- Introduce the excerpt before showing it.
- Explain why the excerpt matters after showing it.
- Prefer pseudocode when implementation details are distracting.

## Appendix

Put longer code in appendices when it supports reproducibility or review:

- Key modules
- Important configuration
- Evaluation scripts
- Data processing logic
- Prompt templates
- API schemas

Do not paste the whole repository. Curate.

## Excerpt Format

Use a short title and source path:

```latex
\begin{codebox}{Core retrieval loop}{python}
for query in queries:
    candidates = retriever.search(query)
    reranked = ranker.score(query, candidates)
    yield reranked[:k]
\end{codebox}
```

For appendix snippets generated from files, use `scripts/extract_code_snippets.py`.
