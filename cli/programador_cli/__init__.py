# Copyright (c) 2020 Erlimar Silva Campos. Todos os direitos reservados.
# Licenciado sobre a licença MIT. Mais informações da licença em LICENSE.

import click
import os
import json
import requests
import pathlib

HOME = str(pathlib.Path.home())
PROGRAMADOR_HOME = os.path.join(HOME, '.programador')
URL_API = 'http://localhost:5000/api'

@click.group(help='Cliente para inscrição no projeto @ErlimarProgramador')
def cli():
    if os.path.exists(PROGRAMADOR_HOME) and not os.path.isdir(PROGRAMADOR_HOME):
        raise click.ClickException('Diretório .programador inválido!')

    if not os.path.exists(PROGRAMADOR_HOME):
        os.mkdir(PROGRAMADOR_HOME)

@cli.command('status', help='Exibe o status de sua conexão com o servidor')
def exibir_status():
    token = obter_token()
    if token != None:
        url = f'{URL_API}/check'
        headers = {'Authorization': f'Bearer {token}'}
        resposta = requests.get(url, headers=headers)

        if resposta.status_code != 200:
            click.secho('Status: Token inválido ou expirado')
        else:
            click.secho(f'Status: Conectado como {resposta.text}')
    else:
        click.secho('Status: Desconectado')

@cli.command('login', help='Faz o login no servidor')
@click.option('--email', help='Informe o e-mail para login')
def logar(email):
    email_login = email if email != None else click.prompt('Informe seu e-mail')
    senha = click.prompt('Informe a senha', hide_input=True)
    url = f'{URL_API}/token'
    headers = {'Content-Type': 'application/json'}
    payload = {'email':email_login, 'senha':senha}
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
    else:
        exibe_mensagem_resposta(resposta, default='Erro desconhecido ao fazer login')

@cli.command(help='Realiza o cadastro de um aluno')
@click.option('--nome', help='Informe seu nome')
@click.option('--email', help='Informe seu e-mail')
def cadastrar(nome, email):
    nome_cadastro = nome if nome != None else click.prompt('Informe seu nome')
    email_cadastro = email if email != None else click.prompt('Informe seu e-mail')
    senha = click.prompt('Informe uma senha', hide_input=True)
    senha_repetida = click.prompt('Informe a mesma senha novamente', hide_input=True)

    if senha != senha_repetida:
        click.echo('As senhas não conferem')
        return

    url = f'{URL_API}/cadastrar'
    headers = {'Content-Type': 'application/json'}
    payload = {'nome': nome_cadastro, 'email': email_cadastro, 'senha': senha }
    resposta = requests.post(url, data=json.dumps(payload), headers=headers)

    if resposta.status_code == 201:
        exibe_mensagem_resposta(resposta, default=None)
    else:
        exibe_mensagem_resposta(resposta, default='Erro desconhecido ao cadastrar usuário')

@cli.command(help='Faz a inscrição em um curso')
@click.option('--curso', help='Informe o código do curso')
def inscrever(curso):
    token = obter_token()

    if not token != None:
        click.secho('É necessário se conectar ao servidor primeiro')
        click.secho('Use: programador login')
    else:
        codigo_curso = curso if curso != None else click.prompt('Informe o código do curso')
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

    if token != None:
        url = f'{URL_API}/cursos'
        headers = {'Authorization': f'Bearer {token}'}
        resposta = requests.get(url, headers=headers)

        if resposta.status_code == 200:
            cursos = resposta.json()

            if len(cursos) > 0:
                click.secho('CODIGO                  NOME\n')
            else:
                click.secho('Não existe nenhum curso disponível!')

            for c in cursos:
                c_codigo = c['codigo'].ljust(20, ' ')
                c_nome = c['nome']
                click.secho(f'{c_codigo} -> {c_nome}')
        else:
            exibe_mensagem_resposta(resposta, default='Erro ao obter cursos do servidor')
    else:
        click.secho('É necessário se conectar ao servidor primeiro')
        click.secho('Use: programador login')

@cli.command('inscricoes')
def listar_meus_cursos():
    token = obter_token()

    if token != None:    
        url = f'{URL_API}/cursos/meus'
        headers = {'Authorization': f'Bearer {token}'}
        resposta = requests.get(url, headers=headers)

        if resposta.status_code == 200:
            inscricoes = resposta.json()

            if len(inscricoes) > 0:
                click.secho('CODIGO                  NOME\n')
            else:
                click.secho('Você ainda não está inscrito em nenhum curso!')

            for i in inscricoes:
                i_codigo = i['codigo'].ljust(20, ' ')
                i_nome = i['nome']
                click.secho(f'{i_codigo} -> {i_nome}')
        else:
            exibe_mensagem_resposta(resposta, default='Erro ao obter suas inscrições do servidor')
    else:
        click.secho('É necessário se conectar ao servidor primeiro')
        click.secho('Use: programador login')

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