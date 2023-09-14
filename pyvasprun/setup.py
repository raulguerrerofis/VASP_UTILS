from setuptools import setup, find_packages

setup(
    author="Raúl Guerrero",
    description="Package for extract and plot bands structure from vasprun.xml files.",
    name="pyvasprun",
    version='0.1.0',
    packages=find_packages(include=[]),
    install_requires=[
        "pandas>=1.5.3",
        "numpy>=1.23.5",
        "ipykernel>=6.25.2"
    ],
    python_requires='>=3.8',
)