import click
import os
import json

from pathlib import Path

HOME = str(Path.home())
PROGRAMADOR_HOME = os.path.join(HOME, '.programador')

@click.group()
def cli():
    if os.path.exists(PROGRAMADOR_HOME) and not os.path.isdir(PROGRAMADOR_HOME):
        raise click.ClickException('Diretório .programador inválido!')

    if not os.path.exists(PROGRAMADOR_HOME):
        os.mkdir(PROGRAMADOR_HOME)

@cli.command()
def status():
    click.secho(f'HOME: {HOME}', fg='green')
    click.secho(f'PROGRAMADOR_HOME: {PROGRAMADOR_HOME}')
    click.secho(f'TOKEN: {obter_token()}')

def obter_token():
    token_file_path = os.path.join(PROGRAMADOR_HOME, 'token.json')

    if not os.path.exists(token_file_path):
        return None

    if not os.path.isfile(token_file_path):
        raise click.ClickException('Arquivo de Token inválido!')

    with open(token_file_path, 'r') as j:
        token_json = json.load(j)

    if 'access_token' not in token_json:
        raise click.ClickException('Arquivo de token sem chave access_token!')

    return token_json['access_token']
