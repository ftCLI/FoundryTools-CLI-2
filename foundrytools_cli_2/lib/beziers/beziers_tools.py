import typing as t

from beziers.path import BezierPath
from beziers.path.representations import Nodelist
from fontTools.misc.psCharStrings import T2CharString
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont


def handle_curve_nodes(pen: T2CharStringPen, nodes_list: Nodelist, i: int) -> int:
    """
    Handles the curve nodes in a BezierPath.

    Args:
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


def draw_bez(paths: t.List[BezierPath], pen: T2CharStringPen) -> None:
    """
    Draws a list of Bezier paths using a T2CharStringPen.

    Args:
        paths (list): The list of BezierPaths.
        pen (T2CharStringPen): The T2CharString pen to draw the paths.
    """
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
                i = handle_curve_nodes(pen, nodes_list, i)
            else:
                raise ValueError(f"Unknown node type: {node.type}")


def bez_to_charstring(paths: t.List[BezierPath], font: TTFont, glyph_name: str) -> T2CharString:
    """
    Converts a list of Bezier paths to a T2CharString.

    Args:
        paths (list): The list of Bezier paths.
        font (TTFont): The font.
        glyph_name (str): The name of the glyph.

    Returns:
        T2CharString: The T2CharString.
    """
    glyph_set = font.getGlyphSet()
    pen = T2CharStringPen(width=glyph_set[glyph_name].width, glyphSet=glyph_set)
    draw_bez(paths=paths, pen=pen)
    charstring = pen.getCharString()
    return charstring


def add_extremes(font: TTFont) -> t.Dict[str, T2CharString]:
    """
    Gets the charstrings of a font by converting the Bezier paths of each glyph to a T2CharString.

    Args:
        font (TTFont): The font.

    Returns:
        dict: A dictionary of the charstrings of each glyph.
    """
    glyph_set = font.getGlyphSet()
    charstrings = {}
    for k in glyph_set:
        bezier_paths: t.List[BezierPath] = BezierPath.fromFonttoolsGlyph(font, glyphname=k)
        for bp in bezier_paths:
            bp.addExtremes()
        charstring: T2CharString = bez_to_charstring(bezier_paths, font, glyph_name=k)
        charstrings[k] = charstring

    return charstrings
