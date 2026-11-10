"""Build the slide deck from the template look of "Aarhus Agentic Meetup.pptx".

Run from the repository root (after slides/figures.py):

    uv run python slides/build_slides.py

The template file is used as the base so its theme, master and 16:9 format are
kept; its slides are removed and new slides are built on the Blank layout with
the template's components (Lao UI titles, grey cards, numbered steps, token bars).
"""

import json
import re
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

sys.path.insert(0, str(Path(__file__).parent))
import style as S  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "sources" / "Aarhus Agentic Meetup.pptx"
FIG = ROOT / "slides" / "figures"
OUT = ROOT / "slides" / "session1_linear_regressions.pptx"
N = json.loads((FIG / "numbers.json").read_text())

FONT = "Lao UI"
MONO = "Consolas"
SLIDE_W, SLIDE_H = 13.333, 7.5
LEFT = 0.46
RIGHT_EDGE = SLIDE_W - 0.46
TOP = 1.75

EVENT = "Introduction to Bayesian Statistics  ·  Center for Humanities Computing"
TITLE = "Session 1 - Linear regressions"
PRESENTER = "Nicolas Legrand"
AFFILIATION = "Aarhus NLP – Center for Humanities Computing – Aarhus University"


def rgb(hex_):
    return RGBColor.from_string(hex_.lstrip("#"))


COLORS = {
    "grey": S.GREY,
    "dark": S.GREY_DARK,
    "mid": S.GREY_MID,
    "blue": S.BLUE_DARK,
    "rose": S.ROSE_DARK,
    "sage": S.SAGE_DARK,
    "white": S.WHITE,
}


# ----------------------------------------------------------------------------
# Deck and low-level helpers
# ----------------------------------------------------------------------------
class Deck:
    def __init__(self):
        self.prs = Presentation(TEMPLATE)
        ids = self.prs.slides._sldIdLst
        for sld_id in list(ids):
            self.prs.part.drop_rel(sld_id.rId)
            ids.remove(sld_id)
        self.blank = next(lo for lo in self.prs.slide_layouts if lo.name == "Blank")
        self.count = 0

    def slide(self, title=None, subtitle=None, notes=None, tag=None, number=True):
        s = self.prs.slides.add_slide(self.blank)
        self.count += 1
        if title:
            text(
                s,
                0.36,
                0.2,
                10.8 if tag else 12.6,
                0.9,
                title,
                size=44,
                bold=True,
                anchor=MSO_ANCHOR.TOP,
                line=1.0,
                spacing=0,
            )
        if subtitle:
            text(s, LEFT, 1.06, 12.4, 0.5, subtitle, size=20)
        if tag:
            perspective_tag(s, tag)
        if notes:
            s.notes_slide.notes_text_frame.text = notes.strip()
        if number:
            text(
                s,
                12.3,
                7.05,
                0.6,
                0.3,
                str(self.count),
                size=10,
                color=S.GREY_LIGHT,
                align=PP_ALIGN.RIGHT,
            )
        return s

    def save(self):
        self.prs.save(OUT)
        print(f"wrote {OUT.relative_to(ROOT)} ({self.count} slides)")


TOKEN = re.compile(r"(\*\*.+?\*\*|\*[^*\s][^*]*?\*|\{\w+!?:.+?\}|`.+?`|_\{.+?\})")


def add_runs(p, line, size, color, bold, font):
    """Add runs to paragraph `p` from light markup.

    **bold**   *italic*   {blue:coloured}   {rose!:coloured bold}   `code`   b_{1}
    """
    for tok in TOKEN.split(line):
        if not tok:
            continue
        r_ = p.add_run()
        f = r_.font
        f.size = Pt(size)
        f.name = font
        f.bold = bold
        f.color.rgb = rgb(color)
        if tok.startswith("**") and tok.endswith("**"):
            r_.text = tok[2:-2]
            f.bold = True
        elif tok.startswith("{") and tok.endswith("}") and ":" in tok:
            key, body = tok[1:-1].split(":", 1)
            if key.endswith("!"):
                key = key[:-1]
                f.bold = True
            r_.text = body
            f.color.rgb = rgb(COLORS[key])
        elif tok.startswith("`") and tok.endswith("`"):
            r_.text = tok[1:-1]
            f.name = MONO
            f.size = Pt(size * 0.92)
        elif tok.startswith("_{") and tok.endswith("}"):
            r_.text = tok[2:-1]
            r_._r.get_or_add_rPr().set("baseline", "-25000")
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            r_.text = tok[1:-1]
            f.italic = True
        else:
            r_.text = tok


def set_bullet(p, color=S.GREY_MID, indent=0.28):
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(Inches(indent)))
    pPr.set("indent", str(-Inches(indent)))
    clr = etree.SubElement(pPr, qn("a:buClr"))
    etree.SubElement(clr, qn("a:srgbClr")).set("val", color.lstrip("#"))
    etree.SubElement(pPr, qn("a:buFont")).set("typeface", "Arial")
    etree.SubElement(pPr, qn("a:buChar")).set("char", "•")


def text(
    slide,
    x,
    y,
    w,
    h,
    content,
    size=18,
    color=S.GREY,
    bold=False,
    align=PP_ALIGN.LEFT,
    anchor=MSO_ANCHOR.TOP,
    font=FONT,
    bullets=False,
    spacing=6,
    line=1.08,
    margin=0.05,
):
    """Text box. `content` is a string (lines split on \\n) or a list of lines."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    for side in ("left", "right"):
        setattr(tf, f"margin_{side}", Inches(margin))
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    lines = content.split("\n") if isinstance(content, str) else content
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line
        p.space_after = Pt(spacing)
        is_bullet = bullets and ln.strip() and not ln.startswith("!")
        if ln.startswith("!"):
            ln = ln[1:]
        add_runs(p, ln, size, color, bold, font)
        if is_bullet:
            set_bullet(p)
    return tb


def no_shadow(shape):
    shape.shadow.inherit = False


def box(
    slide,
    x,
    y,
    w,
    h,
    fill=S.GREY_CARD,
    shape=MSO_SHAPE.ROUNDED_RECTANGLE,
    radius=0.048,
    line=None,
):
    sh = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = radius
    if fill:
        sh.fill.solid()
        sh.fill.fore_color.rgb = rgb(fill)
    else:
        sh.fill.background()
    if line:
        sh.line.color.rgb = rgb(line)
        sh.line.width = Pt(1.25)
    else:
        sh.line.fill.background()
    no_shadow(sh)
    sh.text_frame.text = ""
    return sh


def card(slide, x, y, w, h, content, size=18, fill=S.GREY_CARD, pad=0.22, **kw):
    box(slide, x, y, w, h, fill=fill)
    return text(
        slide,
        x + pad,
        y + pad * 0.8,
        w - 2 * pad,
        h - 1.6 * pad,
        content,
        size=size,
        **kw,
    )


def step_number(slide, n, x, y, d=0.31, fill=S.GREY, size=12):
    c = box(slide, x, y, d, d, fill=fill, shape=MSO_SHAPE.OVAL)
    tf = c.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    add_runs(p, str(n), size, S.WHITE, True, FONT)
    return c


def mark(slide, kind, x, y, d=0.34, fill=S.GREY_DARK):
    """Circle with a vector cross ('no') or check ('yes'): no font glyph needed."""
    box(slide, x, y, d, d, fill=fill, shape=MSO_SHAPE.OVAL)
    if kind == "no":
        segments = [((0.32, 0.32), (0.68, 0.68)), ((0.32, 0.68), (0.68, 0.32))]
    else:
        segments = [((0.26, 0.52), (0.43, 0.69)), ((0.43, 0.69), (0.74, 0.32))]
    for (ax, ay), (bx, by) in segments:
        ln = slide.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT,
            Inches(x + ax * d),
            Inches(y + ay * d),
            Inches(x + bx * d),
            Inches(y + by * d),
        )
        ln.line.color.rgb = rgb(S.WHITE)
        ln.line.width = Pt(2.5)


def step(slide, n, x, y, title, w=3.0, size=16, fill=S.GREY):
    """Numbered circle + title, as in the template's 'Method' slide."""
    step_number(slide, n, x, y + 0.03, fill=fill)
    text(slide, x + 0.42, y - 0.03, w - 0.42, 0.42, title, size=size, bold=True)


def image(slide, name, x, y, w=None, h=None):
    """Place figure `name` inside the box (x, y, w, h), keeping aspect ratio, centred."""
    from PIL import Image

    path = FIG / f"{name}.png"
    with Image.open(path) as im:
        iw, ih = im.size
    ratio = iw / ih
    if w and h:
        if w / h > ratio:
            nw, nh = h * ratio, h
        else:
            nw, nh = w, w / ratio
        x, y = x + (w - nw) / 2, y + (h - nh) / 2
    elif w:
        nw, nh = w, w / ratio
    else:
        nw, nh = h * ratio, h
    return slide.shapes.add_picture(
        str(path), Inches(x), Inches(y), Inches(nw), Inches(nh)
    )


