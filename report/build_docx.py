"""Build an editable Word draft from REPORT.md with only stdlib + markdown-it-py.

Run: python3 report/build_docx.py
"""

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "REPORT.md"
TARGET = ROOT / "BackDown-draft.docx"
FIGURE = ROOT.parent / "figures" / "headline.png"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def run(text, *, bold=False, italic=False, code=False):
    props = []
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    if code:
        props.append('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>')
    return (f"<w:r><w:rPr>{''.join(props)}</w:rPr>"
            f'<w:t xml:space="preserve">{escape(text)}</w:t></w:r>')


def inline(children):
    bits = []
    bold = italic = code = False
    link = None
    for token in children or []:
        if token.type == "strong_open":
            bold = True
        elif token.type == "strong_close":
            bold = False
        elif token.type == "em_open":
            italic = True
        elif token.type == "em_close":
            italic = False
        elif token.type == "code_inline":
            bits.append(run(token.content, code=True))
        elif token.type == "link_open":
            link = token.attrGet("href")
        elif token.type == "link_close":
            if link:
                bits.append(run(f" ({link})"))
            link = None
        elif token.type in ("text", "html_inline"):
            bits.append(run(token.content, bold=bold, italic=italic, code=code))
        elif token.type == "softbreak":
            bits.append(run(" "))
        elif token.type == "hardbreak":
            bits.append("<w:r><w:br/></w:r>")
        elif token.type == "image":
            # The main Figure 1 is an embedded drawing, not a broken file link.
            bits.append(image_xml())
    return "".join(bits)


def paragraph(contents, style="Normal", *, keep_next=False):
    keep = "<w:keepNext/>" if keep_next else ""
    return (f"<w:p><w:pPr><w:pStyle w:val=\"{style}\"/>{keep}</w:pPr>"
            f"{contents}</w:p>")


def image_xml():
    # 6.15 × 4.61 inches, preserving the PNG's 4:3 aspect ratio.
    cx, cy = 5623560, 4217670
    return (
        "<w:r><w:drawing><wp:inline xmlns:wp=\"http://schemas.openxmlformats.org/"
        "drawingml/2006/wordprocessingDrawing\" distT=\"0\" distB=\"0\" distL=\"0\" distR=\"0\">"
        f"<wp:extent cx=\"{cx}\" cy=\"{cy}\"/>"
        "<wp:docPr id=\"1\" name=\"Figure 1: overselling and discrimination\"/>"
        "<a:graphic xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\">"
        "<a:graphicData uri=\"http://schemas.openxmlformats.org/drawingml/2006/picture\">"
        "<pic:pic xmlns:pic=\"http://schemas.openxmlformats.org/drawingml/2006/picture\">"
        "<pic:nvPicPr><pic:cNvPr id=\"0\" name=\"headline.png\"/><pic:cNvPicPr/></pic:nvPicPr>"
        f"<pic:blipFill><a:blip r:embed=\"rId2\" xmlns:r=\"{R}\"/>"
        "<a:stretch><a:fillRect/></a:stretch></pic:blipFill>"
        "<pic:spPr><a:xfrm><a:off x=\"0\" y=\"0\"/>"
        f"<a:ext cx=\"{cx}\" cy=\"{cy}\"/></a:xfrm>"
        "<a:prstGeom prst=\"rect\"><a:avLst/></a:prstGeom></pic:spPr>"
        "</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>"
    )


