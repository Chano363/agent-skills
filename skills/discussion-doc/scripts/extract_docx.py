# -*- coding: utf-8 -*-
"""提取 docx 全文（段落+表格+OMML 公式转 LaTeX+图片）转存 md。

用法:
    python extract_docx.py <src.docx> <dst.md> [assets_dir]

- assets_dir 缺省为 <dst 所在目录>/<dst 文件名>.assets
- 依赖: python-docx, dwml (pip install python-docx dwml)
- 图片以相对路径 <assets 目录名>/imageN.ext 引用
"""
import os
import sys

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn
from dwml.omml import oMath2Latex

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def omath_to_latex(el):
    try:
        return str(oMath2Latex(el))
    except Exception:
        return "".join(t.text or "" for t in el.iter(M + "t"))


def has_ancestor(node, tag):
    p = node.getparent()
    while p is not None:
        if p.tag == tag:
            return True
        p = p.getparent()
    return False


def para_content_md(p, doc_part, img_count, asset_dir, asset_rel):
    """按文档顺序拼段落内容：文本 + 行内/显示公式 + 图片。"""
    parts = []
    for node in p._p.iter():
        tag = node.tag
        if tag == M + "oMathPara":
            om = node.find(M + "oMath")
            latex = omath_to_latex(om) if om is not None else ""
            parts.append(f"$${latex}$$")
        elif tag == M + "oMath":
            if has_ancestor(node, M + "oMathPara"):
                continue
            parts.append(f"${omath_to_latex(node)}$")
        elif tag == W + "t":
            if has_ancestor(node, M + "oMath") or has_ancestor(node, M + "oMathPara"):
                continue
            parts.append(node.text or "")
        elif tag == W + "tab":
            parts.append(" ")
        elif tag == A + "blip":
            rid = node.get(R + "embed")
            if rid and rid in doc_part.related_parts:
                img_count[0] += 1
                img = doc_part.related_parts[rid]
                ext = os.path.splitext(img.partname)[1] or ".png"
                os.makedirs(asset_dir, exist_ok=True)
                fname = f"image{img_count[0]}{ext}"
                with open(os.path.join(asset_dir, fname), "wb") as f:
                    f.write(img.blob)
                parts.append(f"![]({asset_rel}/{fname})")
    return "".join(parts).strip()


def para_md(p, doc_part, img_count, asset_dir, asset_rel):
    text = para_content_md(p, doc_part, img_count, asset_dir, asset_rel)
    if not text:
        return ""
    style = (p.style.name or "").lower()
    for lvl, keys in [(4, ("heading 4", "标题 4")), (3, ("heading 3", "标题 3")),
                      (2, ("heading 2", "标题 2")), (1, ("heading 1", "标题 1"))]:
        if any(k in style for k in keys):
            return "#" * lvl + " " + text
    ppr = p._p.find(qn("w:pPr"))
    if ppr is not None and ppr.find(qn("w:numPr")) is not None:
        return f"- {text}"
    return text


def table_md(t, doc_part, img_count, asset_dir, asset_rel):
    rows = []
    for row in t.rows:
        cells = []
        for c in row.cells:
            segs = [para_content_md(cp, doc_part, img_count, asset_dir, asset_rel) for cp in c.paragraphs]
            cells.append(" ".join(s for s in segs if s).replace("|", "\\|"))
        rows.append(cells)
    if not rows:
        return ""
    ncol = max(len(r) for r in rows)
    pad = lambda r: r + [""] * (ncol - len(r))  # noqa: E731
    lines = ["| " + " | ".join(pad(rows[0])) + " |", "|" + "---|" * ncol]
    for r in rows[1:]:
        lines.append("| " + " | ".join(pad(r)) + " |")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    asset_dir = sys.argv[3] if len(sys.argv) > 3 else os.path.splitext(dst)[0] + ".assets"
    asset_rel = os.path.basename(asset_dir)

    doc = Document(src)
    img_count = [0]
    out = []
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            out.append(para_md(Paragraph(child, doc), doc.part, img_count, asset_dir, asset_rel))
        elif child.tag == qn("w:tbl"):
            out.append(table_md(Table(child, doc), doc.part, img_count, asset_dir, asset_rel))

    md = "\n\n".join(x for x in out if x.strip()) + "\n"
    with open(dst, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"OK -> {dst} ({len(md)} chars, {img_count[0]} images -> {asset_dir})")


if __name__ == "__main__":
    main()
