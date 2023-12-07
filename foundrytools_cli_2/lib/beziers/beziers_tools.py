import typing as t
from beziers.path import BezierPath
from fontTools.misc.psCharStrings import T2CharString
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen


def handle_curve(pen: T2CharStringPen, nodes_list: list, i: int) -> int:
    """
    Handles the curve nodes in a BezierPath.

    Parameters:
        pen (T2CharStringPen): The T2CharString pen to draw the curve.
        nodes_list (list): The list of nodes in the BezierPath.
        i (int): The starting index of the curve nodes.

    Returns:
        int: The index of the next node after the curve.

    """
    curve_points = []
    while i < len(nodes_list) and nodes_list[i].type in {"offcurve", "curve"}:
        curve_points.append((nodes_list[i].x, nodes_list[i].y))
        if nodes_list[i].type == "curve":  # Curve node ends the sequence
            pen.curveTo(*curve_points)
            break
        i += 1
    return i + 1  # Ensure "curve" node is not processed again


def bezier_to_charstring(paths: t.List[BezierPath], font: TTFont, glyph_name: str) -> T2CharString:
    """
    Converts a list of Bezier paths to a T2CharString.

    Parameters:
        paths (list): The list of Bezier paths.
        font (TTFont): The font.
        glyph_name (str): The name of the glyph.

    Returns:
        T2CharString: The T2CharString.

    Raises:
        ValueError: If an unknown node type is encountered.
    """
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
