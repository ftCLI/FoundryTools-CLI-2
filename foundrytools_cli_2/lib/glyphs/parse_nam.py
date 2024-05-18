import itertools
import json
import typing as t
from pathlib import Path

NAM_FILE = "standard.nam"
NAMES_FILE = "names.json"
UNICODES_FILE = "unicodes.json"

"""
- names without prefix are used as production, friendly and alternative names
- names with `>` prefix are used as friendly and alternative names
- names with `<` prefix are used as alternative names
- names with `!` prefix are used as synonyms
"""


def get_unicodes_and_names(
        nam_file: Path
) -> t.Tuple[t.Dict[str, t.Dict[str, t.List[str]]], t.Dict[str, str]]:
    """
    Parses the NAM file and returns a dictionary with the unicode code points as keys and a
    dictionary with the names as values.
    """
    unicodes_dict: t.Dict[str, t.Dict[str, t.List[str]]] = {}
    names_dict: t.Dict[str, str] = {}

    with open(nam_file, encoding="utf-8") as f:
        lines = itertools.islice(f, 3, None)  # skip the first 3 lines
        for line in lines:
            if line.startswith("%"):
                continue
            unicode, name = line.strip().split(" ", 1)  # Separate the unicode and the name
            name = name.strip()

            name_type = "production"
            if name.startswith("!"):
                name = name[1:]  # removing '!' prefix
                name_type = "synonym"
            elif name.startswith(">"):
                name = name[1:]  # removing '>' prefix
                name_type = "friendly"
            elif name.startswith("<"):
                name = name[1:]  # removing '<' prefix
                name_type = "alternative"

            if unicode not in unicodes_dict:
                unicodes_dict[unicode] = {
                    "production": [],
                    "friendly": [],
                    "alternative": [],
                    "synonym": [],
                }

            unicodes_dict[unicode][name_type].append(name)
            names_dict[name] = unicode

    for k, v in unicodes_dict.items():
        if not v["production"]:
            if int(k, 16) > 0xFFFF:
                prefix = "u"
            else:
                prefix = "uni"
            production_name = k.replace('0x', prefix)

            v["production"] = [production_name]
            names_dict[production_name] = k

    return unicodes_dict, names_dict


if __name__ == "__main__":
    unicodes, names = get_unicodes_and_names(Path(NAM_FILE))
    with open(NAMES_FILE, "w", encoding="utf-8") as j:
        json.dump(names, j, indent=4)
    with open(UNICODES_FILE, "w", encoding="utf-8") as j:
        json.dump(unicodes, j, indent=4)
