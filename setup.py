from setuptools import setup, find_packages

setup(
    name="ontology-framework",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "rdflib",
    ],
    python_requires=">=3.8",
) 