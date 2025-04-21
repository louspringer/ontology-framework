from setuptools import setup, find_packages

setup(
    name="ontology-framework",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "rdflib>=6.0.0",
        "click>=8.0.0",
        "jinja2>=3.0.0",
        "black>=22.0.0",
        "pytest>=7.0.0",
        "rich>=10.0.0",
        "requests>=2.0.0",
        "pyshacl>=0.20.0",
        "pytest-docker>=1.0.0"
    ],
    entry_points={
        "console_scripts": [
            "ontology=ontology_framework.cli:main"
        ]
    }
) 