from setuptools import setup, find_packages

setup(
    name='Highlight',
    author='Tab Atkins Jr.',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={'console_scripts': ['highlight = highlighter:cli']},
)
