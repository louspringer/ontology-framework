from setuptools import setup, find_packages

setup(
    name="prompt-manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "psycopg2-binary",
        "pyyaml"
    ],
    entry_points={
        'console_scripts': [
            'prompt-manager=src.prompt_cli:cli',
        ],
    }
) 