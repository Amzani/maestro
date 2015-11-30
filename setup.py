from setuptools import setup, find_packages

import maestro


install_requires = [
    'GitPython>=1.0.1',
    'PyYAML>=3.11',
    'networkx>=1.10',
]

setup(
    name='maestro',
    version=maestro.__version__,
    description=maestro.__doc__.strip(),

    packages=find_packages(),

    author=maestro.__author__,
    author_email='matt.hauglustaine@gmail.com',

    entry_points={
        'console_scripts': [
            'maestro = maestro.__main__:main',
        ]
    },

    install_requires=install_requires,
)
