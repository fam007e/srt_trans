"""Setup configuration for the SRT Translator package."""

import os
from setuptools import setup, find_packages

# Read the content of the README file
with open(
    os.path.join(os.path.dirname(__file__), 'README.md'),
    encoding='utf-8'
) as f:
    long_description = f.read()

setup(
    name='srt-translator',
    version='0.1.1',
    author='Faisal Ahmed Moshiur',
    author_email='faisalmoshiur+gitSRT@gmail.com',
    description='A powerful script to translate .srt files with concurrent processing support.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fam007e/SRT_Trans',
    packages=find_packages(),
    install_requires=[
        'pysrt',
        'deep-translator',
        'tqdm',
        'chardet',
        'nltk>=3.9',
        'langdetect',
        'requests>=2.32.2',
        'urllib3>=1.26.19',
        'zipp>=3.19.1',
    ],
    entry_points={
        'console_scripts': [
            'translate-srt=srt_translator.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Video',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
