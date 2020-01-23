# Copyright (c) 2020 Erlimar Silva Campos. Todos os direitos reservados.
# Licenciado sobre a licença MIT. Mais informações da licença em LICENSE.

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

@cli.command('status')
def exibir_status():
    '''
    Exibe o status de sua conexão com o servidor
    '''

    token = obter_token()

    if not token:
        click.secho('Status: Desconectado')
        return

    url = f'{URL_API}/check'

    headers = {'Authorization': f'Bearer {token}'}
    resposta = requests.get(url, headers=headers)

    if resposta.status_code != 200:
        click.secho('Status: Token inválido ou expirado')
        return

    click.secho('Status: Conectado')

@cli.command('login')
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

@cli.command()
def inscrever():
    '''
    Faz a inscrição em um curso
    '''

    token = obter_token()

    if not token != None:
        click.secho('É necessário se conectar ao servidor primeiro')
        click.secho('Use: programador login')
        return

    codigo_curso = click.prompt('Informe o código do curso')

    url = f'{URL_API}/inscrever'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    payload = {'codigo_curso': codigo_curso }

    resposta = requests.post(url, data=json.dumps(payload), headers=headers)

    if resposta.status_code == 201:
        exibe_mensagem_resposta(resposta, default='Inscrição realizada com sucesso')

    if resposta.status_code != 201:
        exibe_mensagem_resposta(resposta, default='Erro desconhecido ao fazer login')

@cli.command('logout')
def desconectar():
    token_file_path = os.path.join(PROGRAMADOR_HOME, 'token.json')

    if os.path.exists(token_file_path):
        os.unlink(token_file_path)

    click.secho('Agora você está desconectado do servidor')

@cli.command('cursos')
def listar_todos_cursos():
    token = obter_token()

    if not token != None:
        click.secho('É necessário se conectar ao servidor primeiro')
        click.secho('Use: programador login')
        return

    url = f'{URL_API}/cursos'
    headers = {'Authorization': f'Bearer {token}'}

    resposta = requests.get(url, headers=headers)

    if resposta.status_code != 200:
        exibe_mensagem_resposta(resposta, default='Erro ao obter cursos do servidor')
        return

    cursos = resposta.json()

    if len(cursos) > 0:
        click.secho('CODIGO                  NOME\n')
    else:
        click.secho('Não existe nenhum curso disponível!')

    for c in cursos:
        c_codigo = c['codigo'].ljust(20, ' ')
        c_nome = c['nome']
        click.secho(f'{c_codigo} -> {c_nome}')


@cli.command('inscricoes')
def listar_meus_cursos():
    token = obter_token()

    if not token != None:
        click.secho('É necessário se conectar ao servidor primeiro')
        click.secho('Use: programador login')
        return

    url = f'{URL_API}/cursos/meus'
    headers = {'Authorization': f'Bearer {token}'}

    resposta = requests.get(url, headers=headers)

    if resposta.status_code != 200:
        exibe_mensagem_resposta(resposta, default='Erro ao obter suas inscrições do servidor')
        return

    inscricoes = resposta.json()

    if len(inscricoes) > 0:
        click.secho('CODIGO                  NOME\n')
    else:
        click.secho('Você ainda não está inscrito em nenhum curso!')

    for i in inscricoes:
        i_codigo = i['codigo'].ljust(20, ' ')
        i_nome = i['nome']
        click.secho(f'{i_codigo} -> {i_nome}')

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
