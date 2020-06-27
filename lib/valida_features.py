#Autor:Diego Silva
#Data:27/06/2020
#Descrição:Script com métodos de valdiação de features para modelo de machine learning


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
        
