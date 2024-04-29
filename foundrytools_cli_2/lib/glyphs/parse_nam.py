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


def parse_nam(file: str) -> t.Dict[str, t.Dict[str, t.List[str]]]:
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
    print(parse_nam(NAM_FILE)["0x04BB"])

    names = parse_nam(NAM_FILE)
    with open("../../data/names.json", "w", encoding="utf-8") as j:
        json.dump(names, j, indent=4)
