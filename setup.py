from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("semver.txt", "r") as fh:
    semver = fh.read().strip()
with open("requirements.txt", "r") as fh:
    install_requires = [x.strip() for x in fh.read().strip().split("\n")]

setup(
    name='bs-highlighter',
    version=semver,
    author='Tab Atkins-Bittner',
    description='A command-line highlighter syntax-highlighter, using Pygments and widlparser.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tabatkins/highlighter",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.7",
    entry_points={'console_scripts': ['highlight = highlighter:cli']},
)