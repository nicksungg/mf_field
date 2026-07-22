"""Render a report Markdown file to PDF via styled HTML + headless Chrome.

Matches the toolchain that produced the existing deliverables in this repo
(their PDF metadata reports Skia/PDF via HeadlessChrome).

Usage:  python md_to_pdf.py ../MF_FNO_CNN_Hybrid_Report.md
Writes: ../MF_FNO_CNN_Hybrid_Report.pdf  (and a .html alongside, for inspection)
"""

import base64
import mimetypes
import pathlib
import re
import subprocess
import sys

import markdown

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 16mm 14mm 16mm 14mm; }
* { box-sizing: border-box; }
body {
  font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 10.4pt; line-height: 1.62; color: #1c252e; margin: 0;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
h1 { font-size: 20pt; line-height: 1.25; margin: 0 0 6px; color: #10202f; letter-spacing: -0.2px; }
h2 { font-size: 14pt; margin: 26px 0 8px; padding-bottom: 5px;
     border-bottom: 2px solid #dde4ec; color: #10202f; page-break-after: avoid; }
h3 { font-size: 11.6pt; margin: 18px 0 6px; color: #24384a; page-break-after: avoid; }
h4 { font-size: 10.6pt; margin: 14px 0 4px; color: #38495a; page-break-after: avoid; }
h1 + h2 { margin-top: 14px; }
p { margin: 0 0 9px; }
ul, ol { margin: 0 0 10px; padding-left: 21px; }
li { margin-bottom: 3px; }
strong { color: #0d1a26; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 8.9pt;
       background: #eef2f7; padding: 1px 4px; border-radius: 3px; color: #1d3a52; }
pre { background: #f6f8fb; border: 1px solid #dde4ec; border-left: 3px solid #7fa8cc;
      border-radius: 4px; padding: 9px 12px; overflow-x: auto; page-break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 8.6pt; line-height: 1.5; }
table { border-collapse: collapse; width: 100%; margin: 12px 0 14px;
        font-size: 9.1pt; page-break-inside: avoid; }
th { background: #eaf0f7; text-align: left; font-weight: 600; color: #16283a; }
th, td { border: 1px solid #d3dce6; padding: 5px 8px; vertical-align: top; }
tr:nth-child(even) td { background: #fafbfd; }
blockquote { margin: 10px 0; padding: 7px 14px; border-left: 3px solid #b9cbdd;
             background: #f5f8fb; color: #35485a; }
img { max-width: 100%; height: auto; display: block; margin: 14px auto;
      border: 1px solid #e2e8f0; border-radius: 4px; page-break-inside: avoid; }
hr { border: none; border-top: 1px solid #dde4ec; margin: 22px 0; }
a { color: #1f5f96; text-decoration: none; }
em { color: #40525f; }
h2, h3, h4 { break-after: avoid-page; }
"""


def inline_images(html: str, base: pathlib.Path) -> str:
    """Embed local images as data URIs so Chrome needs no file access."""
    def sub(m):
        src = m.group(1)
        if src.startswith(("http://", "https://", "data:")):
            return m.group(0)
        p = (base / src).resolve()
        if not p.exists():
            print(f"  ! missing image: {src}", file=sys.stderr)
            return m.group(0)
        mime = mimetypes.guess_type(str(p))[0] or "image/png"
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f'src="data:{mime};base64,{b64}"'
    return re.sub(r'src="([^"]+)"', sub, html)


def main(md_path: str):
    src = pathlib.Path(md_path).resolve()
    body = markdown.markdown(
        src.read_text(),
        extensions=["tables", "fenced_code", "codehilite", "attr_list", "toc"],
        extension_configs={"codehilite": {"noclasses": True, "pygments_style": "friendly"}},
    )
    body = inline_images(body, src.parent)
    html = f"<!doctype html><html><head><meta charset='utf-8'><title>{src.stem}</title><style>{CSS}</style></head><body>{body}</body></html>"

    html_path = src.with_suffix(".html")
    pdf_path = src.with_suffix(".pdf")
    html_path.write_text(html)

    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf_path}", html_path.as_uri()],
        check=True, capture_output=True,
    )
    print(f"wrote {pdf_path} ({pdf_path.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../MF_FNO_CNN_Hybrid_Report.md")
