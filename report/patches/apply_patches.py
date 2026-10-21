"""Apply the fragments in patches.pdf to the authoritative FINAL.pdf.

Usage: python3 apply_patches.py <input FINAL.pdf> <patches.pdf> <output.pdf>

Every page that is not listed below is copied unchanged. On a patched page the old
region is redacted (its text, and its vector graphics where a figure is replaced), the
new fragment from patches.pdf is placed over it aligned to the original baselines, and
the internal links that pointed into the region are recreated. Requires PyMuPDF >= 1.24.
"""
import sys

import pymupdf as fitz

src_path, patch_path, out_path = sys.argv[1:4]
outline_path = sys.argv[4] if len(sys.argv) > 4 else None
doc = fitz.open(src_path)
ref = fitz.open(src_path)          # untouched copy, used when content is moved
P = fitz.open(patch_path)

PITCH = 17.93                      # body line pitch of the report (pt)


def lines(page, clip=None):
    out = []
    for b in page.get_text("dict", clip=clip)["blocks"]:
        for l in b.get("lines", []):
            out.append((fitz.Rect(l["bbox"]), "".join(s["text"] for s in l["spans"])))
    return sorted(out, key=lambda t: (round(t[0].y0, 1), t[0].x0))


def content_box(page):
    r = fitz.Rect()
    for box, _ in lines(page):
        r.include_rect(box)
    for d in page.get_drawings():
        r.include_rect(d["rect"])
    return r + (-2, -2, 2, 2)


def redact(page, rect, graphics=False):
    for link in page.get_links():
        if fitz.Rect(link["from"]).intersects(rect):
            page.delete_link(link)
    page.add_redact_annot(rect, fill=False)
    page.apply_redactions(
        images=fitz.PDF_REDACT_IMAGE_NONE,
        graphics=(fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED if graphics
                  else fitz.PDF_REDACT_LINE_ART_NONE),
        text=fitz.PDF_REDACT_TEXT_REMOVE)


def place(page, patch_no, dx, dy, clip=None):
    clip = clip or content_box(P[patch_no])
    page.show_pdf_page(clip + (dx, dy, dx, dy), P, patch_no, clip=clip)


def first_line(page, clip=None):
    return lines(page, clip)[0][0]


def link(page, needle, target, every=True):
    hits = page.search_for(needle)
    for r in (hits if every else hits[:1]):
        page.insert_link({"kind": fitz.LINK_GOTO, "from": r, "page": target,
                          "to": fitz.Point(0, 0), "zoom": 0})


# horizontal offset between this build and the original: both lines begin "Figure 4.2"
DX = first_line(ref[31], fitz.Rect(95, 236, 530, 256)).x0 - first_line(P[1]).x0

# P1 -- Figure 4.1 (printed p. 18, PDF page 29): replace the drawing, keep the caption
pg = doc[28]
redact(pg, fitz.Rect(100, 76, 525, 333), graphics=True)
place(pg, 0, DX, 0)

# P2 -- Section 4.3 text (p. 21, PDF 32): everything from the paragraph down
pg = doc[31]
old = first_line(ref[31], fitz.Rect(95, 236, 530, 256))
redact(pg, fitz.Rect(95, old.y0 - 3, 530, 776))
place(pg, 1, DX, old.y0 - first_line(P[1]).y0)
link(pg, "Figure 4.2", 32, every=False)
link(pg, "Section 4.2.4", 29)

# P3 -- body of p. 22 (PDF 33): use case diagram, caption and Section 4.4
pg = doc[32]
redact(pg, fitz.Rect(95, 76, 530, 776), graphics=True)
place(pg, 2, DX, 0)
link(pg, "Figure 4.3", 33)
link(pg, "Figure 4.4", 33)
link(pg, "Figure 4.5", 34)

# P4 -- Section 4.7.1, second paragraph (p. 29, PDF 40): six lines, same slot
pg = doc[39]
old = fitz.Rect(95, 303, 530, 408)
y0 = first_line(ref[39], old).y0
redact(pg, old)
place(pg, 3, DX, y0 - first_line(P[3]).y0)

# P5 -- Figure 4.10 caption (p. 33, PDF 44)
pg = doc[43]
old = fitz.Rect(95, 697, 530, 740)
y0 = first_line(ref[43], old).y0
redact(pg, old)
place(pg, 4, DX, y0 - first_line(P[4]).y0)
link(pg, "Section 4.2.5", 30)

# P6 -- List of Figures entry 4.10 (PDF page 10)
pg = doc[9]
old = fitz.Rect(95, 393, 530, 463)
y0 = first_line(ref[9], old).y0
redact(pg, old)
place(pg, 5, DX, y0 - first_line(P[5]).y0)
for box, _ in lines(pg, old + (0, 0, 0, 0)):
    pg.insert_link({"kind": fitz.LINK_GOTO, "from": fitz.Rect(117, box.y0, 525, box.y1),
                    "page": 43, "to": fitz.Point(0, 0), "zoom": 0})

