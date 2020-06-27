#Autor:Diego Silva
#Data:27/06/2020
#Descrição:Script para scrita de log


def criar_arquivo_log(nomeaquivo):
    #criando arquivo
    return open('logs/analise{}'.format(nomeaquivo),'w')

#método para escreve dados no log
def escrever(arquivo, mensagem, data):
    if data is None:
        arquivo.write('{}\n'.format(mensagem))
    else:
        arquivo.write('[{}] {}\n'.format(str(data),mensagem))


def fechar_arquivo(arquivo):
    arquivo.close()