def code(slide, x, y, w, h, src, size=14, title=None):
    box(slide, x, y, w, h, fill=S.GREY_CARD)
    top = y + 0.15
    if title:
        text(
            slide,
            x + 0.2,
            y + 0.1,
            w - 0.4,
            0.35,
            title,
            size=12,
            bold=True,
            color=S.GREY_MID,
        )
        top += 0.3
    tb = slide.shapes.add_textbox(
        Inches(x + 0.2), Inches(top), Inches(w - 0.4), Inches(h - (top - y) - 0.1)
    )
    tf = tb.text_frame
    tf.word_wrap = False
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = Inches(0.03)
    for i, ln in enumerate(src.strip("\n").split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = 1.0
        r_ = p.add_run()
        r_.text = ln if ln else " "
        r_.font.name = MONO
        r_.font.size = Pt(size)
        is_comment = ln.strip().startswith("#")
        r_.font.color.rgb = rgb(S.GREY_MID if is_comment else S.GREY_DARK)
    return tb


def perspective_tag(slide, tag):
    label = {"freq": "FREQUENTIST", "bayes": "BAYESIAN", "both": "BOTH VIEWS"}[tag]
    pill(slide, 11.25, 0.42, 1.62, 0.38, label, S.GREY_BAR, S.GREY)


def pill(slide, x, y, w, h, label, fill, col, size=12):
    p_ = box(slide, x, y, w, h, fill=fill, radius=0.5)
    tf = p_.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    par = tf.paragraphs[0]
    par.alignment = PP_ALIGN.CENTER
    add_runs(par, label, size, col, True, FONT)
    return p_


def callout(slide, x, y, w, h, content, accent=S.GREY, size=16, fill=S.GREY_CARD):
    """Card with a coloured bar on the left."""
    box(slide, x, y, w, h, fill=fill)
    box(slide, x, y + 0.12, 0.07, h - 0.24, fill=accent, shape=MSO_SHAPE.RECTANGLE)
    return text(
        slide,
        x + 0.25,
        y + 0.1,
        w - 0.4,
        h - 0.2,
        content,
        size=size,
        anchor=MSO_ANCHOR.MIDDLE,
    )


def hline(slide, x, y, w, color=S.BLUE, weight=3):
    ln = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y), Inches(x + w), Inches(y)
    )
    ln.line.color.rgb = rgb(color)
    ln.line.width = Pt(weight)
    return ln


def token_bars(slide, x, y, rows, seed=0, width=4.75, fill=S.GREY_BAR, accents=None):
    """The template's decorative 'token bars'. `accents`: {(row, col): colour}."""
    import random

    rnd = random.Random(seed)
    accents = accents or {}
    for row in range(rows):
        cx = x
        col = 0
        while cx < x + width - 0.5:
            w = min(
                rnd.choice([0.7, 0.83, 0.97, 1.25, 1.53, 1.67, 1.94, 2.08, 2.5]),
                x + width - cx,
            )
            box(
                slide,
                cx,
                y + row * 0.25,
                w,
                0.11,
                fill=accents.get((row, col), fill),
                radius=0.5,
            )
            cx += w + 0.09
            col += 1


def table(
    slide,
    x,
    y,
    col_w,
    rows,
    size=14,
    header_fill=S.GREY_BAR,
    highlight=None,
    row_h=0.42,
    mono_cols=(),
):
    """Simple native table. `highlight`: {col_index: (fill, text colour)}."""
    highlight = highlight or {}
    shape = slide.shapes.add_table(
        len(rows),
        len(col_w),
        Inches(x),
        Inches(y),
        Inches(sum(col_w)),
        Inches(row_h * len(rows)),
    )
    tbl_el = shape._element.graphic.graphicData.tbl
    tbl_el.tblPr.set("firstRow", "0")
    tbl_el.tblPr.set("bandRow", "0")
    style_id = tbl_el.tblPr.find(qn("a:tableStyleId"))
    if style_id is None:
        style_id = etree.SubElement(tbl_el.tblPr, qn("a:tableStyleId"))
    style_id.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"  # No Style, No Grid
    tbl = shape.table
    for j, w in enumerate(col_w):
        tbl.columns[j].width = Inches(w)
    for i, row in enumerate(rows):
        tbl.rows[i].height = Inches(row_h)
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            fill, col = S.WHITE, S.GREY
            bold = i == 0
            if i == 0:
                fill = header_fill
            if j in highlight:
                fill, col = highlight[j]
                if i == 0:
                    bold = True
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(fill)
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            font = MONO if (j in mono_cols and i > 0) else FONT
            add_runs(p, str(val), size, col, bold, font)
    return shape


def hyperlink(slide, x, y, w, h, label, url, size=14, align=PP_ALIGN.LEFT):
    tb = text(slide, x, y, w, h, "", size=size)
    p = tb.text_frame.paragraphs[0]
    p.alignment = align
    r_ = p.add_run()
    r_.text = label
    r_.font.size = Pt(size)
    r_.font.name = FONT
    r_.font.color.rgb = rgb(S.BLUE_DARK)
    r_.hyperlink.address = url
    return tb


def fmt(x, k=2):
    s = f"{x:.{k}f}"
    return s.replace("-", "−")


# ----------------------------------------------------------------------------
# Slide types
# ----------------------------------------------------------------------------
def title_slide(d):
    s = d.slide(
        number=False,
        notes="""
Welcome. Three blocks, each with short slides followed by a notebook; a break; and a
final quiz.
While people settle: ask everyone to open Notebook 1 in Colab (next slides) and run the
first cell, which installs and imports the packages.
""",
    )
    text(
        s, LEFT, 1.2, 7.6, 0.4, EVENT, size=15, bold=True, color=S.ROSE_DARK, spacing=0
    )
    text(
        s,
        LEFT,
        1.6,
        7.2,
        1.7,
        TITLE,
        size=44,
        bold=True,
        anchor=MSO_ANCHOR.TOP,
        line=1.0,
    )
    text(
        s,
        LEFT,
        3.25,
        7.2,
        0.9,
        "Fitting a line, two ways: the frequentist and the Bayesian perspective",
        size=20,
    )
    hline(s, 0.56, 4.43, 1.25, color=S.BLUE, weight=3)
    text(s, LEFT, 4.67, 7.0, 0.42, PRESENTER, size=20, bold=True, color=S.GREY_DARK)
    text(s, LEFT, 5.08, 7.0, 0.67, AFFILIATION, size=14, color="#666666")
    token_bars(
        s,
        8.12,
        0.76,
        9,
        seed=3,
        accents={(2, 1): S.BLUE, (5, 0): S.ROSE_LIGHT, (7, 2): S.SAGE_LIGHT},
    )
    image(s, "title_motif", 8.12, 3.25, 4.75, 3.6)


def section_slide(d, number, title, subtitle, notes):
    s = d.slide(notes=notes)
    text(
        s,
        0.3,
        0.9,
        3.2,
        3.9,
        str(number),
        size=200,
        bold=True,
        color=S.GREY_BAR,
        align=PP_ALIGN.LEFT,
        line=1.0,
        spacing=0,
    )
    text(s, 2.9, 2.35, 9.5, 1.0, title, size=44, bold=True)
    text(s, 2.95, 3.3, 9.5, 0.6, subtitle, size=20)
    hline(s, 3.05, 4.15, 1.25, color=S.BLUE)
    token_bars(s, 8.12, 5.6, 4, seed=number * 7)
    return s


ANIM = ROOT / "animations" / "renders"

# Slide timing for a video that starts automatically and loops until stopped
# (what PowerPoint writes for Playback > Start: Automatically + Loop until Stopped).
AUTOPLAY_LOOP_TIMING = (
    '<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
    '<p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
    '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
    '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>'
    '<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
    '<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
    '<p:par><p:cTn id="5" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" '
    'nodeType="afterEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
    '<p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="6" dur="{dur}" fill="hold"/>'
    '<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:cmd>'
    "</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>"
    "</p:childTnLst></p:cTn>"
    '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
    '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
    "</p:seq>"
    '<p:video><p:cMediaNode vol="80000"><p:cTn id="7" repeatCount="indefinite" fill="hold" display="0">'
    '<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn>'
    '<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cMediaNode></p:video>'
    "</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>"
)


def video_slide(d, name, notes, duration_ms=25000):
    """Full-bleed, untitled slide with a concept animation that autoplays and loops."""
    video = ANIM / f"{name}.mp4"
    poster = ANIM / f"{name}_poster.png"
    if not video.exists():
        print(
            f"  skipped video slide: {video.relative_to(ROOT)} not found (run `make animations`)"
        )
        return None
    s = d.slide(number=False, notes=notes)
    movie = s.shapes.add_movie(
        str(video),
        0,
        0,
        d.prs.slide_width,
        d.prs.slide_height,
        poster_frame_image=str(poster) if poster.exists() else None,
        mime_type="video/mp4",
    )
    timing = etree.fromstring(
        AUTOPLAY_LOOP_TIMING.format(spid=movie.shape_id, dur=duration_ms)
    )
    sld = s._element
    old = sld.find(qn("p:timing"))
    if old is not None:
        sld.replace(old, timing)
    else:
        sld.find(qn("p:clrMapOvr")).addnext(timing)
    return s


