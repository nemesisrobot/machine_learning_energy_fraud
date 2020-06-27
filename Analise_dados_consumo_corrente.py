#Autor:Diego Silva
#Data:27/06/2020
#Descrição:Script com mode me machine learning

#importando bibliotecas, para data science , plot de graficos
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt

#importando bibliotecas para matrizes , cast de dados e data e hora
import datetime
import ast
import numpy as np

#importando bibliotecas para valdia features e escrita de log
import lib.escreve_log_analise as log
import lib.valida_features as vf

#bibliotecas para machine learning
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score

#craindo log
nomeaquivo = str(str(datetime.datetime.now())[0:19]).replace('-','')
nomeaquivo = str(nomeaquivo.replace(':','')).replace(' ','')
arquivo = log.criar_arquivo_log(nomeaquivo)

#método para pegar arquivo de configuração
def lerArquivoConfiguracao():
    configura = open('conf/config.json','r')
    dadosconfiguracao = configura.read()
    configura.close()
    return ast.literal_eval(dadosconfiguracao)
   
#importando dados
log.escrever(arquivo, '-------------------------------------Data Science----------------------------\n', None)
log.escrever(arquivo,'Carregando base de dados de consumo',datetime.datetime.now())

dados = pd.read_json('{}/{}'.format(lerArquivoConfiguracao()['basepath'],lerArquivoConfiguracao()['file']))

log.escrever(arquivo, 'Iniciando Análise de dados',datetime.datetime.now())
#lista para armazenar os dias de consumo
diasconsumo = []

#criando lista para armazenar consumos, medias, maxima , minimas e datas
consumo = []
media = []
maxima = []
minima = []

#dados para analise do machine learning
teste_x = []
teste_y = []

#método para criar teste y
def cria_classe_teste_y(quantidade_de_um):
    for conta in range(0, quantidade_de_um):
        teste_y.append(np.ones(1))

            
#método para coletar datas de leitura
def pegaDataLeitura(dados):
    datas = pd.DataFrame(dados.data.str.slice(0, 10))
    return datas.data.unique()


#metodo para pegar dias de consumo e adicionalos em uma lista
def pegaDiasdeConsumo(diasconsumo):
    for busca in pegaDataLeitura(dados):
        diasconsumo.append(dados.query('data.str.contains("{}")'.format(busca)))

#metodo para preencher listas

#fazendo append das informações na lista
print(pegaDataLeitura(dados))
pegaDiasdeConsumo(diasconsumo)

log.escrever(arquivo,'Tratando dados e fazer append em suas filas',datetime.datetime.now())
#percorrendo lista e separando dados de consumo 
for procura in diasconsumo:

    #append dos valores de consumo por dia
    consumo.append(procura.consumo.max())
    
    #append dos dados de media
    media.append(procura.consumo.mean())

    #append dos dados de maxima
    maxima.append(procura.consumo.max())

    #append dos dados da minima
    minima.append(procura.consumo.min())
    
log.escrever(arquivo,'Finalizando append de filas',datetime.datetime.now())

#gerando novo dataframe
log.escrever(arquivo,'criando novo Dataframe',datetime.datetime.now())
novoframe = {
    'consumo_total':consumo,
    'media':media,
    'maxima':maxima,
    'minimo':minima,
    'data':pegaDataLeitura(dados)
    }

novoframe = pd.DataFrame(novoframe)
log.escrever(arquivo,'Finalizando criação do novo Dataframe',datetime.datetime.now())
print('------------------------------------')
print(novoframe)
print('------------------------------------')

#tratando data de referencia
datas = novoframe.data.str.slice(0,7)
datas = datas.unique()

#plot de dados de consumo
log.escrever(arquivo,'Plot de dados de consumo',datetime.datetime.now())

sns.barplot(x=novoframe.data.str.slice(8, 10),y="consumo_total", data = novoframe)
plt.title('Grafico de Consumo Evolução - Data: {}'.format(datas[0]))
plt.savefig('graficos/consumoevolucao{}.png'.format(nomeaquivo))

#print dos valores do percentual de consumo de um dia para outro
for x in range(0,(novoframe.consumo_total.count()-1)):
    percentual = ((novoframe.consumo_total[x+1]-novoframe.consumo_total[x])/novoframe.consumo_total[x])*100
    mensagem_percentual_datas = "Percentual entre o dia {} e o dia {} : {:.2f}%".format(novoframe.data[x],novoframe.data[x+1],percentual)

    #motando dados para uso de features do machine learning
    teste_x.append([vf.tem_consumo(novoframe.consumo_total[x+1], novoframe.consumo_total[x]),
    vf.dentro_do_esperado(percentual),
    vf.dias_varicao(percentual)])
    
    #print de informações
    print(mensagem_percentual_datas)
    log.escrever(arquivo, mensagem_percentual_datas, datetime.datetime.now())

log.escrever(arquivo, 'Finalizando Análise', datetime.datetime.now())  


#--------------------------------------------
#criando base de treino do machine learning
#sem consumo 
#sem consumo dentro do esperado
#sem consumo com variação esperada
#--------------------------------------------

semfraude1 = [0, 0, 0]
semfraude2 = [0, 1, 0]
semfraude3 = [0, 0, 1]

fraude1 = [0, 1, 1]
fraude2 = [1, 1, 1]
fraude3 = [1, 0, 1]
fraude4 = [1, 1, 1]

#montando dados para treino
treino_x = [fraude1, fraude2, fraude3, fraude4, semfraude1, semfraude2, semfraude3]
treino_y = [1, 1, 1, 1, 0, 0, 0]

log.escrever(arquivo,'-------------------------------------Machine Learning----------------------------',None)
#criando modelo e treinando modelo
log.escrever(arquivo,'Iniciando treinamento do modelo de machine learning',datetime.datetime.now())

print('Treino de modelo para analise de dados')
modelo = LinearSVC()
modelo.fit(treino_x, treino_y)

#previsão
previsao = modelo.predict(teste_x)
log.escrever(arquivo, 'gerando previsão : {}\n'.format(str(previsao)), datetime.datetime.now())

#criando testes_y com base no dados do teste_x
cria_classe_teste_y(len(teste_x))

print(len(teste_x))
#fazendo analise dos dados e gerando a ácuracia
log.escrever(arquivo,'Gerando ácuracia dos dados',datetime.datetime.now())
taxa_de_acerto = accuracy_score(teste_y, previsao)
print("Taxa de acerto: %.2f" % (taxa_de_acerto * 100))
log.escrever(arquivo,'Probabilidade de Fraude {}%'.format(str((taxa_de_acerto * 100))), datetime.datetime.now())

#fechando escrita
log.fechar_arquivo(arquivo)



