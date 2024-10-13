from flask import Flask, render_template, request, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import redis
from sqlalchemy import text
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy.exc import DataError
from flask_cors import CORS

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/Tarefas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'sess:'
app.config['SESSION_REDIS'] = redis.StrictRedis(host='172.20.96.194', port=6379, db=0)

db = SQLAlchemy(app)
Session(app)

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pendente')

with app.app_context():
    db.create_all()

class TarefasValid(Schema):
    descricao = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, error="A descrição não pode estar vazia."),
            validate.Length(max=200, error="A descrição não pode ter mais de 200 caracteres.")
        ]
    )
    status = fields.String(
        required=False,
        validate=validate.OneOf(["pendente", "em andamento", "concluído"], error="Status inválido.")
    )

tarefas_valid = TarefasValid()

@app.route('/test_db', methods=['GET'])
def test_db():
    try:
        result = db.session.execute(text('SELECT 1'))
        return "Conexão bem-sucedida!"
    except Exception as e:
        return f"Erro: {e}"

@app.route('/listar_tarefas', methods=['GET'])
def listar_tarefas():
    try:
        query = text('SELECT * FROM Tarefa')
        result = db.session.execute(query)
        tarefas = [{'id': row['id'], 'descricao': row['descricao'], 'status': row['status']} for row in result]
        return jsonify(tarefas)
    except Exception as e:
        return f"Erro: {e}"

@app.route('/tarefas', methods=['GET'])
def listar():
    tarefas = Tarefa.query.all()
    return jsonify([{'id': tarefa.id, 'descricao': tarefa.descricao, 'status': tarefa.status} for tarefa in tarefas])

@app.route('/tarefas', methods=['POST'])
def adicionar():
    dados = request.json
    try:
        tarefas_valid.load(dados)
    except ValidationError as err:
        return jsonify(err.messages), 400

    nova_tarefa = Tarefa(descricao=dados['descricao'], status=dados.get('status', 'pendente'))
    db.session.add(nova_tarefa)
    try:
        db.session.commit()
    except DataError as e:
        db.session.rollback()
        if "value too long" in str(e.orig):
            return jsonify({"error": "A descrição não pode ter mais de 200 caracteres."}), 400
        return jsonify({"error": "Erro de dados ao adicionar a tarefa."}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erro ao adicionar a tarefa. Por favor, tente novamente."}), 500

    return jsonify({'id': nova_tarefa.id, 'descricao': nova_tarefa.descricao, 'status': nova_tarefa.status}), 201

@app.route('/tarefas/<int:tarefa_id>', methods=['PUT'])
def atualizar(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    dados = request.json
    try:
        tarefas_valid.load(dados, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    tarefa.descricao = dados.get('descricao', tarefa.descricao)
    tarefa.status = dados.get('status', tarefa.status)
    db.session.commit()
    return jsonify({'id': tarefa.id, 'descricao': tarefa.descricao, 'status': tarefa.status})

@app.route('/tarefas/<int:tarefa_id>', methods=['DELETE'])
def remover(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    db.session.delete(tarefa)
    db.session.commit()
    return '', 204

@app.route('/test_redis', methods=['GET'])
def test_redis():
    try:
        cache = redis.StrictRedis(host='localhost', port=6379, db=1)
        cache.set('test_key', 'test_value')
        value = cache.get('test_key')
        return jsonify({'status': 'success', 'value': value.decode('utf-8')}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

def test_redis(client):
    response = client.get('/test_redis')
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['status'] == 'success'
    assert json_data['value'] == 'test_value'
