import click
import os
import json
import requests

from pathlib import Path

HOME = str(Path.home())
PROGRAMADOR_HOME = os.path.join(HOME, '.programador')
URL_API = 'http://localhost:5000/api'

@click.group()
def cli():
    '''
    Cliente para inscrição no projeto @ErlimarProgramador
    '''

    if os.path.exists(PROGRAMADOR_HOME) and not os.path.isdir(PROGRAMADOR_HOME):
        raise click.ClickException('Diretório .programador inválido!')

    if not os.path.exists(PROGRAMADOR_HOME):
        os.mkdir(PROGRAMADOR_HOME)

@cli.command("status")
def exibir_status():
    '''
    Exibe o status de sua conexão com o servidor
    '''

    click.secho(f'HOME: {HOME}', fg='green')
    click.secho(f'PROGRAMADOR_HOME: {PROGRAMADOR_HOME}')
    click.secho(f'TOKEN: {obter_token()}')

@cli.command()
def logar():
    '''
    Faz o login no servidor
    '''

    email = click.prompt('Informe seu e-mail')
    senha = click.prompt('Informe a senha', hide_input=True)

    url = f'{URL_API}/token'
    headers = {'Content-Type': 'application/json'}
    payload = {'email':email, 'senha':senha}

    resposta = requests.post(url, data=json.dumps(payload), headers=headers)

    if resposta.status_code == 201:
        if resposta.headers['content-type'] == 'application/json':
            data_json = resposta.json()

        if data_json == None or not 'access_token' in data_json:
            click.secho('Login efetuado, mas não foi possível entender o Token')
            return

        token_file_path = os.path.join(PROGRAMADOR_HOME, 'token.json')
        with open(token_file_path, 'w') as f:
            f.write(resposta.text)

        click.secho('Login efetuado com sucesso!', fg='green')

    if resposta.status_code != 201:
        exibe_mensagem_resposta(resposta, default='Erro desconhecido ao fazer login')

    #click.secho(str(resposta.headers['content-type']))
    #click.secho(str(resposta.status_code), fg='red')
    #click.secho(str(resposta.text), fg='blue')

# ----------------------------------------------------------------------------
# Métodos autiliares
# ----------------------------------------------------------------------------
def exibe_mensagem_resposta(resposta, default):
    def imprime(msg):
        cor = 'green' if resposta != None and resposta.status_code in range(200, 300) else 'red'
        click.secho(msg, fg=cor)

    if resposta == None or resposta.status_code == None:
        imprime(default)
        return

    if resposta.headers['content-type'] == 'application/json':
        data_json = resposta.json()

        if 'msg' in data_json:
            imprime(data_json['msg'])
            return

        imprime(str(resposta.text))

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
