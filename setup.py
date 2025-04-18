from setuptools import setup, find_packages

setup(
    name="ontology-framework",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rdflib>=6.0.0",
        "openai>=1.0.0",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
    ],
    python_requires=">=3.10",
) 