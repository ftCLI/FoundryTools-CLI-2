import typing as t

import click

from foundrytools_cli_2.cli.shared_callbacks import choice_to_int_callback
from foundrytools_cli_2.cli.shared_options import add_options

__all__ = [
    "set_attrs_options",
    "set_fs_selection_options",
    "set_fs_type_options",
    "panose_options",
]


def weight_class() -> t.Callable:
    """
    Add the ``weight_class`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``weight_class`` option to a click command
    """
    _weight_class = [
        click.option(
            "-wght",
            "--weight-class",
            type=click.IntRange(1, 1000),
            help="""
            The new ``usWeightClass`` value.

            Indicates the visual weight (degree of blackness or thickness of strokes) of the
            characters in the font. Values from 1 to 1000 are valid.
            """,
        )
    ]
    return add_options(_weight_class)


def width_class() -> t.Callable:
    """
    Add the ``width_class`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``width_class`` option to a click command
    """
    _width_class = [
        click.option(
            "-wdth",
            "--width-class",
            type=click.IntRange(1, 9),
            help="""
            The new ``usWidthClass`` value.

            Indicates a relative change from the normal aspect ratio (width to height ratio) as
            specified by a font designer for the glyphs in a font.
            """,
        )
    ]
    return add_options(_width_class)


def vendor_id() -> t.Callable:
    """
    Add the ``vendor_id`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``vendor_id`` option to a click command
    """
    _vendor_id = [
        click.option(
            "-vid",
            "--vendor-id",
            type=click.STRING,
            help="""
            The new ``achVendID`` value.

            The four-character identifier for the vendor of the given type face.
            """,
        )
    ]
    return add_options(_vendor_id)


def typo_ascender() -> t.Callable:
    """
    Add the ``typo_ascender`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``typo_ascender`` option to a click command
    """
    _typo_ascender = [
        click.option(
            "-tasc",
            "--typo-ascender",
            type=click.INT,
            help="""
            The new ``sTypoAscender`` value.

            The typographic ascender of the font. This field should be combined with the
            ``sTypoDescender`` and ``sTypoLineGap`` values to determine default line spacing.
            """,
        )
    ]
    return add_options(_typo_ascender)


def typo_descender() -> t.Callable:
    """
    Add the ``typo_descender`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``typo_descender`` option to a click command
    """
    _typo_descender = [
        click.option(
            "-tdsc",
            "--typo-descender",
            type=click.INT,
            help="""
            The new ``sTypoDescender`` value.

            The typographic descender of the font. This field should be combined with the
            ``sTypoAscender`` and ``sTypoLineGap`` values to determine default line spacing.
            """,
        )
    ]
    return add_options(_typo_descender)


def typo_line_gap() -> t.Callable:
    """
    Add the ``typo_line_gap`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``typo_line_gap`` option to a click command
    """
    _typo_line_gap = [
        click.option(
            "-tlg",
            "--typo-line-gap",
            type=click.INT,
            help="""
            The new ``sTypoLineGap`` value.

            The typographic line gap of the font. This field should be combined with the
            ``sTypoAscender`` and ``sTypoDescender`` values to determine default line spacing.
            """,
        )
    ]
    return add_options(_typo_line_gap)


def win_ascent() -> t.Callable:
    """
    Add the ``win_ascent`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``win_ascent`` option to a click command
    """
    _win_ascent = [
        click.option(
            "-wasc",
            "--win-ascent",
            type=click.INT,
            help="""
            The new ``usWinAscent`` value.

            This field represents the “Windows ascender” metric. This should be used to specify the
            height above the baseline for a clipping region.
            """,
        )
    ]
    return add_options(_win_ascent)


def win_descent() -> t.Callable:
    """
    Add the ``win_descent`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``win_descent`` option to a click command
    """
    _win_descent = [
        click.option(
            "-wdsc",
            "--win-descent",
            type=click.INT,
            help="""
            The new ``usWinDescent`` value.

            This field represents the “Windows descender” metric. This should be used to specify the
            depth below the baseline for a clipping region.
            """,
        )
    ]
    return add_options(_win_descent)


