from setuptools import setup, find_packages

setup(
    name='ProgramadorServidor',
    version='0.1',
    description='Servidor de inscrição para projeto Erlimar Programador',
    author='Erlimar Silva Campos',
    author_email='erlimar@gmail.com',
    url='http://programador.erlimar.com',
    packages=find_packages(),
    install_requires=[
        'Flask>=*',
        'Flask-SQLAlchemy>=*',
        'Flask-JWT-Extended>=*'
    ],
    entry_points={
        'console_scripts': [
            'programador-servidor = programador_servidor:cli'
        ]
    },
    package_data={
        '': ['templates/*']
    }
)
