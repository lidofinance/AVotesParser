from setuptools import setup, find_packages

from parser.package import NAME

setup(
    name=NAME,
    description='Parser for human-readable decoding of EVM scripts.',
    author='Dmitri Ivakhnenko',
    author_email='dmit.ivh@gmail.com',
    use_scm_version={
        'root': '.',
        'relative_to': __file__,
        'local_scheme': 'node-and-timestamp'
    },
    setup_requires=['setuptools_scm'],
    packages=find_packages(
        where='.',
        exclude='tests'
    )

)