def x_height() -> t.Callable:
    """
    Add the ``x_height`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``x_height`` option to a click command
    """
    _x_height = [
        click.option(
            "-xhgt",
            "--x-height",
            type=click.INT,
            help="""
            The new ``sxHeight`` value.

            This metric specifies the distance between the baseline and the approximate height of
            non-ascending lowercase letters measured in FUnits. This value would normally be
            specified by a type designer but in situations where that is not possible, for example
            when a legacy font is being converted, the value may be set equal to the top of the
            unscaled and unhinted glyph bounding box of the glyph encoded at U+0078 (LATIN SMALL
            LETTER X). If no glyph is encoded in this position the field should be set to 0.

            This metric, if specified, can be used in font substitution: the xHeight value of one
            font can be scaled to approximate the apparent size of another.

            This field was defined in version 2 of the ``OS/2`` table.
            """,
        )
    ]
    return add_options(_x_height)


def cap_height() -> t.Callable:
    """
    Add the ``cap_height`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``cap_height`` option to a click command
    """
    _cap_height = [
        click.option(
            "-chgt",
            "--cap-height",
            type=click.INT,
            help="""
            The new ``sCapHeight`` value.

            This metric specifies the distance between the baseline and the approximate height of
            uppercase letters measured in FUnits. This value would normally be specified by a type
            designer but in situations where that is not possible, for example when a legacy font
            is being converted, the value may be set equal to the top of the unscaled and unhinted
            glyph bounding box of the glyph encoded at U+0048 (LATIN CAPITAL LETTER H). If no glyph
            is encoded in this position the field should be set to 0.

            This metric, if specified, can be used in systems that specify type size by capital
            height measured in millimeters. It can also be used as an alignment metric; the top of a
            drop capital, for instance, can be aligned to the sCapHeight metric of the first line of
            text.

            This field was defined in version 2 of the ``OS/2`` table.
            """,
        )
    ]
    return add_options(_cap_height)


def italic() -> t.Callable:
    """
    Add the ``italic`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``italic`` option to a click command
    """
    _italic = [
        click.option(
            "-it/-no-it",
            "--italic/--no-italic",
            "italic",
            default=None,
            is_flag=True,
            help="""
            Sets or clears the ``OS/2.fsSelection`` bit 0 (ITALIC).

            The bit 1 of the ``macStyle`` field in the ``head`` table will be set to the same value
            as bit 0 in the fsSelection field of the ``OS/2`` table.
            """,
        )
    ]
    return add_options(_italic)


def underscore() -> t.Callable:
    """
    Add the ``underscore`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``underscore`` option to a click command
    """
    _underscore = [
        click.option(
            "-us/-no-us",
            "--underscore/--no-underscore",
            "underscore",
            default=None,
            is_flag=True,
            help="""
            Sets or clears the ``OS/2.fsSelection`` bit 1 (UNDERSCORE).

            Set to indicate that the font glyphs are underscored.
            """,
        )
    ]
    return add_options(_underscore)


def negative() -> t.Callable:
    """
    Add the ``negative`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``negative`` option to a click command
    """
    _negative = [
        click.option(
            "-ng/-no-ng",
            "--negative/--no-negative",
            "negative",
            default=None,
            is_flag=True,
            help="""
            Sets or clears the ``OS/2.fsSelection`` bit 2 (NEGATIVE).

            Set this bit when the font glyphs have their foreground and background reversed.
            """,
        )
    ]
    return add_options(_negative)


def outline() -> t.Callable:
    """
    Add the ``outline`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``outline`` option to a click command
    """
    _outline = [
        click.option(
            "-ol/-no-ol",
            "--outline/--no-outline",
            "outline",
            default=None,
            is_flag=True,
            help="""
            Sets or clears the ``OS/2.fsSelection`` bit 3 (OUTLINE).

            Set this bit when the font has outline glyphs.
            """,
        )
    ]
    return add_options(_outline)


