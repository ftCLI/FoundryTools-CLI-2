# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click
from fontTools.misc.roundTools import otRound

from foundrytools_cli_2.cli.fix.options import (
    ignore_errors_flag,
    keep_hinting_flag,
    keep_unused_subroutines_flag,
    min_area_option,
)
from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.cli.task_runner import TaskRunner
from foundrytools_cli_2.lib.tables import HeadTable

cli = click.Group(help="Fix font errors.")


@cli.command("contours")
@min_area_option()
@keep_hinting_flag()
@ignore_errors_flag()
@keep_unused_subroutines_flag()
@base_options()
def fix_contours(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Correct contours of the given fonts by removing overlaps, correcting the direction of the
    contours, and removing tiny paths.

    Fixing procedure:

    * Remove overlaps in the contours of the glyphs.
    * Correct the direction of the contours.
    * Remove tiny paths.
    """
    from foundrytools_cli_2.cli.fix.tasks.contours import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("duplicate-components")
@base_options()
def fix_duplicate_components(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Remove duplicate components.

    fontbakery check id: com.google.fonts/check/glyf_non_transformed_duplicate_components

    Rationale:

    There have been cases in which fonts had faulty double quote marks, with each of them
    containing two single quote marks as components with the same x, y coordinates which makes
    them visually look like single quote marks.

    This check ensures that glyphs do not contain duplicate components which have the same x,
    y coordinates.

    Fixing procedure:

    * Remove duplicate components which have the same x,y coordinates.
    """
    from foundrytools_cli_2.cli.fix.tasks.duplicate_components import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_ps = True
    runner.run()


@cli.command("empty-notdef")
@base_options()
def fix_empty_notdef(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Fixes the empty .notdef glyph by drawing a simple rectangle.

    Glyph 0 must be assigned to a .notdef glyph. The .notdef glyph is very important for providing
    the user feedback that a glyph is not found in the font. This glyph should not be left without
    an outline as the user will only see what looks like a space if a glyph is missing and not be
    aware of the active font’s limitation.
    """
    from foundrytools_cli_2.cli.fix.tasks.empty_notdef import fix_empty_notdef as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("fs-selection")
@base_options()
def fix_fs_selection(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Fixes the style flags (Regular, Italic, Bold) in the ``OS/2.fsSelection`` field and in the
    ``head.macStyle`` field.

    fontbakery check id: com.google.fonts/check/fsselection>

    The ``OS/2.fsSelection`` field is a bit field used to specify the stylistic qualities of the
    font - in particular, it specifies to some operating systems whether the font is italic (bit 0),
    bold (bit 5) or regular (bit 6).

    This fix verifies that the ``fsSelection`` field is set correctly for the font style. If the
    font is not bold or italic, the regular bit is set. If the font is bold or italic, the regular
    bit is cleared.
    """
    from foundrytools_cli_2.cli.fix.tasks.fs_selection import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("kern-table")
@base_options()
def fix_kern_table(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Fix the ``kern`` table by removing pairs that contain unmapped glyphs.

    fontbakery check id: com.google.fonts/check/kern_table

    Rationale:

    Even though all fonts should have their kerning implemented in the ``GPOS`` table, there may
    be kerning info at the ``kern`` table as well.

    Some applications such as MS PowerPoint require kerning info on the kern table. More
    specifically, they require a format 0 kern subtable from a kern table version 0 with only
    glyphs defined in the ``cmap`` table, which is the only one that Windows understands (and
    which is also the simplest and more limited of all the kern subtables).

    Google Fonts ingests fonts made for download and use on desktops, and does all web font
    optimizations in the serving pipeline (using libre libraries that anyone can replicate.)

    Ideally, TTFs intended for desktop users (and thus the ones intended for Google Fonts) should
    have both ``kern`` and ``GPOS`` tables.

    Given all of the above, we currently treat kerning on a v0 ``kern`` table as a good-to-have (
    but optional) feature.

    \b
    * Original proposal: legacy:check/066
    * See also: https://github.com/fonttools/fontbakery/issues/1675
    * See also: https://github.com/fonttools/fontbakery/issues/3148

    Fixing procedure:

    * Remove glyphs that are not defined in the ``cmap`` table from the ``kern`` table.
    """
    from foundrytools_cli_2.cli.fix.tasks.kern_table import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("italic-angle")
@click.option(
    "--min-slant",
    type=float,
    default=2.0,
    show_default=True,
    help="The minimum slant to consider a font italic.",
)
@click.option(
    "--mode",
    type=click.IntRange(1, 3),
    default=1,
    show_default=True,
    help="""Which attributes to set when the calculated italic angle is not 0.

\b
1: Only set the italic bits.
2: Only set the oblique bit.
3: Set the italic and oblique bits.
\n
""",
)
@base_options()
def fix_italic_angle(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Fixes the italic angle and related attributes in the font.

    The italic angle is recalculated as first step.

    The italic and oblique bits are then set based on the calculated italic angle and the provided
    mode.
    """
    from foundrytools_cli_2.cli.fix.tasks.italic_angle import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("legacy-accents")
@base_options()
def fix_legacy_accents(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Check that legacy accents aren't used in composite glyphs.

    fontbakery check id: com.google.fonts/check/legacy_accents

    Rationale:

    Legacy accents should not have anchors and should have positive width. They are often used
    independently of a letter, either as a placeholder for an expected combined mark+letter
    combination in macOS, or separately. For instance, U+00B4 (ACUTE ACCENT) is often mistakenly
    used as an apostrophe, U+0060 (GRAVE ACCENT) is used in Markdown to notify code blocks, and ^ is
    used as an exponential operator in maths.

    More info: https://github.com/googlefonts/fontbakery/issues/4310
    """
    from foundrytools_cli_2.cli.fix.tasks.legacy_accents import fix_legacy_accents as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("nbsp-missing")
@base_options()
def fix_missing_nbsp(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Fixes the missing non-breaking space glyph by double mapping the space glyph.

    fontbakery check id: com.google.fonts/check/whitespace_glyphs

    Rationale:

    Font contains glyphs for whitespace characters?

    Fixing procedure:

    * Add a glyph for the missing ``nbspace`` character by double mapping the ``space`` character
    """
    from foundrytools_cli_2.cli.fix.tasks.nbsp_missing import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("nbsp-width")
@base_options()
def fix_nbsp_width(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Fixes the width of the non-breaking space glyph to be the same as the space glyph.

    fontbakery check id: com.google.fonts/check/whitespace_widths

    Rationale:

    If the ``space`` and ``nbspace`` glyphs have different widths, then Google Workspace has
    problems with the font.

    The ``nbspace`` is used to replace the space character in multiple situations in documents;
    such as the space before punctuation in languages that do that. It avoids the punctuation to
    be separated from the last word and go to next line.

    This is automatic substitution by the text editors, not by fonts. It's also used by designers
    in text composition practice to create nicely shaped paragraphs. If the ``space`` and the
    ``nbspace`` are not the same width, it breaks the text composition of documents.

    Fixing procedure:

    * Check if ``nbspace`` and space glyphs have the same width. If not, correct ``nbspace``
    width to match the ``space`` width.
    """
    from foundrytools_cli_2.cli.fix.tasks.nbsp_width import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("monospace")
@base_options()
def fix_monospace(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Fix metadata in monospaced fonts

    fontbakery check id: com.google.fonts/check/monospace

    Rationale:

    There are various metadata in the OpenType spec to specify if a font is monospaced or not. If
        the font is not truly monospaced, then no monospaced metadata should be set (as sometimes
        they mistakenly are...)

    Requirements for monospace fonts:

    * ``post.isFixedPitch`` - "Set to 0 if the font is proportionally spaced, non-zero if the font
    is not proportionally paced (monospaced)" (https://www.microsoft.com/typography/otspec/post.htm)

    * ``hhea.advanceWidthMax`` must be correct, meaning no glyph's width value is greater.
    (https://www.microsoft.com/typography/otspec/hhea.htm)

    * ``OS/2.panose.bProportion`` must be set to 9 (monospace) on latin text fonts.

    * ``OS/2.panose.bSpacing`` must be set to 3 (monospace) on latin handwritten or latin symbol
    fonts.

    * Spec says: "The PANOSE definition contains ten digits each of which currently describes up to
    sixteen variations. Windows uses ``bFamilyType``, ``bSerifStyle`` and ``bProportion`` in the
    font mapper to determine family type. It also uses ``bProportion`` to determine if the font is
    monospaced."
    (https://www.microsoft.com/typography/otspec/os2.htm#pan,
    https://monotypecom-test.monotype.de/services/pan2)

    * ``OS/2.xAvgCharWidth`` must be set accurately. "OS/2.xAvgCharWidth is used when rendering
    monospaced fonts, at least by Windows GDI"
    (https://typedrawers.com/discussion/comment/15397/#Comment_15397)

    * ``CFF.cff.TopDictIndex[0].isFixedPitch`` must be set to ``True`` for CFF fonts.

    Fixing procedure:

    If the font is monospaced, then:

    * Set ``post.isFixedPitch`` to ``True`` (1)

    * Correct the ``hhea.advanceWidthMax`` value

    * Set the ``OS/2.panose.bProportion`` value to 9 or 3, according to the
    ``OS/2.panose.bFamilyType`` value

    * Set ``CFF.cff.TopDictIndex[0].isFixedPitch`` to ``True`` for CFF fonts
    """
    from foundrytools_cli_2.cli.fix.tasks.monospace import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("transformed-components")
@base_options()
def fix_transformed_components(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Decompose glyphs with transformed components.

    fontbakery check id: com.google.fonts/check/transformed_components

    Rationale:

    Some families have glyphs which have been constructed by using transformed components e.g.
    the 'u' being constructed from a flipped 'n'.

    From a designers point of view, this sounds like a win (less work). However, such approaches
    can lead to rasterization issues, such as having the 'u' not sitting on the baseline at
    certain sizes after running the font through ttfautohint.

    Other issues are outlines that end up reversed when only one dimension is flipped while the
    other isn't.

    As of July 2019, Marc Foley observed that ttfautohint assigns cvt values to transformed
    glyphs as if they are not transformed and the result is they render very badly, and that
    vttLib does not support flipped components.

    When building the font with fontmake, the problem can be fixed by adding this to the command
    line:

    ``--filter DecomposeTransformedComponentsFilter``

    Fixing procedure:

    * Decompose composite glyphs that have transformed components.
    """
    from foundrytools_cli_2.cli.fix.tasks.decompose_transformed import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_ps = True
    runner.filter.filter_out_variable = True
    runner.run()


@cli.command("unreachable-glyphs")
@base_options()
def fix_unreachable_glyphs(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Remove unreachable glyphs from the font.

    fontbakery check id: com.google.fonts/check/unreachable_glyphs

    Rationale:

    Glyphs are either accessible directly through Unicode codepoints or through substitution rules.

    In Color Fonts, glyphs are also referenced by the COLR table. And mathematical fonts also
    reference glyphs via the MATH table.

    Any glyphs not accessible by these means are redundant and serve only to increase the font's
    file size.

    More info: https://github.com/fonttools/fontbakery/issues/3160

    Fixing procedure:

    * Remove glyphs that are not reachable by subsetting the font.
    """
    from foundrytools_cli_2.cli.fix.tasks.unreachable_glyphs import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()


@cli.command("vertical-metrics")
@base_options()
def fix_vertical_metrics(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Ensures that the vertical metrics are consistent across the font family.

    This task calculates the minimum y_min and maximum y_max values from the head table of all
    fonts in the family and sets the vertical metrics accordingly.

    Args:
        input_path (Path): The path to the input font file.
        options (Dict[str, Any]): Additional options for the task runner.

    Raises:
        ClickException: If no fonts are found in the specified path.
    """
    from foundrytools_cli_2.lib.cli_tools.font_finder import FontFinder

    fonts = FontFinder(input_path).find_fonts()
    if not fonts:
        raise click.ClickException("No fonts found.")

    metrics = []
    for font in fonts:
        table_head = HeadTable(font.ttfont)
        metrics.append((table_head.y_min, table_head.y_max))

    # Calculate the minimum y_min and maximum y_max values
    safe_bottom = otRound(min(m[0] for m in metrics))
    safe_top = otRound(max(m[1] for m in metrics))

    options["safe_bottom"] = t.cast(t.Any, safe_bottom)
    options["safe_top"] = t.cast(t.Any, safe_top)

    from foundrytools_cli_2.cli.fix.tasks.vertical_metrics import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.run()
