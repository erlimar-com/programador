# Copyright (c) 2020 Erlimar Silva Campos. Todos os direitos reservados.
# Licenciado sobre a licença MIT. Mais informações da licença em LICENSE.

from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_claims,
    get_jwt_identity
)
from datetime import datetime
from hashlib import sha256
from uuid import uuid1
from os import getenv

# -----------------------------------------------------------
# Configurações da aplicação Flask
# -----------------------------------------------------------
app = Flask(__name__)

ENV_DATABASE_FILE = getenv('DATABASE_FILE', 'db.sqlite3')
ENV_JWT_SECRET_KEY = getenv('JWT_SECRET_KEY', str(uuid1()))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % ENV_DATABASE_FILE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = ENV_JWT_SECRET_KEY

db = SQLAlchemy(app)
jwt = JWTManager(app)

# -----------------------------------------------------------
# Modelos do banco de dados
# -----------------------------------------------------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(56), nullable=False)
    data_cadastro = db.Column(db.DateTime(), nullable=False,
                              default=datetime.utcnow)

class Inscricao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_inscricao = db.Column(db.DateTime(), nullable=False,
                               default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'),
                           nullable=False)
    usuario = db.relationship('Usuario')
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'),
                         nullable=False)
    curso = db.relationship('Curso')

class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    data_cadastro = db.Column(db.DateTime(), nullable=False,
                              default=datetime.utcnow)

# -----------------------------------------------------------
# Utilitários JWT
# -----------------------------------------------------------
@jwt.user_claims_loader
def jwt_add_claims(usuario):
    return { 'usuario.id': usuario.id, 'usuario.email': usuario.email }

@jwt.user_identity_loader
def jwt_identity_lookup(usuario):
    return usuario.email

# -----------------------------------------------------------
# Rotas da API 
# -----------------------------------------------------------
@app.route('/api/cadastrar', methods=['POST'])
def api_cadastrar():
    if not request.is_json:
        return jsonify(error=True, msg='JSON não identificado na requisição'), 400

    nome = request.json.get('nome', None)
    email = request.json.get('email', None)
    senha = request.json.get('senha', None)

    if not nome or not email or not senha:
        return jsonify(error=True, msg='Dados inválidos'), 400

    # A senha precisa ter pelo menos 6 caracteres
    senha = senha.strip()

    if len(senha) < 6:
        return jsonify(error=True, msg='A senha precisa ter pelo menos 6 caracteres'), 400

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario:
        return jsonify(error=True, msg='O e-mail %s já está cadastrado!' % email), 400

    senha_hash = sha256(senha.encode()).hexdigest()
    novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)

    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify(msg='Usuário cadastrado com sucesso!')

@app.route('/api/inscrever', methods=['POST'])
@jwt_required
def api_inscrever():
    if not request.is_json:
        return jsonify(error=True, msg='JSON não identificado na requisição'), 400

    codigo_curso = request.json.get('codigo_curso', None)

    if not codigo_curso:
        return jsonify(error=True, msg='Código de curso não informado'), 400

    curso = Curso.query.filter_by(codigo=codigo_curso).first()

    if not curso:
        return jsonify(error=True, msg='O curso informado não existe.'), 400

    id_usuario_logado = get_jwt_claims()['usuario.id']
    usuario = Usuario.query.filter_by(id=id_usuario_logado).first()

    if not usuario:
        return jsonify(error=True, msg='Erro ao identificar usuário logado.'), 400

    nova_inscricao = Inscricao(usuario_id=usuario.id, curso_id=curso.id)
    db.session.add(nova_inscricao)
    db.session.commit()

    return jsonify(msg='Você foi inscrito com sucesso no curso %s (%s)' % (curso.nome, curso.codigo))

@app.route('/api/token', methods=['POST'])
def api_token():
    if not request.is_json:
        return jsonify(error=True, msg='JSON não identificado na requisição'), 400

    email = request.json.get('email', None)
    senha = request.json.get('senha', None)

    if not email or not senha:
        return jsonify(error=True, msg='Dados inválidos'), 400

    senha_hash = sha256(senha.encode()).hexdigest()
    usuario = Usuario.query.filter_by(email=email, senha=senha_hash).first()

    if not usuario:
        return jsonify(error=True, msg='E-mail ou senha inválidos!'), 400

    access_token = create_access_token(identity=usuario)

    return jsonify(access_token=access_token), 201

@app.route('/api/check', methods=['GET'])
@jwt_required
def api_check():
    email_usuario_logado = get_jwt_claims()['usuario.email']
    return jsonify(email_usuario_logado)

@app.route('/api/cursos', methods=['GET'])
@jwt_required
def api_listar_cursos():
    cursos = []

    for curso in Curso.query.order_by(Curso.nome).all():
        cursos.append({'codigo': curso.codigo, 'nome': curso.nome})

    return jsonify(cursos)

@app.route('/api/cursos/meus', methods=['GET'])
@jwt_required
def api_listar_meus_cursos():
    cursos = []
    id_usuario_logado = get_jwt_claims()['usuario.id']

    for inscricao in Inscricao.query.filter_by(usuario_id=id_usuario_logado):
        curso = Curso.query.filter_by(id=inscricao.curso_id).first()
        cursos.append({'codigo': curso.codigo, 'nome': curso.nome})

    return jsonify(cursos)

# -----------------------------------------------------------
# Páginas do site
# -----------------------------------------------------------
@app.route('/')
def page_index():
    return render_template('index.html')

# -----------------------------------------------------------
# Inicialização 
# -----------------------------------------------------------
def cli():
    print("Utilizando:")
    print("-> JWT_SECRET_KEY: %s" % ENV_JWT_SECRET_KEY)
    print("-> DATABASE_FILE: %s" % ENV_DATABASE_FILE)

    db.create_all()
    app.run(debug=True)