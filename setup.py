import setuptools
import os

# read the contents of your README file
this_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_dir, "README.md")) as f:
    long_description = f.read()

setuptools.setup(
    name="py-vsys",
    version="0.2.2",
    description="The official Python SDK for VSYS APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=[
        "SDK",
        "api wrapper",
        "blockchain",
        "vsystems",
        "smart contract",
        "supernode",
        "defi",
    ],
    url="https://github.com/virtualeconomy/py-vsys",
    author="V SYSTEMS",
    author_email="developers@v.systems",
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=[
        "aiohttp=3.9.5",
        "python-axolotl-curve25519 @ git+https://github.com/hannob/python-axolotl-curve25519.git@fix_type#egg=python-axolotl-curve25519",
        "tiny_keccak",
        "base58~=2.1.1",
        "loguru~=0.7.2",
    ],
    python_requires=">=3.8",
)
