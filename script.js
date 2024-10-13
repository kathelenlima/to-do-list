document.addEventListener('DOMContentLoaded', function() {
    carregTarefas();
});

function carregTarefas() {
    fetch('/tarefas', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        const listaTarefas = document.getElementById('listaTarefas');
        listaTarefas.innerHTML = '';
        data.forEach(tarefa => {
            const li = document.createElement('li');
            li.textContent = tarefa.descricao;
            const botaoDeletar = document.createElement('button');
            botaoDeletar.textContent = "Remover";
            botaoDeletar.onclick = () => deletarTarefa(tarefa.id);
            li.appendChild(botaoDeletar);
            listaTarefas.appendChild(li);
        });
    })
    .catch(error => console.error('Falha ao carregar tarefas: ', error));
}

function addTarefa() {
    const descricao = document.getElementById('descricao').value;
    if (descricao.trim() === '') {
        alert('A descrição da tarefa não pode ser vazia.');
        return;
    }

    fetch('/tarefas', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({descricao: descricao})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Falha ao adicionar tarefa');
        }
        return response.json();
    })
    .then(() => {
        document.getElementById('descricao').value = '';
        carregTarefas();
    })
    .catch(error => console.error('Falha ao adicionar tarefa: ', error));
}

function deletarTarefa(taskID) {
    fetch(`/tarefas/${taskID}`, {
        method: 'DELETE',
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Falha ao remover tarefa');
        }
        carregTarefas();
    })
    .catch(error => console.error('Falha ao remover tarefa: ', error));
}
