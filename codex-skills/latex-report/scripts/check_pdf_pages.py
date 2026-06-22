#!/usr/bin/env python
import argparse
import subprocess
import sys
from pathlib import Path


def count_with_pypdf(pdf_path: Path) -> int | None:
    try:
        from pypdf import PdfReader
    except Exception:
        return None

    reader = PdfReader(str(pdf_path))
    return len(reader.pages)


def count_with_qpdf(pdf_path: Path, qpdf_path: Path) -> int | None:
    if not qpdf_path.exists():
        return None
    result = subprocess.run(
        [str(qpdf_path), "--show-npages", str(pdf_path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        return None
    try:
        return int(result.stdout.strip())
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Check PDF page count.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--min-pages", type=int, default=None)
    parser.add_argument("--max-pages", type=int, default=None)
    parser.add_argument("--qpdf", type=Path, default=Path(r"D:\tools\qpdf\bin\qpdf.exe"))
    args = parser.parse_args()

    pdf_path = args.pdf.resolve()
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        return 2

    pages = count_with_pypdf(pdf_path)
    if pages is None:
        pages = count_with_qpdf(pdf_path, args.qpdf)
    if pages is None:
        print("Could not determine page count with pypdf or qpdf.", file=sys.stderr)
        return 3

    print(f"{pdf_path}: {pages} pages")

    if args.min_pages is not None and pages < args.min_pages:
        print(f"Page count below minimum: {pages} < {args.min_pages}", file=sys.stderr)
        return 4
    if args.max_pages is not None and pages > args.max_pages:
        print(f"Page count above maximum: {pages} > {args.max_pages}", file=sys.stderr)
        return 5

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
