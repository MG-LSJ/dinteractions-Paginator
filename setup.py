from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dinteractions_Paginator",
    version="2.0.2",
    description="Official interactions.py paginator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Toricane/dinteractions-Paginator",
    author="Toricane",
    author_email="prjwl028@gmail.com",
    license="GNU",
    packages=["interactions.ext.paginator"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=["discord-py-interactions", "interactions-wait-for"],
)
