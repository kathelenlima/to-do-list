from flask import Flask, request, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import redis
from sqlalchemy import text


# Inicialização da aplicação
app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/Tarefas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações da sessão com Redis
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'sess:'
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)

# Inicializa o SQLAlchemy e a sessão
db = SQLAlchemy(app)
Session(app)

# Modelo de Tarefa
class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='pendente')

# Criação do banco de dados e tabelas
with app.app_context():
    db.create_all()  # Isso cria as tabelas no banco de dados

# Rota para testar a conexão com o banco de dados
@app.route('/test_db', methods=['GET'])
def test_db():
    try:
        # Usar text() para a consulta SQL
        result = db.session.execute(text('SELECT 1'))
        return "Conexão bem-sucedida!"
    except Exception as e:
        return f"Erro: {e}"

# Rotas da API
@app.route('/tarefas', methods=['GET'])
def listar():
    tarefas = Tarefa.query.all()
    return jsonify([{'id': tarefa.id, 'descricao': tarefa.descricao, 'status': tarefa.status} for tarefa in tarefas])

@app.route('/tarefas', methods=['POST'])
def adicionar():
    dados = request.json
    nova_tarefa = Tarefa(descricao=dados['descricao'])
    db.session.add(nova_tarefa)
    db.session.commit()
    return jsonify({'id': nova_tarefa.id, 'descricao': nova_tarefa.descricao, 'status': nova_tarefa.status}), 201

@app.route('/tarefas/<int:tarefa_id>', methods=['PUT'])
def atualizar(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    tarefa.status = request.json.get('status', tarefa.status)
    db.session.commit()
    return jsonify({'id': tarefa.id, 'descricao': tarefa.descricao, 'status': tarefa.status})

@app.route('/tarefas/<int:tarefa_id>', methods=['DELETE'])
def remover(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    db.session.delete(tarefa)
    db.session.commit()
    return '', 204

# Teste do Redis
@app.route('/test_redis', methods=['GET'])
def test_redis():
    try:
        cache = redis.StrictRedis(host='localhost', port=6379, db=1)  # Certifique-se de que a conexão está correta
        cache.set('test_key', 'test_value')
        value = cache.get('test_key')
        return jsonify({'status': 'success', 'value': value.decode('utf-8')}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


def test_redis(client):
    response = client.get('/test_redis')
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['status'] == 'success'
    assert json_data['value'] == 'test_value'
