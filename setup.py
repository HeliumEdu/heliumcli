from distutils.core import setup

from heliumcli import utils

version = utils.VERSION
description = 'CLI tool that provides a useful set of tools for maintaining, building, and deploying code in ' \
              'compatible projects'

setup(
    name='heliumcli',
    packages=[
        'heliumcli', 'heliumcli.actions'
    ],
    version=version,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=[
        'GitPython >= 2.1.9',
        'PyYAML >=3.12',
        'ansible >= 2.5.2'
    ],
    scripts=['bin/helium-cli'],
    description=description,
    long_description=description,
    author='Alex Laird',
    author_email='contact@alexlaird.com',
    url='https://github.com/HeliumEdu/heliumcli',
    download_url='https://github.com/HeliumEdu/heliumcli/archive/{}.tar.gz'.format(version),
    keywords=['cli', 'build', 'deployment', 'ansible', 'git'],
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools"
    ],
)