def handson_slide(d, n, title, tasks, notes):
    url = N["urls"][f"nb{n}"]
    s = d.slide(title=f"Hands-on {n}", subtitle=title, notes=notes)
    box(s, LEFT, TOP, 7.6, 4.95)
    text(
        s,
        LEFT + 0.3,
        TOP + 0.2,
        7.0,
        0.4,
        "In the notebook",
        size=14,
        bold=True,
        color=S.GREY_MID,
    )
    for i, t in enumerate(tasks):
        yy = TOP + 0.75 + i * 1.0
        step_number(s, i + 1, LEFT + 0.3, yy + 0.04)
        text(s, LEFT + 0.75, yy - 0.02, 6.6, 0.95, t, size=18)
    image(s, f"qr_0{n}", 8.75, TOP, 2.6, 2.6)
    text(
        s,
        8.3,
        TOP + 2.7,
        3.5,
        0.4,
        f"Notebook {n} in Colab",
        size=16,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    hyperlink(
        s,
        8.3,
        TOP + 3.1,
        3.5,
        0.4,
        "Open in Colab ↗",
        url,
        size=14,
        align=PP_ALIGN.CENTER,
    )
    text(
        s,
        LEFT,
        6.85,
        11,
        0.35,
        "Stuck? Ask your neighbour first, then raise your hand. Solutions are shared after class.",
        size=12,
        color=S.GREY_MID,
    )
    return s


# ----------------------------------------------------------------------------
# Content
# ----------------------------------------------------------------------------
def intro(d):
    title_slide(d)

    s = d.slide(
        title="Today",
        subtitle="Three blocks: short slides, then hands-on in a notebook",
        notes="""
Walk through the plan: each block has short slides, then a notebook.
Emphasise that the notebooks are 'run, read, modify' - nobody needs to write code from scratch.
""",
    )
    blocks = [
        (
            "Drawing a line",
            "Least squares and maximum likelihood.\nReading statsmodels output.",
        ),
        (
            "How sure are we?",
            "Standard errors, confidence intervals and p-values.\nPriors, posteriors and credible intervals.",
        ),
        (
            "More than one predictor",
            "Binary predictors, centering, and what\n'holding the other constant' means.",
        ),
        (
            "Quiz",
            "15 questions with instant corrections.\nThen we discuss the hardest ones.",
        ),
    ]
    xs = [LEFT, LEFT + 3.15, LEFT + 6.3, LEFT + 9.45]
    for i, (t, desc) in enumerate(blocks):
        x = xs[i]
        box(s, x, TOP, 2.95, 4.6)
        step_number(s, i + 1, x + 0.22, TOP + 0.3, d=0.42, size=16)
        text(s, x + 0.2, TOP + 0.95, 2.6, 0.9, t, size=20, bold=True, line=1.0)
        text(s, x + 0.2, TOP + 1.9, 2.6, 2.6, desc, size=16)
    text(
        s,
        LEFT,
        6.55,
        12.4,
        0.4,
        "Break between blocks 2 and 3",
        size=14,
        color=S.GREY_MID,
    )

    s = d.slide(
        title="By the end of today you can…",
        notes="""
Read these quickly; we come back to them in the wrap-up.
""",
    )
    goals = [
        "explain what the **intercept**, the **slope** and **σ** of a fitted line mean,",
        "describe **least squares** and **maximum likelihood** in one sentence each,",
        "correctly read a **standard error**, a **95% confidence interval** and a **p-value**,",
        "explain a **posterior** as 'many plausible lines' and read a **credible interval**,",
        "fit the same model with `statsmodels` and `PyMC` and compare the results,",
        "interpret a model with **two predictors**.",
    ]
    for i, g in enumerate(goals):
        yy = TOP + i * 0.78
        step_number(s, i + 1, LEFT + 0.1, yy + 0.06)
        text(s, LEFT + 0.6, yy, 11.6, 0.6, g, size=20)

    s = d.slide(
        title="Getting set up",
        subtitle="Open Notebook 1 now, so it is ready when we need it",
        notes="""
Common issues: not logged into Google; forgetting to 'Save a copy in Drive' (changes are
then lost). The first cell installs/imports PyMC, which can take a moment.
""",
    )
    url = N["urls"]["nb1"]
    image(s, "qr_01", LEFT, TOP + 0.05, 2.3, 2.3)
    hyperlink(s, LEFT, TOP + 2.45, 3.0, 0.4, "Open Notebook 1 in Colab ↗", url, size=14)
    steps = [
        "Scan the code or click the link (Google account needed).",
        "**File → Save a copy in Drive**, so your changes are kept.",
        "Run the first cell: click it and press **Shift + Enter**.",
    ]
    for i, t in enumerate(steps):
        yy = TOP + 0.05 + i * 0.8
        step_number(s, i + 1, 3.2, yy + 0.04)
        text(s, 3.65, yy - 0.02, 3.5, 0.75, t, size=16)
    box(s, 7.6, TOP, 5.27, 4.6)
    text(
        s,
        7.9,
        TOP + 0.2,
        4.8,
        0.4,
        "How the notebooks work",
        size=16,
        bold=True,
    )
    tips = [
        ("Top to bottom", "Run the cells in order with Shift + Enter."),
        ("Exercise cells", "Complete the ___ blanks or change something, then run."),
        ("Something broke?", "Runtime → Restart session and run all."),
        ("Solutions", "Shared after class as separate notebooks."),
    ]
    for i, (lab, desc) in enumerate(tips):
        yy = TOP + 0.85 + i * 0.9
        text(s, 7.9, yy, 4.8, 0.4, lab, size=18, bold=True)
        text(s, 7.9, yy + 0.36, 4.8, 0.6, desc, size=14, color=S.GREY_MID, line=1.0)


def block1(d):
    R = N["reading"]
    section_slide(
        d,
        1,
        "Drawing a line through data",
        "Least squares and maximum likelihood",
        """
Block 1. Goal: understand what a fitted line is and how it is chosen.
No uncertainty yet - that is block 2.
""",
    )

    s = d.slide(
        title="Why fit a line?",
        subtitle="Regression summarises how an outcome changes with a predictor",
        notes="""
Three uses of regression. Today mostly 'describe', a bit of 'predict'.
Careful with 'explain': comparing groups is not the same as finding causes.
""",
    )
    items = [
        ("Describe", "How does reading time change with the length of a text?"),
        ("Predict", "How long will it take to read a 1,000-word text?"),
        (
            "Compare",
            "Do children of mothers who finished high school score higher, at equal maternal IQ?",
        ),
    ]
    for i, (t, q) in enumerate(items):
        x = LEFT + i * 4.17
        step(s, i + 1, x, TOP + 0.2, t, w=3.9, size=20)
        card(s, x, TOP + 0.8, 3.95, 2.6, f"“{q}”", size=20)
    callout(
        s,
        LEFT,
        TOP + 3.75,
        12.4,
        1.0,
        "One outcome **y**, one or more predictors **x**, and a line (or plane) that "
        "summarises how y changes with x.",
        accent=S.BLUE,
        size=18,
    )

    s = d.slide(
        title="Our first dataset",
        subtitle="How long does it take to read a text?",
        notes="""
Simulated data: we chose the true values ourselves, so later we can check whether the
methods recover them. In real life we never know the truth.
Ask: by eye, where would you draw the line?
""",
    )
    text(
        s,
        LEFT,
        TOP,
        4.8,
        3.2,
        [
            f"**{R['n']} texts** (simulated)",
            "**x** = text length (hundreds of words)",
            "**y** = reading time (minutes)",
            "Question: which line best describes these points?",
        ],
        size=18,
        bullets=True,
        spacing=12,
    )
    callout(
        s,
        LEFT,
        TOP + 3.3,
        4.8,
        1.55,
        "{sage!:We made these data ourselves},\nso we know the truth:\n"
        "{sage:a = 0.5,  b = 0.8,  σ = 1.0}",
        accent=S.SAGE,
        size=16,
    )
    image(s, "b1_scatter", 5.47, TOP, 7.4, 5.0)

    s = d.slide(
        title="Anatomy of a line",
        subtitle="Two numbers describe a straight line",
        notes="""
Intercept: value of y when x = 0 (here: 'time to get started'). Often not meaningful by
itself - we come back to that with centering in block 3.
Slope: change in y for a one-unit increase in x. Units matter: minutes per 100 words.
""",
    )
    text(s, LEFT, TOP, 4.8, 1.0, "y = {rose!:a} + {blue!:b} · x", size=32)
    text(
        s,
        LEFT,
        TOP + 1.05,
        4.8,
        3.6,
        [
            "{rose!:a, the intercept}: the predicted y when x = 0",
            "{blue!:b, the slope}: how much y changes when x increases by 1",
            "Here: each extra 100 words adds about **0.8 minutes**",
        ],
        size=18,
        bullets=True,
        spacing=14,
    )
    image(s, "b1_anatomy", 5.47, TOP, 7.4, 5.0)

    s = d.slide(
        title="Points don't sit on the line",
        subtitle="The error term ε captures everything the line does not explain",
        notes="""
The model has three parameters: a, b and sigma. Sigma is often forgotten but matters for
prediction. Normal errors is an assumption - checking it is a topic for a later session.
""",
    )
    image(s, "eq_line", LEFT, 1.65, 9.0, 1.15)
    text(
        s,
        LEFT,
        TOP + 1.35,
        4.9,
        3.6,
        [
            "We assume the errors follow a **Normal** distribution centred on the line",
            "{sage!:σ} (sigma) = how spread out the points are around the line",
            "Three numbers to learn from data: **a**, **b** and **σ**",
        ],
        size=18,
        bullets=True,
        spacing=14,
    )
    image(s, "b1_error", 5.9, TOP + 1.2, 6.97, 4.1)

    video_slide(
        d,
        "01_where_data_come_from",
        notes="""
Animation (25 s loop, starts automatically, no sound). Talk over it:
0-3 s   the TRUE line (green, dashed): known only because we simulate.
3-6 s   bell curves along the line: for each text length, reading times scatter around the
        line with spread sigma.
6-15 s  each text is drawn: it starts ON the true line and drops to its observed value.
        The green trail is its error epsilon.
17-20 s we only see the points, so we fit a line: least squares (blue). Close to the truth,
        not on it.
20-23 s the residuals (observed - predicted) flash: least squares makes their squares small.
""",
    )

    s = d.slide(
        title="Which line is best?",
        subtitle="Residual = observed − predicted",
        notes="""
Every candidate line gives 40 residuals. We need ONE number that says how good the line is.
Ask: why not just add the residuals up? (Positive and negative cancel.)
""",
    )
    text(
        s,
        LEFT,
        TOP,
        4.8,
        4.5,
        [
            "For every point, the **residual** is the vertical distance to the line",
            "A good line has small residuals overall",
            "Positive and negative residuals would cancel out if we just added them…",
            "…so how do we turn 40 residuals into one score?",
        ],
        size=18,
        bullets=True,
        spacing=14,
    )
    image(s, "b1_residuals", 5.47, TOP, 7.4, 5.0)

    rss = N["rss"]
    s = d.slide(
        title="Least squares",
        tag="freq",
        subtitle="Choose a and b to make the sum of squared residuals (RSS) as small as possible",
        notes=f"""
Squaring makes all residuals positive and penalises big misses more.
The poor guess has RSS = {rss["A poor guess"]}, the least-squares line {rss["The least-squares line"]}.
No other line has a smaller RSS. In the notebook they try to beat it with sliders.
Ordinary least squares (OLS) = this criterion. There is a closed-form formula (appendix).
""",
    )
    image(s, "eq_rss", LEFT, 1.62, 5.6, 0.62)
    image(s, "b1_least_squares", LEFT, 2.3, 12.4, 4.7)

    s = d.slide(
        title="Maximum likelihood",
        tag="freq",
        subtitle="Choose the line under which the observed data are most probable",
        notes="""
Second way of thinking: each line + sigma defines a 'cloud' of Normal curves. The likelihood
is the product of the heights of these curves at the observed points.
Key result: with Normal errors, maximising the likelihood gives exactly the least-squares
line (proof in the appendix). The likelihood will come back as half of Bayes' rule.
""",
    )
    image(s, "eq_likelihood", LEFT, 1.62, 7.2, 0.62)
    image(s, "b1_mle", LEFT, 2.3, 12.4, 4.0)
    callout(
        s,
        LEFT,
        6.35,
        12.4,
        0.6,
        "With Normal errors, **least squares = maximum likelihood**: same line, two stories.",
        accent=S.BLUE,
        size=16,
    )

    s = d.slide(
        title="Reading the output",
        tag="freq",
        subtitle="statsmodels does the least-squares fit for us",
        notes=f"""
Formula 'time ~ words' reads 'time explained by words'. The intercept is added automatically.
Focus on the coef column only. Compare with the truth: {R["ols"]["Intercept"]} vs 0.5 and
{R["ols"]["words"]} vs 0.8 - close but not exact, because of noise in a finite sample.
The other columns are the topic of block 2.
""",
    )
    code(
        s,
        LEFT,
        TOP,
        6.3,
        1.55,
        """
import statsmodels.formula.api as smf

fit = smf.ols("time ~ words", data=df).fit()
fit.summary()""",
        size=14,
    )
    p_ = R["ols_p"]
    rows = [
        ["", "coef", "std err", "t", "P>|t|", "[0.025", "0.975]"],
        [
            "Intercept",
            fmt(R["ols"]["Intercept"], 3),
            fmt(R["ols_se"]["Intercept"], 3),
            fmt(R["ols_t"]["Intercept"], 3),
            fmt(p_["Intercept"], 3),
            fmt(R["ols_ci"]["Intercept"][0], 3),
            fmt(R["ols_ci"]["Intercept"][1], 3),
        ],
        [
            "words",
            fmt(R["ols"]["words"], 3),
            fmt(R["ols_se"]["words"], 3),
            fmt(R["ols_t"]["words"], 3),
            "0.000",
            fmt(R["ols_ci"]["words"][0], 3),
            fmt(R["ols_ci"]["words"][1], 3),
        ],
    ]
    table(
        s,
        LEFT,
        TOP + 1.85,
        [1.6, 1.15, 1.15, 1.15, 1.15, 1.15, 1.15],
        rows,
        size=16,
        highlight={1: (S.BLUE_LIGHT, S.BLUE_DARK)},
        row_h=0.5,
        mono_cols=(1, 2, 3, 4, 5, 6),
    )
    text(
        s,
        LEFT,
        TOP + 3.6,
        6.3,
        1.4,
        [
            "{blue!:coef}: the estimates of **a** (Intercept) and **b** (words)",
            "std err, t, P>|t| and the interval: **block 2**",
        ],
        size=16,
        bullets=True,
        spacing=8,
    )
    callout(
        s,
        7.1,
        TOP,
        5.77,
        1.55,
        f"Estimated:  a = {fmt(R['ols']['Intercept'])},  b = {fmt(R['ols']['words'])}\n"
        "{sage:Truth:  a = 0.5,  b = 0.8}\n"
        "Close, but not exact: the data are noisy.",
        accent=S.SAGE,
        size=16,
    )
    callout(
        s,
        7.1,
        TOP + 3.55,
        5.77,
        1.3,
        "**Prediction** for a 1,000-word text:\n"
        f"{fmt(R['ols']['Intercept'])} + {fmt(R['ols']['words'])} × 10 = "
        f"**{R['ols']['Intercept'] + 10 * R['ols']['words']:.1f} minutes**",
        accent=S.BLUE,
        size=16,
    )

    handson_slide(
        d,
        1,
        "Fitting a line",
        [
            "**Guess the line** with sliders: can you beat the least-squares RSS?",
            "Fit the model with `statsmodels` and compare with the truth.",
            "Change the sample size and the noise: what happens to the estimates?",
            "Predict the reading time of a 1,000-word text.",
        ],
        notes="""
Walk around. Typical issue: forgetting to run cells from the top.
Quick debrief: who got closest to the least-squares RSS with the sliders?
""",
    )


def block2(d):
    R, B = N["reading"], N["bayes"]
    section_slide(
        d,
        2,
        "How sure are we?",
        "Two answers: frequentist and Bayesian",
        """
Block 2. The densest block. Optional slides: the priors slide and 'when do they disagree'
(both topics are also in the notebook).
""",
    )

    s = d.slide(
        title="Two meanings of probability",
        tag="both",
        subtitle="Same data, same model, different questions",
        notes="""
Recap from the Bayesian intro. Frequentist: parameters are fixed but unknown; probability
describes what would happen over repeated samples. Bayesian: probability describes our
uncertainty about the parameters themselves.
""",
    )
    rows = [
        (
            "Probability is…",
            "the long-run frequency over repeated samples",
            "a degree of belief, given what we know",
        ),
        (
            "The true slope b is…",
            "fixed but unknown",
            "uncertain: described by a distribution",
        ),
        (
            "What is random?",
            "the data (another sample would differ)",
            "the parameters (data are fixed once observed)",
        ),
        (
            "Uncertainty is shown by…",
            "standard errors, confidence intervals, p-values",
            "the posterior and credible intervals",
        ),
    ]
    pill(s, 3.75, TOP, 4.3, 0.45, "FREQUENTIST", S.GREY_BAR, S.GREY_DARK, size=14)
    pill(s, 8.4, TOP, 4.3, 0.45, "BAYESIAN", S.GREY_BAR, S.GREY_DARK, size=14)
    for i, (lab, f, b) in enumerate(rows):
        yy = TOP + 0.65 + i * 1.08
        text(s, LEFT, yy + 0.15, 3.2, 0.8, lab, size=16, bold=True)
        card(s, 3.75, yy, 4.3, 0.95, f, size=16, pad=0.15, anchor=MSO_ANCHOR.MIDDLE)
        card(s, 8.4, yy, 4.3, 0.95, b, size=16, pad=0.15, anchor=MSO_ANCHOR.MIDDLE)

    s = d.slide(
        title="New data, new line",
        tag="freq",
        subtitle="If we repeated the study, we would get a different slope each time",
        notes="""
Three new samples from the same 'world' (same true line, dashed green). Each gives a
different estimate. This variation between samples is what frequentist uncertainty is about.
""",
    )
    image(s, "b2_three_datasets", LEFT, TOP, 12.4, 5.0)

    video_slide(
        d,
        "02_repeat_the_study",
        notes=f"""
Animation (25 s loop, starts automatically, no sound). Talk over it:
Each flash is a new study of 40 texts from the same world (green = true line / true slope).
Its least-squares line (blue) is drawn and its slope drops as a brick on the right.
First slowly (5 studies), then 200 studies in a rush: the blue lines fan out around the truth
and the bricks pile up into a bell shape: the SAMPLING DISTRIBUTION of the slope.
22 s: the bracket is +/- 1 SD of that pile (about {N["sampling_sd"]:.3f}): the STANDARD ERROR.
statsmodels estimates it from a single study ({N["reading"]["ols_se"]["words"]:.3f}), next slide.
""",
    )

    sd = N["sampling_sd"]
    s = d.slide(
        title="The standard error",
        tag="freq",
        subtitle="How much the estimate would vary from study to study",
        notes=f"""
We repeated the study 2000 times: same 40 texts, new reading times (new readers).
Their slopes spread around the truth with SD ≈ {sd}. That SD is what the standard error
estimates: statsmodels estimated it from ONE dataset: {R["ols_se"]["words"]}. The two agree
because the standard error describes exactly this kind of repetition (text lengths fixed);
the small difference is simulation noise.
Rule of thumb: more data → smaller standard error (÷2 for 4× data).
""",
    )
    text(
        s,
        LEFT,
        TOP,
        4.8,
        3.0,
        [
            "Repeat the study 2,000 times: same 40 texts, new reading times",
            f"Their spread (SD ≈ {sd:.3f}) is the **standard error**",
            f"From our single dataset, statsmodels estimates it at **{R['ols_se']['words']:.3f}**",
        ],
        size=18,
        bullets=True,
        spacing=12,
    )
    table(
        s,
        LEFT,
        TOP + 3.35,
        [1.6, 1.4, 1.6],
        [
            ["", "coef", "std err"],
            ["words", fmt(R["ols"]["words"], 3), fmt(R["ols_se"]["words"], 3)],
        ],
        size=16,
        highlight={2: (S.BLUE_LIGHT, S.BLUE_DARK)},
        row_h=0.5,
        mono_cols=(1, 2),
    )
    image(s, "b2_sampling_dist", 5.47, TOP, 7.4, 5.0)

    ci = R["ols_ci"]["words"]
    cov = N["ci_coverage"]
    s = d.slide(
        title="Confidence intervals",
        tag="freq",
        subtitle="A procedure that captures the truth in 95% of studies",
        notes=f"""
Interval ≈ estimate ± 2 standard errors. In the simulation {cov["n"] - cov["miss"]} of {cov["n"]}
intervals contain the truth. The 95% is a property of the PROCEDURE, not of our one interval:
our interval either contains 0.8 or it doesn't. The 'probability that b is in the interval'
reading is the Bayesian credible interval - coming up.
""",
    )
    text(
        s,
        LEFT,
        TOP,
        4.8,
        2.4,
        [
            f"Our interval: **[{fmt(ci[0])}, {fmt(ci[1])}]**  (≈ estimate ± 2 SE)",
            "Over many studies, **95% of intervals built this way contain the true slope**",
        ],
        size=18,
        bullets=True,
        spacing=12,
    )
    table(
        s,
        LEFT,
        TOP + 2.35,
        [1.6, 1.2, 1.9],
        [
            ["", "coef", "[0.025   0.975]"],
            ["words", fmt(R["ols"]["words"], 3), f"{fmt(ci[0], 3)}   {fmt(ci[1], 3)}"],
        ],
        size=16,
        highlight={2: (S.BLUE_LIGHT, S.BLUE_DARK)},
        row_h=0.5,
        mono_cols=(1, 2),
    )
    callout(
        s,
        LEFT,
        TOP + 3.6,
        4.8,
        1.35,
        "It does **not** mean: “there is a 95% probability that b is in "
        f"[{fmt(ci[0])}, {fmt(ci[1])}]”.",
        accent=S.GREY_DARK,
        size=16,
    )
    image(s, "b2_ci_coverage", 5.47, TOP, 7.4, 5.0)

    # Misreadings of a confidence interval. Rows 1-3: the classic list (Wikipedia,
    # "Confidence interval" > Common misunderstandings; Methods 2 week 3). Rows 4-5:
    # Regression and Other Stories, §4.4 and §1.5 / §4.2.
    iv = f"[{fmt(ci[0])}, {fmt(ci[1])}]"
    s = d.slide(
        title="What a 95% CI is not",
        tag="freq",
        subtitle=f"Five common misreadings, applied to our interval {iv}",
        notes="""
Common misreadings of a 95% confidence interval, each next to its correction.
Rows 1-3 are the classic list: Wikipedia "Confidence interval" (Common misunderstandings),
citing Morey et al. (2016), Greenland et al. (2016) and Hazra (2017); the same three are on
the Methods 2 week-3 slide "What confidence intervals are not".
Rows 4-5 come from Regression and Other Stories: "It is never possible to 'accept' a
statistical hypothesis" (§4.4); coverage holds "if the model is correct" (§4.2), and intervals
reported because they exclude zero do not have 95% coverage in the real world (§1.5).
Link back: Notebook 2, exercise 4.1 (true slope 0.05, yet p = 0.26 and the CI includes 0).

Extra points:
- Not all values inside are equally plausible. ROS §1.5: Jamaica study, 95% CI for the
  earnings effect [+2%, +98%]; an effect of 2% (or even 0%) is plausible, doubling earnings is not.
- Two overlapping (or touching) CIs do not imply "no difference", and one CI excluding the
  other group's estimate does not imply a difference (Belia et al. 2005): look at the CI of
  the difference instead.
- ROS §8.4 suggests "uncertainty interval" or "compatibility interval": the range of values
  most compatible with the data, given the model.
""",
    )
    rows = [
        (
            f"“There is a 95% probability that b lies in {iv}.”",
            "The slope is fixed: this interval either contains it or not. The 95% describes "
            "the **procedure** over many studies (the probability reading is a credible interval).",
        ),
        (
            f"“95% of our data lie inside {iv}.”",
            "It is an interval for **one parameter** (the slope), not a range for the data. "
            f"Individual reading times scatter far more (σ ≈ {R['ols_sigma']:.1f} min).",
        ),
        (
            "“A replication's slope will fall inside it with 95% probability.”",
            "Not in general: our interval may itself be off-centre. What is 95% is the share of "
            "replications whose **own** intervals capture the true slope.",
        ),
        (
            "“The interval includes 0, so there is no effect.”",
            "The data cannot rule out 0, but cannot rule out values far from 0 either. "
            "**Not rejected ≠ accepted**: the effect may be small, or the study too small.",
        ),
        (
            "“The 95% coverage is guaranteed.”",
            "Only if the **model is right** and intervals are not picked for being “significant”: "
            "published intervals that exclude 0 cover the truth less often.",
        ),
    ]
    LW, RW, GAP, RH, RG = 4.75, 7.45, 0.2, 0.9, 0.12
    for i, (wrong, right) in enumerate(rows):
        y = TOP + i * (RH + RG)
        box(s, LEFT, y, LW, RH, fill=S.GREY_CARD)
        mark(s, "no", LEFT + 0.15, y + (RH - 0.34) / 2, fill=S.GREY_DARK)
        text(
            s,
            LEFT + 0.6,
            y + 0.04,
            LW - 0.72,
            RH - 0.08,
            f"*{wrong}*",
            size=15,
            color=S.GREY_DARK,
            anchor=MSO_ANCHOR.MIDDLE,
            spacing=0,
            line=1.0,
        )
        x2 = LEFT + LW + GAP
        box(s, x2, y, RW, RH, fill=S.BLUE_LIGHT)
        mark(s, "yes", x2 + 0.15, y + (RH - 0.34) / 2, fill=S.BLUE_DARK)
        text(
            s,
            x2 + 0.6,
            y + 0.04,
            RW - 0.72,
            RH - 0.08,
            right,
            size=14,
            anchor=MSO_ANCHOR.MIDDLE,
            spacing=0,
            line=1.0,
        )
    text(
        s,
        LEFT,
        6.86,
        11.6,
        0.32,
        "Sources: Wikipedia, “Confidence interval” (Common misunderstandings): Morey et al. 2016, "
        "Greenland et al. 2016, Hazra 2017 · Gelman, Hill & Vehtari 2020, ROS §1.5, §4.2, §4.4",
        size=10,
        color=S.GREY_MID,
    )

    s = d.slide(
        title="p-values",
        tag="freq",
        subtitle="How surprising would our slope be if the true slope were 0?",
        notes=f"""
The 'null world': same design, but no relation between length and time. In 2000 simulated
null studies, no slope came anywhere near {R["ols"]["words"]:.2f} - so p is tiny (statsmodels prints 0.000).
Common misreadings: p is NOT the probability that the null hypothesis is true, and a small p
does not mean a large or important effect.
""",
    )
    text(
        s,
        LEFT,
        TOP,
        4.8,
        2.5,
        [
            "Imagine a **null world** where the true slope is 0",
            "**p-value** = how often that world produces a slope at least as extreme as ours",
            "Here: essentially never  →  p < 0.001",
        ],
        size=18,
        bullets=True,
        spacing=12,
    )
    table(
        s,
        LEFT,
        TOP + 2.55,
        [1.6, 1.4, 1.4],
        [
            ["", "coef", "P>|t|"],
            ["words", fmt(R["ols"]["words"], 3), "0.000"],
        ],
        size=16,
        highlight={2: (S.BLUE_LIGHT, S.BLUE_DARK)},
        row_h=0.5,
        mono_cols=(1, 2),
    )
    callout(
        s,
        LEFT,
        TOP + 3.7,
        4.8,
        1.25,
        "**Not** the probability that the null is true.\n"
        "Small p ≠ large or important effect.",
        accent=S.GREY_DARK,
        size=16,
    )
    image(s, "b2_pvalue", 5.47, TOP, 7.4, 5.0)

    s = d.slide(
        title="The Bayesian route",
        tag="bayes",
        subtitle="Combine what we knew before with what the data say",
        notes="""
Same likelihood as in maximum likelihood - this is the bridge between the two worlds.
New: the prior (what is plausible before seeing data) and the posterior (what is plausible
after). '∝' = proportional to: we drop a constant that does not depend on a, b, sigma.
""",
    )
    image(s, "eq_bayes", 1.2, TOP + 0.1, 10.9, 1.45)
    cards = [
        (
            "Posterior",
            S.ROSE_DARK,
            "What is plausible **after** seeing the data: a whole distribution, not one number.",
        ),
        (
            "Likelihood",
            S.BLUE_DARK,
            "How probable the data are for given a, b, σ: the **same** as in maximum likelihood.",
        ),
        ("Prior", S.ROSE, "What we consider plausible **before** seeing the data."),
    ]
    for i, (t, c, body) in enumerate(cards):
        x = LEFT + i * 4.17
        box(s, x, TOP + 1.95, 3.95, 0.08, fill=c, shape=MSO_SHAPE.RECTANGLE)
        text(s, x, TOP + 2.15, 3.95, 0.45, t, size=20, bold=True, color=c)
        text(s, x, TOP + 2.65, 3.95, 1.5, body, size=16)
    callout(
        s,
        LEFT,
        TOP + 4.25,
        12.4,
        0.7,
        "∝ means “proportional to”: the missing constant does not depend on a, b or σ, "
        "and the sampler does not need it.",
        accent=S.ROSE,
        size=15,
    )

    s = d.slide(
        title="Priors",
        tag="bayes",
        subtitle="Before seeing data: which lines do we consider plausible?",
        notes="""
Each pink line is one draw from the prior. A vague prior allows absurd lines (reading a
text in -50 minutes). A weakly informative prior keeps the right order of magnitude but
still lets the data decide. With 40 data points the choice barely matters here
(see 'when do they disagree').
""",
    )
    image(s, "b2_prior_lines", LEFT, TOP, 12.4, 4.6)
    text(
        s,
        LEFT,
        6.5,
        12.4,
        0.45,
        "We use **weakly informative** priors: rule out absurdly large values, then let the data speak.",
        size=16,
    )

    s = d.slide(
        title="Writing the model",
        tag="bayes",
        subtitle="The maths and the PyMC code say the same thing, line by line",
        notes="""
Map each line of the maths to the code. 'observed=' is what turns the Normal into a
likelihood. pm.sample() runs MCMC (next slide) and returns posterior draws.
""",
    )
    box(s, LEFT, TOP, 4.9, 4.4)
    text(
        s,
        LEFT + 0.25,
        TOP + 0.2,
        4.4,
        0.4,
        "Model",
        size=14,
        bold=True,
        color=S.GREY_MID,
    )
    text(s, LEFT + 0.25, TOP + 0.75, 4.5, 0.35, "likelihood", size=13, color=S.GREY_MID)
    text(
        s,
        LEFT + 0.25,
        TOP + 1.1,
        4.5,
        0.5,
        "{blue:time  ~  Normal(a + b · words, σ)}",
        size=18,
    )
    text(s, LEFT + 0.25, TOP + 1.95, 4.5, 0.35, "priors", size=13, color=S.GREY_MID)
    text(
        s,
        LEFT + 0.25,
        TOP + 2.3,
        4.5,
        1.8,
        [
            "{rose:a  ~  Normal(0, 5)}",
            "{rose:b  ~  Normal(0, 2)}",
            "{rose:σ  ~  HalfNormal(2)}",
        ],
        size=18,
        spacing=10,
    )
    code(
        s,
        5.6,
        TOP,
        7.27,
        4.4,
        """
import pymc as pm

with pm.Model() as model:
    # priors
    intercept = pm.Normal("intercept", mu=0, sigma=5)
    slope = pm.Normal("slope", mu=0, sigma=2)
    sigma = pm.HalfNormal("sigma", sigma=2)

    # likelihood
    mu = intercept + slope * df["words"]
    pm.Normal("time", mu=mu, sigma=sigma,
              observed=df["time"])

    idata = pm.sample()""",
        size=14,
    )

    s = d.slide(
        title="Many plausible lines",
        tag="bayes",
        subtitle="The posterior is a distribution over lines, not a single best line",
        notes="""
Each pink line is one draw of (a, b) from the posterior. Together they show which lines are
compatible with the data and the prior. Notice they fan out at the edges, where there is
less data. The dashed blue line is the least-squares fit: right in the middle.
""",
    )
    text(
        s,
        LEFT,
        TOP,
        4.8,
        4.5,
        [
            "Each pink line is one draw (a, b) from the posterior",
            "Lines agree where the data are dense and spread out at the edges",
            "With weak priors, they surround the least-squares line",
        ],
        size=18,
        bullets=True,
        spacing=14,
    )
    image(s, "b2_spaghetti", 5.47, TOP, 7.4, 5.0)

    s = d.slide(
        title="MCMC in one picture",
        tag="bayes",
        subtitle="We cannot write the posterior down, so we draw samples from it",
        notes="""
Markov chain Monte Carlo: a sampler moves through parameter space, spending time in each
region in proportion to its posterior probability. PyMC uses NUTS. We run 2 chains from
different starting points; if they agree (r_hat ≈ 1.00) we trust the result.
""",
    )
    image(s, "b2_mcmc", LEFT, TOP, 12.4, 4.7)
    text(
        s,
        LEFT,
        6.5,
        12.4,
        0.45,
        "Check that independent chains agree: **r_hat ≈ 1.00** in `az.summary(idata)`.",
        size=16,
    )

    s = d.slide(
        title="Credible intervals",
        tag="bayes",
        subtitle="Read the posterior directly as probabilities about the slope",
        notes=f"""
95% credible interval: the middle 95% of the posterior draws. It CAN be read as 'given the
model and the prior, there is a 95% probability that b is in this range'.
We can answer any question by counting draws: P(b > 0.8) = share of draws above 0.8 = {B["p_slope_gt_08"]}.
""",
    )
    text(
        s,
        LEFT,
        TOP,
        4.8,
        2.6,
        [
            f"**95% credible interval: [{fmt(B['slope_ci'][0])}, {fmt(B['slope_ci'][1])}]**",
            "Given model and prior, there is a 95% probability that b lies in this range",
        ],
        size=18,
        bullets=True,
        spacing=12,
    )
    callout(
        s,
        LEFT,
        TOP + 2.55,
        4.8,
        2.4,
        "Ask any question by counting draws:\n"
        f"P(b > 0 | data) = {B['p_slope_gt_0']:.2f}\n"
        f"P(b > 0.8 | data) = {B['p_slope_gt_08']:.2f}\n"
        "`(slope_draws > 0.8).mean()`",
        accent=S.ROSE,
        size=16,
    )
    image(s, "b2_credible", 5.47, TOP, 7.4, 5.0)

    s = d.slide(
        title="Side by side",
        tag="both",
        subtitle="With weak priors and enough data: the same numbers, different readings",
        notes="""
The numbers are almost identical here. What differs is the interpretation and what the
approach lets you do (direct probability statements; adding prior knowledge).
""",
    )
    rows = [
        ["", "Frequentist (statsmodels)", "Bayesian (PyMC)"],
        [
            "Estimate of b",
            fmt(R["ols"]["words"]),
            f"{fmt(B['slope_mean'])}  (posterior mean)",
        ],
        [
            "95% interval",
            f"[{fmt(ci[0])}, {fmt(ci[1])}]  confidence",
            f"[{fmt(B['slope_ci'][0])}, {fmt(B['slope_ci'][1])}]  credible",
        ],
        ["What is random?", "the data", "the parameters"],
        [
            "The interval says…",
            "95% of such intervals contain b",
            "95% probability that b is inside",
        ],
        ["Prior knowledge?", "not used", "explicit, via the prior"],
    ]
    table(
        s,
        LEFT,
        TOP,
        [2.6, 4.9, 4.9],
        rows,
        size=16,
        row_h=0.55,
        highlight={1: (S.GREY_CARD, S.GREY_DARK), 2: (S.GREY_CARD, S.GREY_DARK)},
    )
    image(s, "b2_compare_intervals", LEFT, TOP + 3.45, 12.4, 1.8)

    dis = N["disagree"]
    s = d.slide(
        title="When do they disagree?",
        tag="both",
        subtitle="Little data + a strong prior: the prior matters. More data: the data win.",
        notes=f"""
A colleague is convinced people read 250 words/min (b ≈ 0.4), typical of casual silent
reading, and encodes this as a strong prior Normal(0.4, 0.1). But our participants read
carefully for a comprehension test (125 words/min): the prior comes from a different situation. With n = 8 the posterior sits between prior and data
({dis[0]["bayes"]} vs least squares {dis[0]["ols"]}). With n = 400 both agree ({dis[2]["bayes"]} vs {dis[2]["ols"]}).
Priors are an explicit, debatable assumption - report them.
""",
    )
    image(s, "b2_disagree", LEFT, TOP, 12.4, 4.85)
    text(
        s,
        LEFT,
        6.65,
        12.4,
        0.4,
        "Priors are assumptions: state them, justify them, and check how much they matter.",
        size=16,
    )

    handson_slide(
        d,
        2,
        "Uncertainty, two ways",
        [
            "Simulate many studies: the standard error and confidence-interval coverage.",
            "Fit the Bayesian model with `PyMC` and check that r_hat ≈ 1.",
            "Plot plausible lines and compute P(slope > 0.8).",
            "Use only 8 texts and a strong prior: when do the approaches disagree?",
        ],
        notes="""
PyMC compiles the model the first time it runs in Colab, which takes a moment.
Then: break.
""",
    )

    s = d.slide(number=True, notes="Break.")
    text(
        s,
        LEFT,
        2.5,
        12.4,
        1.2,
        "Break",
        size=60,
        bold=True,
        align=PP_ALIGN.CENTER,
        line=1.0,
        spacing=0,
    )
    token_bars(s, 4.3, 5.2, 3, seed=11)


def block3(d):
    K = N["kid"]
    section_slide(
        d,
        3,
        "More than one predictor",
        "Real data, binary predictors and centering",
        """
Block 3. Real data from Regression and Other Stories (chapter 10).
Both approaches give nearly the same numbers here, so we focus on interpretation.
""",
    )

    s = d.slide(
        title="Real data: children's test scores",
        subtitle=f"{K['n']} children from a US survey (Gelman, Hill & Vehtari, 2020)",
        notes="""
kid_score: cognitive test score at age 3-4. mom_hs: 1 if the mother finished high school.
mom_iq: mother's IQ score (mean 100, SD 15). This is observational data: we can describe and
compare, but not claim causes.
""",
    )
    text(
        s,
        LEFT,
        TOP,
        4.8,
        4.6,
        [
            "`kid_score`: test score at age 3–4",
            "`mom_hs`: did the mother finish high school? (1 = yes, 0 = no)",
            "`mom_iq`: mother's IQ score",
            "Observational data: we can **compare**, not prove causes",
        ],
        size=18,
        bullets=True,
        spacing=14,
    )
    image(s, "b3_scatter", 5.47, TOP, 7.4, 5.0)
    text(
        s,
        LEFT,
        7.05,
        11.0,
        0.3,
        "Data: KidIQ, Gelman, Hill & Vehtari (2020), Regression and Other Stories, ch. 10.",
        size=10,
        color=S.GREY_MID,
    )

    hs = K["hs_only"]
    s = d.slide(
        title="A binary predictor",
        tag="freq",
        subtitle="With a 0/1 predictor, the slope is a difference between two group means",
        notes=f"""
kid_score ~ mom_hs. Intercept = mean score when mom_hs = 0 ({hs["Intercept"]}).
Slope = difference between the two group means ({hs["mom_hs"]}). The 'line' only connects two
group means.
""",
    )
    code(s, LEFT, TOP, 4.8, 0.85, 'smf.ols("kid_score ~ mom_hs", data=kid)', size=13)
    text(
        s,
        LEFT,
        TOP + 1.1,
        4.8,
        3.8,
        [
            f"**Intercept = {hs['Intercept']:.1f}**: average score when `mom_hs` = 0",
            f"**Slope = {hs['mom_hs']:.1f}**: children of mothers who finished high school score "
            f"{hs['mom_hs']:.1f} points higher on average",
        ],
        size=18,
        bullets=True,
        spacing=14,
    )
    image(s, "b3_binary", 5.47, TOP, 7.4, 5.0)

    s = d.slide(
        title="Centering",
        tag="freq",
        subtitle="Shift a predictor so that 0 is a meaningful value",
        notes=f"""
With raw IQ, the intercept ({K["iq_raw"]["Intercept"]}) is the predicted score for a mother
with IQ 0 - meaningless. Subtracting 100 moves 0 to an average IQ: the intercept becomes
{K["iq_c"]["Intercept"]}. The slope ({K["iq_c"]["mom_iq_c"]}) does not change.
""",
    )
    image(s, "b3_centering", LEFT, TOP, 12.4, 4.6)
    text(
        s,
        LEFT,
        6.5,
        12.4,
        0.45,
        f"`mom_iq_c = mom_iq − 100`:  the slope stays {K['iq_c']['mom_iq_c']:.2f}, the "
        "intercept becomes interpretable.",
        size=16,
    )

    b = K["both"]
    s = d.slide(
        title="Two predictors",
        tag="freq",
        subtitle="Each coefficient compares children who are equal on the other predictor",
        notes=f"""
b1 = {b["mom_hs"]}: comparing children whose mothers have the SAME IQ, those whose mothers
finished high school score {b["mom_hs"]} points higher on average.
b2 = {b["mom_iq_c"]}: comparing children whose mothers have the same high-school status, each
extra IQ point goes with {b["mom_iq_c"]} more points.
The model forces the same IQ slope in both groups: parallel lines.
""",
    )
    image(s, "eq_multi", LEFT, 1.6, 6.6, 0.55)
    text(
        s,
        LEFT,
        TOP + 0.6,
        4.8,
        4.3,
        [
            f"**b**_{{1}}** = {b['mom_hs']:.1f}**: high-school gap, at **equal** maternal IQ",
            f"**b**_{{2}}** = {b['mom_iq_c']:.2f}**: points per IQ point, at **equal** high-school status",
            f"**a = {b['Intercept']:.1f}**: mother without high school, IQ 100",
            "Same IQ slope in both groups → **parallel lines**",
        ],
        size=18,
        bullets=True,
        spacing=12,
    )
    image(s, "b3_parallel", 5.47, TOP + 0.3, 7.4 * 0.94, 5.0 * 0.94)

    video_slide(
        d,
        "03_holding_constant",
        duration_ms=30000,
        notes=f"""
Animation (30 s loop, starts automatically, no sound). What "controlling for IQ" means.
0-6 s    two groups of children; big dots = group means; blue bracket = the gap
         ({K["hs_only"]["mom_hs"]:.1f} points, the mom_hs-only model).
6-12 s   the groups move to the right panel; a copy of every child flies to the left panel:
         child's score against mother's IQ (same children, same vertical scale).
         Triangles: each group's mean IQ ({K["group_iq"]["0"]:.0f} vs {K["group_iq"]["1"]:.0f}).
12-15 s  the IQ slope from the two-predictor model ({b["mom_iq_c"]:.2f} points per IQ point,
         holding high school constant), drawn through the means (IQ 100).
15-21 s  CONTROLLING FOR IQ = setting that slope to 0. Every child's score is adjusted to what
         it would be at IQ 100: minus {b["mom_iq_c"]:.2f} x (IQ - 100). Same shift in both panels:
         children of low-IQ mothers (mostly "no") move up, high-IQ ones (mostly "yes") move down.
         The group means converge and the gap shrinks to {b["mom_hs"]:.1f} = the mom_hs coefficient.
21-27 s  hold: new gap ({b["mom_hs"]:.1f}) next to the dashed ghost of the old one ({K["hs_only"]["mom_hs"]:.1f}).
Exact: {K["hs_only"]["mom_hs"]:.1f} - {b["mom_iq_c"]:.2f} x ({K["group_iq"]["1"]:.1f} - {K["group_iq"]["0"]:.1f}) = {b["mom_hs"]:.2f}.
""",
    )

    s = d.slide(
        title="Why did it shrink?",
        tag="freq",
        subtitle=f"The mom_hs coefficient drops from {K['hs_only']['mom_hs']:.1f} to {b['mom_hs']:.1f} once IQ is in the model",
        notes=f"""
Mothers who finished high school have higher IQ on average ({K["group_iq"]["1"]:.0f} vs
{K["group_iq"]["0"]:.0f}). Alone, mom_hs 'absorbs' part of the IQ difference. Once IQ is in the
model, mom_hs only captures the gap at equal IQ. Lesson: a coefficient's meaning depends on
what else is in the model.
""",
    )
    image(s, "b3_coef_change", LEFT, TOP, 12.4, 4.6)
    text(
        s,
        LEFT,
        6.5,
        12.4,
        0.45,
        "A coefficient's meaning depends on **what else is in the model**.",
        size=16,
    )

    kb = K["bayes"]
    s = d.slide(
        title="Same model, both ways",
        tag="both",
        subtitle="434 children and weak priors: nearly identical answers",
        notes=f"""
Same formula logic in both. statsmodels b_hs = {b["mom_hs"]} [CI {K["both_ci"]["mom_hs"][0]}, {K["both_ci"]["mom_hs"][1]}];
PyMC b_hs = {kb["b_hs"]["mean"]} [{kb["b_hs"]["ci"][0]}, {kb["b_hs"]["ci"][1]}].
The PyMC version makes every assumption visible, including the priors.
""",
    )
    code(
        s,
        LEFT,
        TOP,
        6.0,
        1.1,
        """
smf.ols("kid_score ~ mom_hs + mom_iq_c",
        data=kid).fit()""",
        size=13,
        title="statsmodels",
    )
    code(
        s,
        LEFT,
        TOP + 1.3,
        6.0,
        3.7,
        """
with pm.Model():
    intercept = pm.Normal("intercept", mu=80, sigma=20)
    b_hs = pm.Normal("b_hs", mu=0, sigma=10)
    b_iq = pm.Normal("b_iq", mu=0, sigma=1)
    sigma = pm.HalfNormal("sigma", sigma=20)

    mu = (intercept + b_hs * kid["mom_hs"]
          + b_iq * kid["mom_iq_c"])
    pm.Normal("kid_score", mu=mu, sigma=sigma,
              observed=kid["kid_score"])
    idata = pm.sample()""",
        size=13,
        title="PyMC",
    )
    image(s, "b3_forest", 6.75, TOP, 6.1, 4.9)

    it = K["interaction"]
    s = d.slide(
        title="Teaser: interactions",
        tag="freq",
        subtitle="What if the IQ slope differs between the two groups?",
        notes=f"""
Adding mom_hs × mom_iq_c lets each group have its own slope:
{it["mom_iq_c"]} without high school, {it["mom_iq_c"] + it["mom_hs:mom_iq_c"]:.2f} with.
Interpreting interactions takes care - a topic for a later session.
""",
    )
    image(s, "eq_interaction", LEFT, 1.6, 6.6, 0.55)
    text(
        s,
        LEFT,
        TOP + 0.6,
        4.8,
        4.3,
        [
            "Add the product `mom_hs × mom_iq_c`",
            "Each group gets **its own slope**: the lines are no longer parallel",
            "Coefficients get harder to read: **next session**",
        ],
        size=18,
        bullets=True,
        spacing=12,
    )
    image(s, "b3_interaction", 5.47, TOP + 0.3, 7.4 * 0.94, 5.0 * 0.94)

    handson_slide(
        d,
        3,
        "Multiple predictors",
        [
            "Fit `kid_score ~ mom_hs` and interpret both coefficients.",
            "Center `mom_iq` and interpret the new intercept.",
            "Fit both predictors with `statsmodels` and `PyMC`; compare the results.",
            "Bonus: add an interaction and plot the two lines.",
        ],
        notes="Then the quiz.",
    )


def outro(d):
    s = d.slide(
        title="Quiz",
        subtitle="15 questions  ·  instant corrections",
        notes="""
Individual quiz, then a debrief. Ask for a show of hands on each block's questions to find
the hardest ones, and discuss those.
""",
    )
    image(s, "qr_quiz", 4.9, TOP + 0.1, 3.5, 3.5)
    hyperlink(
        s,
        2.0,
        TOP + 3.75,
        9.3,
        0.45,
        N["urls"]["quiz"],
        N["urls"]["quiz"],
        size=16,
        align=PP_ALIGN.CENTER,
    )
    text(
        s,
        2.0,
        TOP + 4.3,
        9.3,
        0.5,
        "Nothing is recorded: the quiz runs in your browser. Then we discuss the hardest questions.",
        size=14,
        color=S.GREY_MID,
        align=PP_ALIGN.CENTER,
    )

    s = d.slide(title="What we learned", notes="Revisit the learning goals.")
    items = [
        (
            "Drawing a line",
            S.GREY,
            "A line has an intercept, a slope and σ.\nLeast squares = maximum likelihood (with Normal errors).",
        ),
        (
            "How sure are we?",
            S.ROSE_DARK,
            "Frequentist: standard errors, confidence intervals, p-values.\n"
            "Bayesian: prior × likelihood → posterior; credible intervals and direct probabilities.",
        ),
        (
            "More than one predictor",
            S.SAGE_DARK,
            "A coefficient compares units that are equal on the other predictors.\n"
            "Centering makes the intercept meaningful.",
        ),
    ]
    for i, (t, c, body) in enumerate(items):
        x = LEFT + i * 4.17
        step(s, i + 1, x, TOP, t, w=3.95, size=18)
        card(s, x, TOP + 0.55, 3.95, 2.75, body, size=16)
    callout(
        s,
        LEFT,
        TOP + 3.6,
        12.4,
        1.2,
        "Same model, two readings. **Frequentist**: what would happen over repeated "
        "samples. **Bayesian**: what is plausible given the data and the prior. "
        "With weak priors and enough data, the numbers agree.",
        accent=S.GREY,
        size=16,
    )

    s = d.slide(
        title="Where to go next",
        notes="Point to the references and to the next session.",
    )
    refs = [
        "**Gelman, Hill & Vehtari (2020).** *Regression and Other Stories.* Cambridge "
        "University Press. Free PDF at avehtari.github.io/ROS-Examples",
        "**McElreath (2020).** *Statistical Rethinking* (2nd ed.). CRC Press. Lectures on YouTube.",
        "**PyMC example gallery**: pymc.io/projects/examples",
        '**Bambi**: formula syntax for Bayesian models, `bmb.Model("y ~ x", df)`',
        "**Next session**: model checking, prediction and interactions",
    ]
    text(s, LEFT, TOP, 12.4, 4.5, refs, size=18, bullets=True, spacing=16)
    text(
        s,
        LEFT,
        6.3,
        12.4,
        0.65,
        "Thank you!",
        size=28,
        bold=True,
        color=S.ROSE_DARK,
        spacing=0,
    )


def appendix(d):
    section_slide(
        d,
        "A",
        "Appendix",
        "A few formulas for the curious",
        """
Optional material, not presented in class.
""",
    )
    s = d.slide(
        title="Least squares in closed form",
        tag="freq",
        subtitle="Setting the derivatives of RSS to zero gives a formula for a and b",
        notes="Derivation: d RSS / d a = 0 and d RSS / d b = 0 (normal equations).",
    )
    image(s, "eq_rss", LEFT, TOP, 6.0, 0.7)
    image(s, "eq_ols_closed", LEFT, TOP + 1.1, 9.0, 1.25)
    text(
        s,
        LEFT,
        TOP + 2.7,
        12.0,
        0.5,
        "With several predictors, in matrix form:",
        size=18,
    )
    image(s, "eq_ols_matrix", LEFT, TOP + 3.25, 4.5, 0.65)

    s = d.slide(
        title="OLS = maximum likelihood",
        tag="freq",
        subtitle="With Normal errors, the log-likelihood is a shifted, scaled −RSS",
        notes="For any fixed σ, the (a, b) that maximise the log-likelihood are those that minimise RSS.",
    )
    image(s, "eq_likelihood", LEFT, TOP, 8.0, 0.75)
    image(s, "eq_loglik", LEFT, TOP + 1.2, 10.0, 0.95)
    text(
        s,
        LEFT,
        TOP + 2.6,
        12.0,
        1.5,
        [
            "For any fixed σ, maximising the log-likelihood over (a, b) = minimising RSS",
            "The maximum-likelihood σ is √(RSS / n); statsmodels reports √(RSS / (n − 2))",
        ],
        size=18,
        bullets=True,
        spacing=12,
    )

    s = d.slide(
        title="Priors as regularisation",
        tag="bayes",
        subtitle="A Normal(0, τ) prior on b adds a penalty to least squares",
        notes="The posterior mode (MAP) with a Normal prior on b is the ridge-regression estimate with λ = σ²/τ².",
    )
    image(s, "eq_ridge", LEFT, TOP, 10.0, 0.95)
    text(
        s,
        LEFT,
        TOP + 1.4,
        12.0,
        2.0,
        [
            "The most probable (a, b) under this posterior is the **ridge regression** estimate",
            "Strong prior (small τ) = big penalty: the slope is pulled towards 0",
            "Weak prior (large τ) = tiny penalty: back to least squares",
        ],
        size=18,
        bullets=True,
        spacing=12,
    )


def main():
    d = Deck()
    intro(d)
    block1(d)
    block2(d)
    block3(d)
    outro(d)
    appendix(d)
    d.save()


if __name__ == "__main__":
    main()
