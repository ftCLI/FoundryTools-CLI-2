from typing import List
from beziers.path import BezierPath
from fontTools.misc.psCharStrings import T2CharString
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen


def handle_curve(pen: T2CharStringPen, nodes_list: list, i: int) -> int:
    curve_points = []
    while i < len(nodes_list) and nodes_list[i].type in {"offcurve", "curve"}:
        curve_points.append((nodes_list[i].x, nodes_list[i].y))
        if nodes_list[i].type == "curve":  # Curve node ends the sequence
            pen.curveTo(*curve_points)
            break
        i += 1
    return i + 1  # Ensure "curve" node is not processed again


def bezier_to_charstring(paths: List[BezierPath], font: TTFont, glyph_name: str) -> T2CharString:
    glyph_set = font.getGlyphSet()
    pen = T2CharStringPen(width=glyph_set[glyph_name].width, glyphSet=glyph_set)

    for path in paths:
        nodes_list = path.asNodelist()
        pen.moveTo((nodes_list[0].x, nodes_list[0].y))
        i = 1
        while i < len(nodes_list):
            node = nodes_list[i]
            if node.type == "move":
                pen.moveTo((node.x, node.y))
                i += 1
            elif node.type == "line":
                pen.lineTo((node.x, node.y))
                i += 1
            elif node.type in {"offcurve", "curve"}:
                i = handle_curve(pen, nodes_list, i)
            else:
                raise ValueError(f"Unknown node type: {node.type}")

    charstring = pen.getCharString()
    return charstring
