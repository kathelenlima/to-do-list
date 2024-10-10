from flask import Flask, request, jsonfy


def mostrar_tarefas(tarefas):
    print("\nLista de tarefas:")
    for i, tarefa in enumerate(tarefas,1):
        print(f'{i}. {tarefa}')
    print()

def adicionar_tarefa(tarefas):
    tarefa = input('Digite a nova tarefa: ')
    tarefas.append(tarefa)
    print(f'tarefa "{tarefa}" adicionada com sucesso!\n')

def remover_tarefa(tarefas):
    mostrar_tarefas(tarefas)
    numero = int(input("Digite o número da tarefa a ser removida: "))
    if 0 < numero <= len(tarefas):
        tarefa = tarefas.pop(numero - 1)
        print(f'Tarefa "{tarefa}" removida com sucesso!\n')
    else:
        print('Número inválido!')

def main():
    tarefas = []
    while True:
        print('1. Mostrar Tarefas')
        print('2. Adicionar Tarefas')
        print('3. Remover Tarefas')
        print('4. Sair')
        escolha = input('Escolha uma opção: ')

        if escolha == '1':
            mostrar_tarefas(tarefas)
        elif escolha == '2':
            adicionar_tarefa(tarefas)
        elif escolha == '3':
            remover_tarefa(tarefas)
        elif escolha == '4':
            print('Saindo...')
            break
        else:
            print('Opção inválida! Tente Novamente. \n')

if __name__ == "__main__":
    main()