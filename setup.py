from setuptools import setup

from heliumcli import settings

version = settings.VERSION

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="heliumcli",
    packages=[
        "heliumcli",
        "heliumcli.actions"
    ],
    version=version,
    python_requires=">=3.8",
    install_requires=[
        "GitPython>=2.1.15",
        "PyYAML>=5.1.2",
        "ansible>=2.10.0",
        "pyngrok>=7.1.0",
    ],
    scripts=["bin/helium-cli"],
    include_package_data=True,
    description="CLI tool that provides a useful set of tools for maintaining, building, and "
                "deploying code in compatible projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alex Laird",
    author_email="contact@alexlaird.com",
    url="https://github.com/HeliumEdu/heliumcli",
    download_url="https://github.com/HeliumEdu/heliumcli/archive/{}.tar.gz".format(
        version),
    project_urls={
        "Sponsor": "https://github.com/sponsors/alexdlaird"
    },
    license="MIT",
    classifiers=[
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Testing",
    ],
)
