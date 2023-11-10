import unittest
from io import BytesIO
from pathlib import Path

from fontTools.ttLib import TTFont, TTLibError

from foundrytools_cli_2.lib.font import Font

DATA_DIR = Path(__file__).parent.joinpath("test_data").resolve()

STATIC_OTF = DATA_DIR.joinpath("static.otf").resolve()
STATIC_TTF = DATA_DIR.joinpath("static.ttf").resolve()
STATIC_OTF_WOFF = DATA_DIR.joinpath("static.otf.woff").resolve()
STATIC_OTF_WOFF2 = DATA_DIR.joinpath("static.otf.woff2").resolve()
STATIC_TTF_WOFF = DATA_DIR.joinpath("static.ttf.woff").resolve()
STATIC_TTF_WOFF2 = DATA_DIR.joinpath("static.ttf.woff2").resolve()

VARIABLE_OTF = DATA_DIR.joinpath("variable.otf").resolve()
VARIABLE_TTF = DATA_DIR.joinpath("variable.ttf").resolve()
VARIABLE_OTF_WOFF = DATA_DIR.joinpath("variable.otf.woff").resolve()
VARIABLE_OTF_WOFF2 = DATA_DIR.joinpath("variable.otf.woff2").resolve()
VARIABLE_TTF_WOFF = DATA_DIR.joinpath("variable.ttf.woff").resolve()
VARIABLE_TTF_WOFF2 = DATA_DIR.joinpath("variable.ttf.woff2").resolve()


class TestFont(unittest.TestCase):
    #  can initialize a Font object with no arguments
    def test_initialize_font_with_no_arguments(self):
        font = Font()
        self.assertIsInstance(font, Font)
        self.assertIsInstance(font.ttfont, TTFont)
        self.assertIsInstance(font._bytesio, BytesIO)

    #  can initialize a Font object with a file path
    def test_initialize_font_with_file_path(self):
        font = Font(STATIC_OTF)
        self.assertIsInstance(font, Font)
        self.assertIsInstance(font.ttfont, TTFont)
        self.assertIsInstance(font.file, Path)
        self.assertTrue(font.is_ps and font.is_sfnt and font.is_static)
        self.assertFalse(font.is_variable or font.is_tt or font.is_woff or font.is_woff2)

    #  can initialize a Font object with a BytesIO object
    def test_initialize_font_with_bytesio_object(self):
        bytesio = BytesIO()
        tt_font = TTFont(STATIC_TTF)
        tt_font.save(bytesio)
        font = Font(bytesio)
        self.assertIsInstance(font, Font)

    #  can initialize a Font object with a TTFont object
    def test_initialize_font_with_ttfont_object(self):
        tt_font = TTFont(STATIC_TTF)
        font = Font(tt_font)
        self.assertIsInstance(font, Font)

    #  can initialize a Font object with an empty file
    def test_initialize_font_with_empty_file(self):
        font = Font()
        self.assertIsInstance(font, Font)

    #  can initialize a Font object with an invalid file path
    def test_initialize_font_with_invalid_file_path(self):
        with self.assertRaises(FileNotFoundError):
            Font("invalid_font.ttf")

    #  can initialize a Font object with an invalid BytesIO object
    def test_initialize_font_with_invalid_bytesio_object(self):
        bytesio = BytesIO(b"invalid_font_data")
        with self.assertRaises(TTLibError):
            Font(bytesio)

    def test_returns_font_instance(self):
        font_path = STATIC_TTF
        with Font(font_path) as font:
            self.assertIsInstance(font, Font)

    def test_save_to_file(self):
        import tempfile

        font_path = STATIC_TTF
        font = Font(source=font_path)
        with tempfile.NamedTemporaryFile(suffix=".ttf", mode="wb") as temp_file:
            font.save_to_file(file=temp_file)

    # can get the real extension of a Font.tt_font object
    def test_get_real_extension(self):
        font = Font(STATIC_OTF)
        self.assertEqual(font.real_extension, ".otf")
        font = Font(STATIC_TTF)
        self.assertEqual(font.real_extension, ".ttf")
        font = Font(STATIC_OTF_WOFF)
        self.assertEqual(font.real_extension, ".woff")
        font = Font(STATIC_OTF_WOFF2)
        self.assertEqual(font.real_extension, ".woff2")
        font = Font(STATIC_TTF_WOFF)
        self.assertEqual(font.real_extension, ".woff")
        font = Font(STATIC_TTF_WOFF2)
        self.assertEqual(font.real_extension, ".woff2")
        font = Font(VARIABLE_OTF)
        self.assertEqual(font.real_extension, ".otf")
        font = Font(VARIABLE_TTF)
        self.assertEqual(font.real_extension, ".ttf")
        font = Font(VARIABLE_OTF_WOFF)
        self.assertEqual(font.real_extension, ".woff")
        font = Font(VARIABLE_OTF_WOFF2)
        self.assertEqual(font.real_extension, ".woff2")
        font = Font(VARIABLE_TTF_WOFF)
        self.assertEqual(font.real_extension, ".woff")
        font = Font(VARIABLE_TTF_WOFF2)
        self.assertEqual(font.real_extension, ".woff2")
