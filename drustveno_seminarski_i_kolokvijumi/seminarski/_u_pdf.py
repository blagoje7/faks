# -*- coding: utf-8 -*-
"""
HTML -> PDF preko playwright-a (sinhroni API).

nbconvert --to webpdf puca na Windowsu zbog asyncio event loop-a, pa se ovde
koristi sinhroni playwright koji taj problem nema.

Pokretanje:
    python _u_pdf.py seminarski.html seminarski.pdf
"""
import os
import sys
from playwright.sync_api import sync_playwright

CSS_ZA_STAMPU = """
@page { size: A4; margin: 16mm 14mm; }
body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
/* ne prelamaj celije, tabele i slike preko strane */
.jp-Cell, .jp-OutputArea-child, table, img, pre { break-inside: avoid; page-break-inside: avoid; }
h1, h2, h3 { break-after: avoid; page-break-after: avoid; }
h1 { break-before: page; page-break-before: page; }
h1:first-of-type { break-before: auto; page-break-before: auto; }
/* sakrij prompt brojeve, nepotrebni su u radu */
.jp-InputPrompt, .jp-OutputPrompt { display: none !important; }
/* duge linije koda se prelamaju umesto da se odseku na ivici strane */
pre, code, .jp-RenderedText, .CodeMirror-line, .highlight pre {
    white-space: pre-wrap !important;
    word-break: break-word !important;
    overflow-wrap: anywhere !important;
}
.jp-OutputArea-output, .jp-InputArea-editor { overflow: visible !important; }
"""


def u_pdf(ulaz, izlaz):
    put = "file:///" + os.path.abspath(ulaz).replace("\\", "/")
    with sync_playwright() as p:
        b = p.chromium.launch()
        s = b.new_page()
        s.goto(put, wait_until="networkidle", timeout=120_000)
        s.add_style_tag(content=CSS_ZA_STAMPU)
        s.emulate_media(media="print")
        s.pdf(path=izlaz, format="A4", print_background=True,
              margin={"top": "16mm", "bottom": "16mm", "left": "14mm", "right": "14mm"})
        b.close()
    print(f"Upisano {izlaz}  ({os.path.getsize(izlaz)/1024:.0f} KB)")


if __name__ == "__main__":
    ulaz = sys.argv[1] if len(sys.argv) > 1 else "seminarski.html"
    izlaz = sys.argv[2] if len(sys.argv) > 2 else "seminarski.pdf"
    u_pdf(ulaz, izlaz)
