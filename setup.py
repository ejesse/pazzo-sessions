from setuptools import setup, find_packages

long_description = open('README.rst').read()

setup(
    name='pazzo',
    version="0.1",
    description='Session storage for Python sessions',
    long_description=long_description,
    author='Jesse Emery',
    author_email='jesse@jesseemery.com',
    url='https://github.com/ejesse/pazzo-sessions',
    packages=find_packages(),
    license='MIT License',
    platforms=["any"],
)
