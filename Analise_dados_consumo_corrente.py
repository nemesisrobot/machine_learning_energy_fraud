#importando bibliotecas
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import ast

#método para pegar arquivo de configuração
def lerArquivoConfiguracao():
    configura = open('conf/config.json','r')
    dadosconfiguracao = configura.read()
    configura.close()
    return ast.literal_eval(dadosconfiguracao)


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


#método para coletar datas de leitura
def pegaDataLeitura(dados):
    datas = pd.DataFrame(dados.data.str.slice(0, 10))
    return datas.data.unique()


#metodo para pegar dias de consumo e adicionalos em uma lista
def pegaDiasdeConsumo(diasconsumo):
    for busca in pegaDataLeitura(dados):
        diasconsumo.append(dados.query('data.str.contains("{}")'.format(busca)))

#metodo para preencher listas

#fazendo append das informações na lsita
print(pegaDataLeitura(dados))
pegaDiasdeConsumo(diasconsumo)
print(diasconsumo)

arquivo.write('[{}] Tratando dados e fazer append em suas filas\n'.format(str(datetime.datetime.now())))
#percorrendo lista e separando dados de consumo 
for procura in diasconsumo:

    #append dos valores de consumo por dia
    consumo.append(procura.consumo.sum())
    
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


#plot de dados de consumo
arquivo.write('[{}] Plot de dados de consumo\n'.format(str(datetime.datetime.now())))
sns.barplot(x="data",y="consumo_total", data = novoframe)
plt.title('Grafico de Consumo Evolução')
plt.show()

#print dos valores do percentual de consumo de um dia para outro
for x in range(0,(novoframe.consumo_total.count()-1)):
    percentual = ((novoframe.consumo_total[x+1]-novoframe.consumo_total[x])/novoframe.consumo_total[x])*100
    mensagem_percentual_datas = "Percentual entre o dia {} e o dia {} : {:.2f}%".format(novoframe.data[x],novoframe.data[x+1],percentual)

    #print de informações
    print(mensagem_percentual_datas)
    arquivo.write('[{}] {}\n'.format(str(datetime.datetime.now()),mensagem_percentual_datas))
    
arquivo.write('[{}] Finalizando Análise\n'.format(str(datetime.datetime.now())))
arquivo.close()