def strikeout() -> t.Callable:
    """
    Add the ``strikeout`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``strikeout`` option to a click command
    """
    _strikeout = [
        click.option(
            "-so/-no-so",
            "--strikeout/--no-strikeout",
            "strikeout",
            default=None,
            is_flag=True,
            help="""
            Sets or clears the ``OS/2.fsSelection`` bit 4 (STRIKEOUT).

            Set this bit when the font has glyphs that are overstruck.
            """,
        )
    ]
    return add_options(_strikeout)


def bold() -> t.Callable:
    """
    Add the ``bold`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``bold`` option to a click command
    """
    _bold = [
        click.option(
            "-bd/-no-bd",
            "--bold/--no-bold",
            "bold",
            default=None,
            is_flag=True,
            help="""
            Sets or clears the ``OS/2.fsSelection`` bit 5 (BOLD).

            The bit 0 of the ``macStyle`` field in the ``head`` table will be set to the same value
            as ``fsSelection`` bit 5.
            """,
        )
    ]
    return add_options(_bold)


def regular() -> t.Callable:
    """
    Add the ``regular`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``regular`` option to a click command
    """
    _regular = [
        click.option(
            "-rg",
            "--regular",
            "regular",
            default=None,
            is_flag=True,
            help="""
            Sets the ``OS/2.fsSelection`` bit 6 (REGULAR).

            If bit 6 is set, then ``OS/2.fsSelection`` bits 0 and 5 will be cleared, as well as the
            ``macStyle`` bits 0 and 1 in the ``head`` table.
            """,
        )
    ]
    return add_options(_regular)


def use_typo_metrics() -> t.Callable:
    """
    Add the ``use_typo_metrics`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``use_typo_metrics`` option to a click command
    """
    _use_typo_metrics = [
        click.option(
            "-utm/-no-utm",
            "--use-typo-metrics/--no-use-typo-metrics",
            "use_typo_metrics",
            default=None,
            is_flag=True,
            help="""
            Sets or clears the ``OS/2.fsSelection`` bit 7 (USE_TYPO_METRICS).

            If set, it is strongly recommended that applications use ``OS/2.sTypoAscender -
            OS/2.sTypoDescender + OS/2.sTypoLineGap`` as the default line spacing for this font.

            Bit 7 was defined in version 4 of the ``OS/2`` table.
            """,
        )
    ]
    return add_options(_use_typo_metrics)


def wws_consistent() -> t.Callable:
    """
    Add the ``wws_consistent`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``wws_consistent`` option to a click command
    """
    _wws_consistent = [
        click.option(
            "-wws/-no-wws",
            "--wws-consistent/--no-wws-consistent",
            "wws_consistent",
            default=None,
            is_flag=True,
            help="""
            Sets or clears the ``OS/2.fsSelection`` bit 8 (WWS_CONSISTENT).

            If bit 8 is set, then ``name`` table strings for family and subfamily are provided that
            are consistent with a weight/width/slope family model without requiring the use of name
            IDs 21 or 22.

            Bit 8 was defined in version 4 of the ``OS/2`` table.
            """,
        )
    ]
    return add_options(_wws_consistent)


def oblique() -> t.Callable:
    """
    Add the ``oblique`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``oblique`` option to a click command
    """
    _oblique = [
        click.option(
            "-obl/-no-obl",
            "--oblique/--no-oblique",
            "oblique",
            default=None,
            is_flag=True,
            help="""
            Sets or clears the ``OS/2.fsSelection`` bit 9 (OBLIQUE).

            If bit 9 is set, then this font is to be considered an “oblique” style by processes
            which make a distinction between oblique and italic styles, such as Cascading Style
            Sheets font matching. For example, a font created by algorithmically slanting an upright
            face will set this bit.

            This bit, unlike the ITALIC bit (bit 0), is not related to style-linking in applications
            that assume a four-member font-family model comprised of regular, italic, bold and bold
            italic. It may be set or unset independently of the ITALIC bit. In most cases, if
            OBLIQUE is set, then ITALIC will also be set, though this is not required.

            Bit 9 was defined in version 4 of the ``OS/2`` table.
            """,
        )
    ]
    return add_options(_oblique)


