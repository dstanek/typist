import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import typist


HERE = os.path.dirname(__file__)


def read_requirements(filename):
    filename = os.path.join(HERE, filename)
    return [line.strip() for line in open(filename) if line.strip()]


setup(
    name='typist',
    packages=['typist', 'typist.tests'],
    version=typist.__version__,
    description='type checking at test time',
    long_description=open('README.rst').read(),
    author='David Stanek',
    author_email='dstanek@dstanek.com',
    url='https://github.com/dstanek/typist',
    license='Apache Software License',
    install_requires=read_requirements('requirements.txt'),
    tests_require=read_requirements('test-requirements.txt'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ]
)
