#!/usr/bin/env python
import argparse
from pathlib import Path


LANG_BY_SUFFIX = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".jsx": "JavaScript",
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C",
    ".rs": "Rust",
    ".go": "Go",
    ".sql": "SQL",
    ".sh": "bash",
    ".ps1": "PowerShell",
}


def latex_escape_title(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "#": r"\#",
        "$": r"\$",
        "%": r"\%",
        "&": r"\&",
        "_": r"\_",
        "^": r"\^{}",
        "~": r"\~{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def parse_range(spec: str) -> tuple[Path, int, int]:
    if ":" not in spec:
        raise ValueError(f"Expected path:start-end, got {spec}")
    path_text, range_text = spec.rsplit(":", 1)
    if "-" not in range_text:
        raise ValueError(f"Expected start-end line range, got {range_text}")
    start_text, end_text = range_text.split("-", 1)
    return Path(path_text), int(start_text), int(end_text)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract line ranges into appendix-ready LaTeX codebox blocks."
    )
    parser.add_argument("ranges", nargs="+", help="Use path:start-end, e.g. src/app.py:10-40")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    blocks: list[str] = []
    for range_spec in args.ranges:
        path, start, end = parse_range(range_spec)
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        excerpt = "\n".join(lines[start - 1 : end])
        lang = LANG_BY_SUFFIX.get(path.suffix.lower(), "text")
        title = latex_escape_title(f"{path} lines {start}-{end}")
        blocks.append(f"\\begin{{codebox}}{{{title}}}{{{lang}}}\n{excerpt}\n\\end{{codebox}}\n")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(blocks), encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
