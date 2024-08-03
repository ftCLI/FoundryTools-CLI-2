# pylint: disable=import-outside-toplevel
import typing as t
from pathlib import Path

import click

from foundrytools_cli_2.cli.shared_options import base_options
from foundrytools_cli_2.cli.task_runner import TaskRunner

cli = click.Group(help="Fix font errors.")


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
    from foundrytools_cli_2.cli.fix.snippets.duplicate_components import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_ps = True
    runner.run()


@cli.command("notdef-empty")
@base_options()
def fix_empty_notdef(input_path: Path, **options: t.Dict[str, t.Any]) -> None:
    """
    Fixes the empty .notdef glyph by drawing a simple rectangle.

    Glyph 0 must be assigned to a .notdef glyph. The .notdef glyph is very important for providing
    the user feedback that a glyph is not found in the font. This glyph should not be left without
    an outline as the user will only see what looks like a space if a glyph is missing and not be
    aware of the active font’s limitation.
    """
    from foundrytools_cli_2.cli.fix.snippets.empty_notdef import fix_notdef_empty as task

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
    from foundrytools_cli_2.cli.fix.snippets.italic_angle import main as task

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
    from foundrytools_cli_2.cli.fix.snippets.legacy_accents import fix_legacy_accents as task

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
    from foundrytools_cli_2.cli.fix.snippets.monospace import main as task

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
    from foundrytools_cli_2.cli.fix.snippets.nbsp_missing import fix_missing_nbsp as task

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
    from foundrytools_cli_2.cli.fix.snippets.decompose_transformed import main as task

    runner = TaskRunner(input_path=input_path, task=task, **options)
    runner.filter.filter_out_ps = True
    runner.filter.filter_out_variable = True
    runner.run()
