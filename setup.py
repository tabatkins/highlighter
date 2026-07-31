from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("semver.txt", "r", encoding="utf-8") as fh:
    semver = fh.read().strip()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    install_requires = [x.strip() for x in fh.read().strip().split("\n") if len(x) and x[0].isalpha()]

setup(
    name="bs-highlighter",
    version=semver,
    author="Tab Atkins-Bittner",
    description="A command-line syntax-highlighter, using Pygments and widlparser.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tabatkins/highlighter",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.7",
    entry_points={"console_scripts": [
        "bs-highlight = highlighter:cli",
        "bs-highlight-server = highlighter:server",
    ]},
)