def embed_level() -> t.Callable:
    """
    Add the ``embed_level`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``embed_level`` option to a click command
    """
    _embed_level = [
        click.option(
            "-el",
            "--embed-level",
            type=click.Choice(choices=["0", "2", "4", "8"]),
            callback=choice_to_int_callback,
            help="""
            Usage permissions. Valid fonts must set at most one of bits 1, 2 or 3; bit 0 is
            permanently reserved and must be zero. Valid values for this sub-field are 0, 2, 4 or 8.
            The meaning of these values is as follows:

            0: Installable embedding: the font may be embedded, and may be permanently installed for
            use on a remote systems, or for use by other users. The user of the remote system
            acquires the identical rights, obligations and licenses for that font as the original
            purchaser of the font, and is subject to the same end-user license agreement, copyright,
            design patent, and/or trademark as was the original purchaser.

            2: Restricted License embedding: the font must not be modified, embedded or exchanged in
            any manner without first obtaining explicit permission of the legal owner.

            4: Preview & Print embedding: the font may be embedded, and may be temporarily loaded on
            other systems for purposes of viewing or printing the document. Documents containing
            Preview & Print fonts must be opened “read-only”; no edits can be applied to the
            document.

            8: Editable embedding: the font may be embedded, and may be temporarily loaded on other
            systems. As with Preview & Print embedding, documents containing Editable fonts may be
            opened for reading. In addition, editing is permitted, including ability to format new
            text using the embedded font, and changes may be saved.
            """,
        )
    ]
    return add_options(_embed_level)


def no_subsetting() -> t.Callable:
    """
    Add the ``no_subsetting`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``no_subsetting`` option to a click command
    """
    _no_subsetting = [
        click.option(
            "-ns/-no-ns",
            "--no-subsetting/--subsetting",
            "no_subsetting",
            default=None,
            is_flag=True,
            help="""
            Sets or clears the ``OS/2.fsType`` bit 8 (NO_SUBSETTING).

            When this bit is set, the font may not be subsetted prior to embedding. Other embedding
            restrictions specified in bits 0 to 3 and bit 9 also apply.
            """,
        )
    ]
    return add_options(_no_subsetting)


def bitmap_embed_only() -> t.Callable:
    """
    Add the ``bitmap_embed_only`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``bitmap_embed_only`` option to a click command
    """
    _bitmap_embed_only = [
        click.option(
            "-beo/-no-beo",
            "--bitmap-embed-only/--no-bitmap-embed-only",
            "bitmap_embed_only",
            default=None,
            is_flag=True,
            help="""
            Sets or clears the ``OS/2.fsType`` bit 9 (BITMAP_EMBED_ONLY).

            When this bit is set, only bitmaps contained in the font may be embedded. No outline
            data may be embedded. If there are no bitmaps available in the font, then the font is
            considered unembeddable and the embedding services will fail. Other embedding
            restrictions specified in bits 0-3 and 8 also apply.
            """,
        )
    ]
    return add_options(_bitmap_embed_only)


def set_attrs_options() -> t.Callable:
    """
    Add the options for setting the attributes of the ``OS/2`` table to a click command.

    Returns:
        t.Callable: A decorator that adds the options to a click command
    """
    _set_attrs_options = [
        weight_class(),
        width_class(),
        vendor_id(),
        typo_ascender(),
        typo_descender(),
        typo_line_gap(),
        win_ascent(),
        win_descent(),
        panose_x_height(),
        cap_height(),
    ]
    return add_options(_set_attrs_options)


def set_fs_selection_options() -> t.Callable:
    """
    Add the options for setting the flags of the ``OS/2.fsSelection`` field to a click command.

    Returns:
        t.Callable: A decorator that adds the options to a click command
    """
    _set_flags_options = [
        italic(),
        underscore(),
        negative(),
        outline(),
        strikeout(),
        bold(),
        regular(),
        use_typo_metrics(),
        wws_consistent(),
        oblique(),
    ]
    return add_options(_set_flags_options)


def set_fs_type_options() -> t.Callable:
    """
    Add the options for setting the flags of the ``OS/2.fsType`` field to a click command.

    Returns:
        t.Callable: A decorator that adds the options to a click command
    """
    _set_permissions_options = [
        embed_level(),
        no_subsetting(),
        bitmap_embed_only(),
    ]
    return add_options(_set_permissions_options)


