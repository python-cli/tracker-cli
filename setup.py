from setuptools import setup, find_packages

setup(
    name='tracker-cli',
    version='0.1.0',
    description='A simple CLI tool for tracking records using TinyDB',
    author='Will Han',
    author_email='xingheng.hax@qq.com',
    packages=find_packages(),
    install_requires=[
        'tinydb',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'tracker=tracker.main:cli',
        ],
    },
    python_requires='>=3.7',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
) 