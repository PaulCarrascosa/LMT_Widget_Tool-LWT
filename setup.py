'''
Copyright (C)
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)#fulltext. 

For license issues, please contact:

Paul Carrascosa
Institut de Génomique Fonctionnelle
141 Rue de la Cardonille
34000, Montpellier

Email: paul.carrascosa@igf.cnrs.fr or damien.huzard@igf.cnrs.fr
'''



from setuptools import setup,find_packages
import pathlib
import os

path=pathlib.Path(__file__).parent.resolve()

try:
    with open(os.path.join(path,'README.md'),encoding='utf-8') as readme:
        long_description=readme.read()
except Exception:
    long_description=''


setup(name='LMT_Widget_Tool',version='1.0.0',author='Paul Carrascosa, Damien Huzard',
    author_email='paul.carrascosa@igf.cnrs.fr',
    description='Tool for LMT data analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT',
    platform='any',
    packages=find_packages(),
    package_data={
        '':['*.txt','*.png','*.pb','*.jpg','*.csv','*.index','*.data-00000-of-00001']
    },
    license='GNU General Public License v3 (GPLv3)',
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: OS Independent',
    ],
    keywords='LMT, Tool, Data analysis',
    python_requires='>=3.10',
    install_requires=[
    'matplotlib',
    'lxml',
    'pandas',
    'affine',
    'networkx',
    'seaborn',
    'dabest',
    'statsmodels',
    'tabulate',
    ]  
)
