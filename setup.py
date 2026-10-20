from setuptools import setup, find_packages

setup(
    name='jays-linter',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'jays-linter = src.cli:main',
        ],
    },
    author='Jay Choy',
    author_email='choyzhengjay@gmail.com',
    description='A Python function comment linter CLI tool',
    url='https://github.com/yourusername/function-comment-linter',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
