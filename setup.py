from setuptools import setup, find_packages

setup(
    name='jay_linter',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'jay_lint = main.cli:main',
        ],
    },
)