#!/usr/bin/env python3
"""
Setup script for Smart Class Attendance System
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Smart Class Attendance System using Facial Recognition"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='attendance-system',
    version='1.0.0',
    description='Smart Class Attendance System using Facial Recognition',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Sharon Yegon, Gidion Yegon, Gabriel Okal',
    author_email='attendance@moiuniversity.edu',
    url='https://github.com/RamspheldOnyangoOchieng/attendance-system',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'attendance-system=app:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Topic :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='attendance facial-recognition opencv raspberry-pi education',
)
