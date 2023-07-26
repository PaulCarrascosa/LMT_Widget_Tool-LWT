'''
Copyright (C)
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)#fulltext. 

For license issues, please contact:

Paul Carrascosa
Institut de Genomique Fonctionnelle
141 Rue de la Cardonille
34000, Montpellier

Email: paul.carrascosa@igf.cnrs.fr or damien.huzard@igf.cnrs.fr
'''

from setuptools import setup, find_packages
import pathlib
import os

path=pathlib.Path(__file__).parent.resolve()

try:
    with open(os.path.join(path,'README.md'),encoding='utf-8') as readme:
        long_description=readme.read()
except Exception:
    long_description=''


setup(name='LWTools',version='1.0.3',author='Paul Carrascosa, Damien Huzard',
    author_email='paul.carrascosa@igf.cnrs.fr',
    description='Tool for LMT data analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PaulCarrascosa/LMT_Widget_Tool-LWT',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'LWTools':['*.py''*.ipynb','*.txt','*.png','*.pb','*.jpg','*.csv','*.index','*.data-00000-of-00001']
    },
    license='GNU General Public License v3 (GPLv3)',
    classifiers=[
    'Programming Language :: Python :: 3.10',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: OS Independent',
    ],
    keywords='Live Mouse Tracker, LMT, Tool, Data analysis',
    python_requires='>=3.10',
    install_requires=[
        'setuptools>=61.0',
    	'matplotlib==3.5.2',
    	'lxml==4.9.1',
    	'pandas==1.4.3',
    	'affine==2.3.1',
    	'networkx==2.8.5',
    	'seaborn==0.11.2',
    	'dabest==2023.2.14',
    	'statsmodels==0.13.2',
    	'tabulate==0.8.10',
    	'ipywidgets==8.0.3',
    	'jupyterlab==3.5.0',
    ]   
)
