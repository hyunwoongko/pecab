import os

from setuptools import setup, find_packages

version = None
author = None

with open(os.path.join("pecab", "__init__.py"), encoding="utf-8") as f:
    for line in f:
        if line.strip().startswith("__version__"):
            version = line.split("=")[1].strip().replace('"', "").replace("'", "")
        if line.strip().startswith("__author__"):
            author = line.split("=")[1].strip().replace('"', "").replace("'", "")

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pecab",
    version=version,
    author=author,
    author_email="kevin.ko@tunib.ai",
    url="https://github.com/hyunwoongko/pecab",
    license="Apache 2.0 License",
    description="Pure python Korean morpheme analyzer based on Mecab",
    long_description_content_type="text/markdown",
    platforms=["any"],
    long_description=long_description,
    packages=find_packages(exclude=["tests", "assets"]),
    python_requires=">=3",
    zip_safe=False,
    install_requires=[
        "numpy",
        "pyarrow",
        "regex",
        "emoji==1.2.0",
        "pytest"
    ],
    package_data={
        "": [
            "pecab/_resources/arrays.arrow",
            "pecab/_resources/words.arrow",
            "pecab/_resources/matrix.npy",
        ]
    },
    include_package_data=True,
)
