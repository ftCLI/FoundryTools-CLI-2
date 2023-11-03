import io
from pathlib import Path
import setuptools

this_directory = Path(__file__).parent
long_description = this_directory.joinpath("README.md").read_text()


def _get_requirements():
    """
    Relax hard pinning in setup.py
    """
    with io.open("requirements.txt", encoding="utf8") as requirements:
        return [line.replace("==", ">=") for line in requirements.readlines()]


setuptools.setup(
    name="foundrytools-cli-2",
    version="0.0.1",
    description="A set of command line tools to inspect, manipulate and convert font files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ftCLI",
    author_email="ftcli@proton.me",
    url="https://github.com/ftCLI/FoundryTools-CLI-2",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["ft-cli = foundrytools_cli_2.__main__:main"]},
    install_requires=_get_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    zip_safe=False,
)