def table_xml(rows):
    columns = max(map(len, rows))
    grid = "".join("<w:gridCol w:w=\"{}\"/>".format(9360 // columns)
                   for _ in range(columns))
    cells = []
    for index, row in enumerate(rows):
        row_cells = []
        for cell in row:
            bg = '<w:shd w:fill="E8EDF3"/>' if index == 0 else ""
            row_cells.append(
                f"<w:tc><w:tcPr>{bg}</w:tcPr>"
                + paragraph(inline(cell), "TableText")
                + "</w:tc>")
        cells.append("<w:tr>" + "".join(row_cells) + "</w:tr>")
    return (
        '<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/>'
        '<w:tblW w:w="0" w:type="auto"/></w:tblPr>'
        f"<w:tblGrid>{grid}</w:tblGrid>{''.join(cells)}</w:tbl>"
    )


def document_body(markdown):
    tokens = MarkdownIt("commonmark").enable("table").parse(markdown)
    out = []
    current_table = None
    current_row = None
    list_depth = 0
    in_quote = False
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type == "table_open":
            current_table = []
        elif token.type == "table_close":
            out.append(table_xml(current_table))
            current_table = None
        elif token.type == "tr_open":
            current_row = []
        elif token.type == "tr_close":
            current_table.append(current_row)
        elif token.type in ("bullet_list_open", "ordered_list_open"):
            list_depth += 1
        elif token.type in ("bullet_list_close", "ordered_list_close"):
            list_depth -= 1
        elif token.type == "blockquote_open":
            in_quote = True
        elif token.type == "blockquote_close":
            in_quote = False
        elif token.type in ("heading_open", "paragraph_open", "list_item_open",
                            "th_open", "td_open") and i + 1 < len(tokens):
            next_token = tokens[i + 1]
            if next_token.type == "inline":
                if token.type in ("th_open", "td_open"):
                    current_row.append(next_token.children)
                elif token.type == "heading_open":
                    level = int(token.tag[1])
                    style = "Title" if level == 1 else ("Heading1" if level == 2
                                                       else "Heading2")
                    out.append(paragraph(inline(next_token.children), style,
                                         keep_next=True))
                elif token.type == "paragraph_open":
                    contents = inline(next_token.children)
                    if list_depth:
                        contents = run("• ") + contents
                    style = "Caption" if next_token.content.startswith(
                        ("**Figure ", "**Table ")) else ("Quote" if in_quote else "Normal")
                    out.append(paragraph(contents, style, keep_next=style == "Caption"))
        i += 1
    return "".join(out)


STYLES = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{W}">
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/>
<w:pPr><w:spacing w:after="110" w:line="252" w:lineRule="auto"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="20"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/>
<w:pPr><w:spacing w:after="220"/></w:pPr><w:rPr><w:b/><w:sz w:val="34"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>
<w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="200" w:after="95"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="25"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/>
<w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="155" w:after="75"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="22"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="Caption"/>
<w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="100"/></w:pPr>
<w:rPr><w:sz w:val="18"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/>
<w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="420"/></w:pPr>
<w:rPr><w:i/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="TableText"><w:name w:val="Table Text"/>
<w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="0"/></w:pPr>
<w:rPr><w:sz w:val="16"/></w:rPr></w:style>
<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/>
<w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4"/><w:left w:val="single" w:sz="4"/>
<w:bottom w:val="single" w:sz="4"/><w:right w:val="single" w:sz="4"/>
<w:insideH w:val="single" w:sz="4"/><w:insideV w:val="single" w:sz="4"/>
</w:tblBorders></w:tblPr></w:style></w:styles>"""


def build():
    body = document_body(SOURCE.read_text(encoding="utf-8"))
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W}" xmlns:r="{R}"><w:body>{body}'
        '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1080" w:right="1080" w:bottom="1080" w:left="1080"/>'
        '</w:sectPr></w:body></w:document>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="png" ContentType="image/png"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '</Types>'
    )
    relationships = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/></Relationships>'
    )
    doc_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId2" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
        'Target="media/headline.png"/>'
        '<Relationship Id="rId3" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/></Relationships>'
    )
    parts = {
        "[Content_Types].xml": content_types.encode(),
        "_rels/.rels": relationships.encode(),
        "word/document.xml": document.encode(),
        "word/styles.xml": STYLES.encode(),
        "word/_rels/document.xml.rels": doc_rels.encode(),
        "word/media/headline.png": FIGURE.read_bytes(),
    }
    with ZipFile(TARGET, "w", ZIP_DEFLATED) as output:
        for name, data in parts.items():
            output.writestr(name, data)
    print(TARGET)


if __name__ == "__main__":
    build()
