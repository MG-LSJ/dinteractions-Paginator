from setuptools import setup
with open("README.md","r",encoding="utf-8") as fh:
    long_description=fh.read()

setup(
    name="dinteractions_Paginator",
    version="1.0.1",
    description="Unofficial discord-interactions multi page embed handler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JUGADOR123/Paginator.py",
    author="Jugador123",
    author_email="momocordova@gmail.com",
    license="GNU",
    packages=[""],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU License",
        "Operating System :: OS Independent",
    ],
)