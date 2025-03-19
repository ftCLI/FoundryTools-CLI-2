from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = this_directory.joinpath("README.md").read_text(encoding="utf-8")

REQUIREMENTS_FILE = this_directory.joinpath("requirements.txt")


def _get_requirements() -> list[str]:
    """
    Relax hard pinning in setup.py
    """
    with open(REQUIREMENTS_FILE, encoding="utf-8") as requirements:
        return [line.replace("==", ">=") for line in requirements.readlines()]


setuptools.setup(
    name="foundrytools-cli-ng",
    version="2.0.0",
    description="A set of command line tools to inspect, manipulate and convert font files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cesare Gilento",
    author_email="ftcli@proton.me",
    url="https://github.com/ftCLI/FoundryTools-CLI-2",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    entry_points={"console_scripts": ["ft-cli = foundrytools_cli_ng.__main__:cli"]},
    install_requires=_get_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    zip_safe=False,
)
