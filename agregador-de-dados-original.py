import pandas as pd
import time
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import datetime
import os

from IPython.display import display_html

def display_side_by_side(*args):
    html_str=''
    for df in args:
        html_str+=df.to_html(index = True, justify = 'center')
    display_html(html_str.replace('table','table style="display:inline"'),raw=True)
    
def energia_diaria(inversor):
    min_ene = 0
    first_energy = ''
    # itera até encontrar o primeiro valor de energia não nulo em modo de trabalho 1
    for i, j, k in zip(inversor.grid_energy, inversor.work_mode, inversor.timestamp):
        i = float(i)
        if((i > min_ene) & (j == 1)):
            min_ene = i
            first_energy = k
            break
    
    # itera começando do último elemento do dia, até encontrar o primeiro valor não nulo
    # em modo de trabalho 1
    max_ene = 0
    last_energy = ''
    for i, j, k in zip(inversor.grid_energy[::-1], inversor.work_mode[::-1], inversor.timestamp[::-1]):
        i = float(i)
        if((i > max_ene) & (j == 1)):
            max_ene = i
            last_energy = k
            break
    resp = [max_ene - min_ene, first_energy, last_energy]
    return (resp)

def tensao_barramento_diaria(inversor):
    v_bus = 0
    for i, j in zip(inversor.dc_bus_voltage, inversor.work_mode):
        i = float(i)
        if(j == 1):
            v_bus+= i;
    return (v_bus)


# In[7]:


cities = [['ct', '1'], ['pg', '2'], ['pb', '3'], ['cm', '4'], ['md', '5'], ['cp', '6']]
techs = ('mono', 'poli', 'cigs', 'cdte')
# mais perda de tempo por causa de mudanca de nome. Esse dict adequa os novos nomes de arquivo,
# de forma que não tenha que reescrever o código do próximo bloco.
argh = {'mon1': '00', 'mon2': '01', 'pol1': '00', 'pol2': '01', 'cigs': '00', 'cdte': '00'}
# pegando os inversores de 1k5 de Ponta Grossa
for city in cities:
    # pegando os caminhos para os inversores de 1k5 para dada cidade
    vars()['filepaths_'+city[0]] = list(Path("./leituras2/2020/06").rglob('*'+city[0]+"*.csv"))
    # pegando os caminhos para os inversores de 3k para dada cidade
    #vars()['filepaths_'+city[0]] = vars()['filepaths_'+city[0]] + list(Path("/leituras").rglob("*inv-2"+city[1]+"*.csv"))
    print('Numero de caminhos (' + city[0] + '): ' + str(len(vars()['filepaths_'+city[0]])))
    # criando dicts vazios para cada tecnologia
    for name in techs:
        vars()[name+'_'+city[0]] = {}

    # abrindo os csvs em dataframes para cada tecnologia
    for path in vars()['filepaths_'+city[0]]:
        for name in techs:
            if name in str(path):
                #vars()[name+'_'+city[0]][str(path).split('_')[4]+'_'+str(path).split('_')[5][:10]] = pd.read_csv(path, header=0, sep=',', skip_blank_lines = True, error_bad_lines=False).dropna()
                aux = str(path).split('-')
                vars()[name+'_'+city[0]][argh[aux[1]] + '_' + '20' + aux[2]+'-'+aux[3]+'-'+aux[4][0:2]] = pd.read_csv(path, names=['timestamp','v','i','net_ac_v','net_ac_i','net_ac_freq','ac_power','grid_energy','work_hours','dc_bus_voltage','work_mode','data'], header=0, sep=',', skip_blank_lines = True, error_bad_lines=False).dropna()
                break

    total = 0
    print('Arquivos por inversor (' + city[0] + '):')
    for name in techs:
        print(name + ': ' + str(len(vars()[name + '_' + city[0]])))
        total+=len(vars()[name+'_'+city[0]])
    print('Total: ' + str(total))


# In[8]:


# EDITE AQUI O PERÍODO QUE QUER PROCURAR OS ARQUIVOS
DATA_INICIO = "2020-06-01"
DATA_FIM = "2020-07-01" 

# EDITE AQUI DE QUAIS CIDADES QUER PROCURAR OS ARQUIVOS
#cities = [['ct', '1'], ['pg', '2'], ['pb', '3'], ['cm', '4'], ['md', '5'], ['cp', '6']]
#cities = [['ct', '1'], ['pg', '2'], ['pb', '3'], ['cm', '4'], ['md', '5'], ['cp', '6']]
#techs = ('mono', 'poli', 'cigs', 'cdte')

inicio = dt.datetime.strptime(DATA_INICIO, "%Y-%m-%d")
fim = dt.datetime.strptime(DATA_FIM, "%Y-%m-%d")


# In[9]:


# EXECUTE ESTA CÉLULA PARA GERAR OS .CSVS COM A ENERGIA DIÁRIA PARA O PERÍODO E CIDADES DEFINIDOS NA CÉLULA ANTERIOR
quantia_tec = {'mono': 2, 'poli': 2, 'cdte': 1, 'cigs': 1}
for city in cities:
    dia = inicio
    for nome in techs:
        for i in range(0, quantia_tec[nome]):
            pd.DataFrame
            vars()[nome+str(i)+'_'+city[0]+'_ene'] = pd.DataFrame(columns=['dia', 'energia', 'primeira_hora', 'ultima_hora'])
            vars()[nome+str(i)+'_'+city[0]+'_ene'].name = nome+str(i)

    # coleta a energia de cada dia e coloca no dataframe do respectivo inversor
    while dia < fim:
        for nome in techs:
            for i in range(0, quantia_tec[nome]):
                try:
                    energia = energia_diaria(vars()[nome+'_'+city[0]]['0'+str(i) + '_' + dia.strftime("%Y-%m-%d")])
                    vars()[nome+str(i)+'_'+city[0]+'_ene'] = vars()[nome+str(i)+'_'+city[0]+'_ene'].append(pd.DataFrame([[dia.strftime("%Y-%m-%d"), 
                                                                                                                          energia[0],
                                                                                                                          energia[1][11:],
                                                                                                                          energia[2][11:]]],
                                                                                                                          columns=['dia', 'energia', 'primeira_hora', 'ultima_hora']),
                                                                                                                          ignore_index=True).round(1)
                    #vars()[nome+str(i)+'_'+city[0]+'_ene']
                except KeyError:
                    pass
                    print('Sem dados para o dia ' + dia.strftime("%Y-%m-%d") + ' para o inversor ' + nome + str(i) + ' de ' + city[0] + '.')
                except TypeError:
                    print("Arquivo " + nome + ' ' + str(dia) + ' ' + city[0] + ' com erro de formatação.')
        dia+= dt.timedelta(days=1)

    arquivo = []
    # salva os dataframes em arquivos
    if not os.path.exists(inicio.strftime("%b")):
        os.makedirs(inicio.strftime("%b"))
    for nome in techs:
        for i in range(0, quantia_tec[nome]):
            vars()[nome+str(i)+'_'+city[0]+'_ene'].to_csv(inicio.strftime("%b")+'/'+nome+str(i)+'_'+city[0]+'_ene'+'_'+inicio.strftime("%m")+'.csv', decimal = ',', sep = ';', index = False)
            print((nome+str(i)+'_'+city[0]+'_ene'+'_'+inicio.strftime("%m")+'.csv gerado.').center(90, '_'))
            arquivo.append(vars()[nome+str(i)+'_'+city[0]+'_ene'])
            display(arquivo[i])

    #display_side_by_side(*arquivo)