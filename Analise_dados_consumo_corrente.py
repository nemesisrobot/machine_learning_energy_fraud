#importando bibliotecas
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import ast

#bibliotecas para machine learning
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score

#método para pegar arquivo de configuração
def lerArquivoConfiguracao():
    configura = open('conf/config.json','r')
    dadosconfiguracao = configura.read()
    configura.close()
    return ast.literal_eval(dadosconfiguracao)

#metodo para feaature de consumo
def tem_consumo(dia_mais_um, dia_atual):
    if dia_atual > dia_mais_um:
        return 0
    else:
        return 1

#método de feature para checar se variação esta dentro do esperado
def dentro_do_esperado(percentual):
    if percentual >= 12.00:
        return 0
    else:
        return 1

#método para feature de variação entre dias
def dias_varicao(percentual):
    if percentual >= 10:
        return 0
    else:
        return 1
        
   
#importando dados
dados = pd.read_json('{}/{}'.format(lerArquivoConfiguracao()['basepath'],lerArquivoConfiguracao()['file']))

#motando nome do arquivo
nomeaquivo = str(str(datetime.datetime.now())[0:19]).replace('-','')
nomeaquivo = str(nomeaquivo.replace(':','')).replace(' ','')

#criando arquivo
arquivo = open('logs/analise{}'.format(nomeaquivo),'w')
arquivo.write('[{}] Iniciando Análise\n'.format(str(datetime.datetime.now())))
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
def cria_dados(recursos):
    for busca in teste_x:
        if((busca[0]+busca[1]+busca[2]) > 1):
            teste_y.append(1)
        else:
            teste_y.append(0)
            
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
#print(diasconsumo)

arquivo.write('[{}] Tratando dados e fazer append em suas filas\n'.format(str(datetime.datetime.now())))
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
arquivo.write('[{}] Finalizando append de filas\n'.format(str(datetime.datetime.now())))

#gerando novo dataframe
arquivo.write('[{}] criando novo Dataframe\n'.format(str(datetime.datetime.now())))
novoframe = {
    'consumo_total':consumo,
    'media':media,
    'maxima':maxima,
    'minimo':minima,
    'data':pegaDataLeitura(dados)
    }

novoframe = pd.DataFrame(novoframe)
arquivo.write('[{}] Finalizando criação do novo Dataframe\n'.format(str(datetime.datetime.now())))
print('------------------------------------')
print(novoframe)
print('------------------------------------')

#tratando data de referencia
datas = novoframe.data.str.slice(0,7)
datas = datas.unique()


#plot de dados de consumo
arquivo.write('[{}] Plot de dados de consumo\n'.format(str(datetime.datetime.now())))
sns.barplot(x=novoframe.data.str.slice(8, 10),y="consumo_total", data = novoframe)
plt.title('Grafico de Consumo Evolução - Data: {}'.format(datas[0]))
#plt.show()
plt.savefig('graficos/consumoevolucao{}.png'.format(nomeaquivo))

#print dos valores do percentual de consumo de um dia para outro
for x in range(0,(novoframe.consumo_total.count()-1)):
    percentual = ((novoframe.consumo_total[x+1]-novoframe.consumo_total[x])/novoframe.consumo_total[x])*100
    mensagem_percentual_datas = "Percentual entre o dia {} e o dia {} : {:.2f}%".format(novoframe.data[x],novoframe.data[x+1],percentual)

    #motando dados para uso de features do machine learning
    teste_x.append([tem_consumo(novoframe.consumo_total[x+1], novoframe.consumo_total[x]),
    dentro_do_esperado(percentual),
    dias_varicao(percentual)])
    
    #print de informações
    print(mensagem_percentual_datas)
    arquivo.write('[{}] {}\n'.format(str(datetime.datetime.now()),mensagem_percentual_datas))
    
arquivo.write('[{}] Finalizando Análise\n'.format(str(datetime.datetime.now())))
arquivo.close()

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

#criando modelo e treinando modelo
print('Treino modelo para analise de dados')
modelo = LinearSVC()
modelo.fit(treino_x, treino_y)

#previsão
previsao = modelo.predict(teste_x)

#criando testes_y com base no dados do teste_x
cria_dados(teste_x)
print('previsao')
print(previsao)
print("y"+str(teste_y))
print("x"+str(teste_x))
print(previsao)
#fazendo analise dos dados e gerando a ácuracia 
corretos = (previsao == [1, 1, 1, 1]).sum()
print(corretos)
total = len(teste_x)
taxa_de_acerto = corretos/total
print("Taxa de acerto: %.2f" % (taxa_de_acerto * 100))


