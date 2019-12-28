import setuptools
import PyBugger

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyBugger",
    version=PyBugger.__version__,
    author="Krzysztof Krysiński",
    author_email="krysinskikrzysztof123@gmail.com",
    description="Debug python functions without leaving python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flabbet/Pybugger",
    packages=['PyBugger'],
    keywords='debug python code debugger',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
