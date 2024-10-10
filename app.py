from flask import Flask, request, jsonify
from flask_session import Session
import redis

app = Flask(__name__)  #inicialização da aplicação

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'sess:'
app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)

Session(app)

cache = redis.StrictRedis(host='localhost', port=6379, db=1)


tarefas = []

@app.route('/tarefas', methods = ['GET'])       #rota para o endpoint \tarefas que responde a req GET
def listar():
    return jsonify(tarefas)

@app.route('/tarefas', methods=['POST'])
def adicionar():
    novaT = request.json                   #dados da nova tarefa do corpo da requisição
    novaT['id'] = len(tarefas) + 1         #ID único à nova tarefa
    novaT['status'] = 'pendente'           #status inicial é pendente
    tarefas.append(novaT)
    return jsonify(novaT), 201

@app.route('/tarefas/<int:tarefa_id>', methods=['PUT'])
def atualizar(tarefa_id):
    for tarefa in tarefas:
        if tarefa['id'] == tarefa_id:
            tarefa['status'] = request.json.get('status', tarefa['status'])
            return jsonify(tarefa)
        return jsonify({'erro': 'Tarefa não encontrada'}), 404
    
@app.route('/tarefas/<int:tarefa_id>', methods=['DELETE'])
def remover(tarefa_id):
    global tarefas
    tarefas = [tarefa for tarefa in tarefas if tarefa['id'] != tarefa_id]
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
