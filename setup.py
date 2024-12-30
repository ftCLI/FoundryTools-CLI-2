from pathlib import Path
from typing import List

import setuptools

this_directory = Path(__file__).parent
long_description = this_directory.joinpath("README.md").read_text(encoding="utf-8")


def _get_requirements() -> List[str]:
    """
    Relax hard pinning in setup.py
    """
    with open("requirements.txt", encoding="utf-8") as requirements:
        return [line.replace("==", ">=") for line in requirements.readlines()]


setuptools.setup(
    name="foundrytools-cli-2",
    version="2.0.0",
    description="A set of command line tools to inspect, manipulate and convert font files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ftCLI",
    author_email="ftcli@proton.me",
    url="https://github.com/ftCLI/FoundryTools-CLI-2",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["ft-cli = foundrytools_cli_2.__main__:cli"]},
    install_requires=_get_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    zip_safe=False,
)
