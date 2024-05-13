import itertools
import json
import typing as t

NAM_FILE = "standard.nam"

"""
- names without prefix are used as production, friendly and alternative names
- names with `>` prefix are used as friendly and alternative names
- names with `<` prefix are used as alternative names
- names with `!` prefix are used as synonyms
"""


def get_names_unicodes(file: str) -> t.Dict[str, int]:
    names_unicodes = {}

    with open(file, encoding="utf-8") as f:
        for line in f.readlines():
            if line.startswith("%"):
                continue
            unicode, name = line.strip().split(" ", 1)
            name = name.strip()
            unicode = int(unicode.replace("0x", ""), 16)

            if name.startswith("!"):
                name = name[1:]
            elif name.startswith(">"):
                name = name[1:]
            elif name.startswith("<"):
                name = name[1:]

            names_unicodes[name] = unicode

    return names_unicodes


def get_unicodes_names(file: str) -> t.Dict[str, t.Dict[str, t.List[str]]]:
    """
    Parses the NAM file and returns a dictionary with the unicode code points as keys and a
    dictionary with the names as values.
    """
    parsed_names: t.Dict[str, t.Dict[str, t.List[str]]] = {}
    with open(file, encoding="utf-8") as f:
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

            if unicode not in parsed_names:
                parsed_names[unicode] = {
                    "production": [],
                    "friendly": [],
                    "alternative": [],
                    "synonym": [],
                }

            parsed_names[unicode][name_type].append(name)

    for k, v in parsed_names.items():
        if not v["production"]:
            if int(k, 16) > 0xFFFF:
                v["production"] = [f"u{k.replace('0x', '')}"]
            else:
                v["production"] = [f"uni{k.replace('0x', '')}"]

    return parsed_names


if __name__ == "__main__":
    print(get_unicodes_names(NAM_FILE)["0x04BB"])
    print(get_names_unicodes(NAM_FILE)["space"])

    names_unicodes = get_names_unicodes(NAM_FILE)
    with open("../../data/names_unicodes.json", "w", encoding="utf-8") as j:
        json.dump(names_unicodes, j, indent=4)

    unicodes_names = get_unicodes_names(NAM_FILE)
    with open("../../data/unicodes_names.json", "w", encoding="utf-8") as j:
        json.dump(unicodes_names, j, indent=4)
