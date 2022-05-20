from interactions.ext import Base, Version, VersionAuthor

version: Version = Version(
    version="2.0.0",
    author=VersionAuthor(
        name="Toricane",
        email="prjwl028@gmail.com",
    ),
)

base = Base(
    name="dinteractions-Paginator",
    version=version,
    description="Unofficial discord-interactions multi page embed handler",
    link="https://github.com/Toricane/dinteractions-Paginator",
    packages=["interactions.ext.paginator"],
    requirements=["discord-py-interactions>=4.2.0", "interactions-wait-for"],
)
