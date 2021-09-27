"""
Parsing and decoding for human-readable representation of aragon votes payload.
"""
from setuptools import setup, find_namespace_packages

setup(
    name='avotes-parser-core',
    description=__doc__,
    author='Dmitri Ivakhnenko',
    author_email='dmit.ivh@gmail.com',
    use_scm_version={
        'root': './../..',
        'relative_to': __file__,
        'local_scheme': 'node-and-timestamp'
    },
    setup_requires=['setuptools_scm'],
    packages=find_namespace_packages(
        include=['avotes_parser.*']
    ),
    python_requires='>=3.8',
    install_requires=[
        'requests~=2.26.0',
        'pysha3~=1.0.0',
        'eth-brownie~=1.16.0',
        'web3~=5.23.0'
    ]
)
