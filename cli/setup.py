from setuptools import setup, find_packages

setup(
    name='ProgramadorCLI',
    version='0.1',
    description='Cliente de inscrição para projeto Erlimar Programador',
    author='Erlimar Silva Campos',
    author_email='erlimar@gmail.com',
    url='http://programador.erlimar.com',
    packages=find_packages(),
    install_requires=[
        'Click>=*',
    ],
    entry_points={
        'console_scripts': [
            'programador = programador_cli:cli'
        ]
    },
    package_data={}
)
