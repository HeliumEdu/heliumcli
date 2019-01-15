from setuptools import setup, find_packages

from heliumcli.cli import __version__

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="heliumcli",
    version=__version__,
    packages=find_packages(exclude=["tests"]),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=[
        "click",
        "GitPython >= 2.1.9",
        "PyYAML <= 3.13, >=3.12",
        "ansible >= 2.5"
    ],
    entry_points="""
        [console_scripts]
        helium=heliumcli.cli:cli
    """,
    description="CLI that provides a useful set of tools for maintaining, building, and deploying code in compatible projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alex Laird",
    author_email="support@heliumedu.com",
    url="https://github.com/HeliumEdu/heliumcli",
    download_url="https://github.com/HeliumEdu/heliumcli/archive/{}.tar.gz".format(__version__),
    keywords=["cli", "build", "deployment", "ansible", "git"],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools"
    ],
)
