# -*- coding: utf-8 -*-

# Copyright (c) 2020 Erlimar Silva Campos. Todos os direitos reservados.
# Licenciado sobre a licença MIT. Mais informações da licença em LICENSE.

from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashlib import sha256

# -----------------------------------------------------------
# Configurações da aplicação Flask
# -----------------------------------------------------------
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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
    nome = db.Column(db.String(100), unique=True, nullable=False)
    data_cadastro = db.Column(db.DateTime(), nullable=False,
                              default=datetime.utcnow)


# -----------------------------------------------------------
# Rotas da API 
# -----------------------------------------------------------
@app.route("/api/cadastrar", methods=['POST'])
def api_route_cadastrar():
    if not request.is_json:
        return jsonify(error=True, msg="JSON não identificado na requisição"), 400

    nome = request.json.get("nome", None)
    email = request.json.get("email", None)
    senha = request.json.get("senha", None)

    if not nome or not email or not senha:
        return jsonify(error=True, msg="Dados inválidos"), 400

    # A senha precisa ter pelo menos 6 caracteres
    senha = senha.strip()

    if len(senha) < 6:
        return jsonify(error=True, msg="A senha precisa ter pelo menos 6 caracteres"), 400

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario:
        return jsonify(error=True, msg="O e-mail %s já está cadastrado!" % email), 400

    senha_hash = sha256(senha.encode()).hexdigest()
    novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
    
    db.session.add(novo_usuario)
    db.session.commit()

    print("Novo usuário: %s" % novo_usuario)

    return jsonify(msg="Ok")

# -----------------------------------------------------------
# Páginas do site
# -----------------------------------------------------------
@app.route("/")
def page_index():
    return render_template('index.html')

# -----------------------------------------------------------
# Inicialização 
# -----------------------------------------------------------
db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