# P7 -- Section 7.2.6, first paragraph (p. 58, PDF 69): eleven lines, same slot
pg = doc[68]
old = fitz.Rect(95, 370, 530, 565)
y0 = first_line(ref[68], old).y0
redact(pg, old)
place(pg, 6, DX, y0 - first_line(P[6]).y0)
link(pg, "Table 7.6", 70)

# P8 -- Section 7.2.7 opening (p. 59, PDF 70): two lines become three, so the rest of
# the page moves down by one line (it has one line of space left at the bottom)
pg = doc[69]
n_old = len({round(b.y0) for b, _ in lines(ref[69], fitz.Rect(95, 110, 530, 148))})
n_new = len({round(b.y0) for b, _ in lines(P[7])})
shift = (n_new - n_old) * PITCH
y0 = first_line(ref[69], fitz.Rect(95, 110, 530, 130)).y0
moved = [l for l in ref[69].get_links() if fitz.Rect(l["from"]).y0 > 150]
redact(pg, fitz.Rect(90, 110, 535, 757), graphics=True)
place(pg, 7, DX, y0 - first_line(P[7]).y0)
# source for the moved block: a copy of the page with everything outside the block
# removed, so no clipped-away text (old opening, header, footer) survives invisibly
tmp = fitz.open(src_path)
tp = tmp[69]
for r in (fitz.Rect(0, 0, 595.3, 150), fitz.Rect(0, 757, 595.3, 841.9)):
    tp.add_redact_annot(r, fill=False)
tp.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,
                    graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED,
                    text=fitz.PDF_REDACT_TEXT_REMOVE)
pg.show_pdf_page(fitz.Rect(0, shift, 595.3, 841.9 + shift), tmp, 69)
for l in moved:
    l = dict(l)
    l["from"] = fitz.Rect(l["from"]) + (0, shift, 0, shift)
    pg.insert_link(l)
link(pg, "Table 7.6", 70, every=False)
link(pg, "Section 7.2.6", 68)

# P9 -- Declaration (front matter, PDF page 2): the whole page is re-typeset; the page
# object is kept (redact + overlay rather than a page swap) so the outline stays valid
pg = doc[1]
redact(pg, pg.rect, graphics=True)
pg.show_pdf_page(pg.rect, P, 8)

# P10 -- cover page date (PDF page 1): only the date line changes; the new line is
# centred on the old one's axis and set on the same baseline
pg = doc[0]
old = ref[0].search_for("November 2026")[0]
new = first_line(P[9])
redact(pg, old + (-1, -1, 1, 1))
place(pg, 9, (old.x0 + old.x1) / 2 - (new.x0 + new.x1) / 2, old.y0 - new.y0)

# P11 -- footer: "College of Engineering" becomes "College of Engineering Trivandrum" on
# every page that carries the footer (PDF pages 12-78). Nothing is removed or rewritten:
# the word "Trivandrum" is added after the existing text (the fragment reserves the width
# of "College of Engineering" invisibly), on the same baseline. Redacting the old footer
# would re-encode the whole page stream and nudge some glyphs by a fraction of a point.
def baseline(page):
    for b in page.get_text("rawdict")["blocks"]:
        for l in b.get("lines", []):
            return l["spans"][0]["origin"][1]

frag_base = baseline(P[10])
footers = 0
for i, pg in enumerate(doc):
    hits = [box for box, text in lines(ref[i]) if box.y0 > 775 and text == "College of Engineering"]
    for old in hits:
        old_base = [s["origin"][1] for b in ref[i].get_text("rawdict", clip=old + (-1, -1, 1, 1))["blocks"]
                    for l in b.get("lines", []) for s in l["spans"]][0]
        place(pg, 10, DX, old_base - frag_base)
        footers += 1
assert footers == 67, footers
print(f"footers extended: {footers}")

# P12 -- Acknowledgment (front matter, PDF page 4): the whole page is re-typeset; the page
# object is kept (redact + overlay) so the outline stays valid
pg = doc[3]
redact(pg, pg.rect, graphics=True)
pg.show_pdf_page(pg.rect, P, 11)

# Outline: the bookmarks of the input may point at named destinations that no longer
# resolve after earlier page swaps, so rebuild them with explicit page numbers taken from
# a PDF whose outline is intact (the originally uploaded report has the same pagination).
if outline_path:
    good = fitz.open(outline_path).get_toc(simple=True)
    assert all(1 <= t[2] <= doc.page_count for t in good), "outline source is broken too"
    doc.set_toc(good)

doc.save(out_path, garbage=4, deflate=True)
print(f"wrote {out_path}: {doc.page_count} pages; DX={DX:.2f} pt; p.59 shift={shift:.2f} pt")