def family_type() -> t.Callable:
    """
    Add the ``family_type`` option to a click command.

    Returns:
        t.Callable: A decorator that adds the ``family_type`` option to a click command
    """
    _family_type = [
        click.option(
            "-ft",
            "--family-type",
            "bFamilyType",
            type=click.IntRange(0, 5),
            help="""
            Sets the 'bFamilyType' value.
            """,
        )
    ]
    return add_options(_family_type)


def serif_style() -> t.Callable:
    """
    Add the ``serif_style`` option to a click command.
    """
    _serif_style = [
        click.option(
            "-ss",
            "--serif-style",
            "bSerifStyle",
            type=click.IntRange(0, 15),
            help="""
            Sets the 'bSerifStyle' value.
            """,
        )
    ]
    return add_options(_serif_style)


def weight() -> t.Callable:
    """
    Add the ``weight`` option to a click command.
    """
    _weight = [
        click.option(
            "-wt",
            "--weight",
            "bWeight",
            type=click.IntRange(0, 11),
            help="""
            Sets the 'bWeight' value.
            """,
        )
    ]
    return add_options(_weight)


def proportion() -> t.Callable:
    """
    Add the ``proportion`` option to a click command.
    """
    _proportion = [
        click.option(
            "-pr",
            "--proportion",
            "bProportion",
            type=click.IntRange(0, 9),
            help="""
            Sets the 'bProportion' value.
            """,
        )
    ]
    return add_options(_proportion)


def contrast() -> t.Callable:
    """
    Add the ``contrast`` option to a click command.
    """
    _contrast = [
        click.option(
            "-ct",
            "--contrast",
            "bContrast",
            type=click.IntRange(0, 9),
            help="""
            Sets the 'bContrast' value.
            """,
        )
    ]
    return add_options(_contrast)


def stroke_variation() -> t.Callable:
    """
    Add the ``stroke_variation`` option to a click command.
    """
    _stroke_variation = [
        click.option(
            "-sv",
            "--stroke-variation",
            "bStrokeVariation",
            type=click.IntRange(0, 9),
            help="""
            Sets the 'bStrokeVariation' value.
            """,
        )
    ]
    return add_options(_stroke_variation)


def arm_style() -> t.Callable:
    """
    Add the ``arm_style`` option to a click command.
    """
    _arm_style = [
        click.option(
            "-as",
            "--arm-style",
            "bArmStyle",
            type=click.IntRange(0, 11),
            help="""
            Sets the 'bArmStyle' value.
            """,
        )
    ]
    return add_options(_arm_style)


def letter_form() -> t.Callable:
    """
    Add the ``letter_form`` option to a click command.
    """
    _letter_form = [
        click.option(
            "-lf",
            "--letter-form",
            "bLetterForm",
            type=click.IntRange(0, 15),
            help="""
            Sets the 'bLetterForm' value.
            """,
        )
    ]
    return add_options(_letter_form)


def midline() -> t.Callable:
    """
    Add the ``midline`` option to a click command.
    """
    _midline = [
        click.option(
            "-ml",
            "--midline",
            "bMidline",
            type=click.IntRange(0, 13),
            help="""
            Sets the 'bMidline' value.
            """,
        )
    ]
    return add_options(_midline)


def panose_x_height() -> t.Callable:
    """
    Add the ``panose_x_height`` option to a click command.
    """
    _x_height = [
        click.option(
            "-xh",
            "--x-height",
            "bXHeight",
            type=click.IntRange(0, 7),
            help="""
            Sets the 'bXHeight' value.
            """,
        )
    ]
    return add_options(_x_height)


def panose_options() -> t.Callable:
    """
    Add the Panose options to a click command.
    """
    _panose_options = [
        family_type(),
        serif_style(),
        weight(),
        proportion(),
        contrast(),
        stroke_variation(),
        arm_style(),
        letter_form(),
        midline(),
        panose_x_height(),
    ]
    return add_options(_panose_options)
