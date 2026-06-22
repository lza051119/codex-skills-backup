# PDF Chinese Image Translator Skill

Codex skill for translating English PDF files into Simplified Chinese visual PDFs through a whole-page raster workflow:

1. Render PDF pages to full-page images.
2. Use the built-in `imagegen` skill to regenerate each whole page as a clean Chinese page image.
3. Normalize generated page dimensions back to the source render dimensions.
4. Bind normalized page images into a PDF.
5. Audit page count and image dimensions.

## Install

Copy this directory into your Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R pdf-zh-image-translator "${CODEX_HOME:-$HOME/.codex}/skills/"
```

## Dependencies

The helper scripts use Python 3 and Pillow. `prepare_pdf_pages.py` prefers PyMuPDF (`fitz`) for rendering and text extraction. On macOS it can fall back to the bundled Swift/PDFKit renderer plus `pypdf` text extraction.

Typical setup:

```bash
python3 -m pip install pillow pymupdf pypdf
```

## Safety Boundary

This package intentionally does not include sample PDFs, generated images, API keys, tokens, local user paths, or external AI bridge configuration.

The skill is designed to avoid external OCR/translation tools such as Gemini, Ollama, DeepLX, Google Translate, and pdf2zh unless the user explicitly requests a comparison outside this workflow. OCR/translation support should come from Codex/ChatGPT visual reading or authorized Codex child agents; final translated page images should come from whole-page `imagegen`.

## License

MIT. See `LICENSE`.
