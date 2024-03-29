from setuptools import setup
import json


with open("metadata.json", encoding="utf-8") as fp:
    metadata = json.load(fp)


setup(
    name="lexibank_abrahammonpa",
    version="1.0",
    description=metadata["title"],
    license=metadata.get("license", ""),
    url=metadata.get("url", ""),
    py_modules=["lexibank_abrahammonpa"],
    include_package_data=True,
    zip_safe=False,
    entry_points={"lexibank.dataset": ["abrahammonpa=lexibank_abrahammonpa:Dataset"]},
    install_requires=["beautifulsoup4>=4.7.1", "pylexibank>=3.0"],
    extras_require={"test": ["pytest-cldf"]},
)
