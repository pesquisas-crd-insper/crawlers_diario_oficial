
import os,re
import pandas as pd
from pathlib import Path
import glob
import fitz
import numpy as np
import time


ini = time.time()
lista = glob.glob("./*.csv")


# for planilha in lista:
# 	dados = pd.read_csv(planilha)
# 	dados = dados [["numero_processo","publicacao",'numeros_paginas',"nomes_pastas"]]
# 	print(dados["publicacao"].iloc[-1])
# 	z = input("")
# print(planilha["publicacao"])


# planilha.to_excel("teste.xlsx", index = False)


############# parte de selecionar as publis

dados_separados = pd.DataFrame()
for planilha in lista:
	print("lendo:",planilha)
	dados = pd.read_csv(planilha)
	idx =[]
	for n in range(len(dados)):
		pub = str(dados['publicacao'][n])
		if re.search(r'(?i)corrupção',pub,re.MULTILINE):
			pass
		else:
			idx.append(n)

	dados.drop(idx, inplace = True)
	# print(dados)
	dados_separados = pd.concat([dados_separados,dados])

print(dados_separados)
dados_separados.to_csv("Separados_corrupção.csv", index = False)
# z = input("")
fim = time.time()
tempo_total = (fim-ini)//60 #calcula o tempo decorrido
print("O tempo de execução foi aproximadamente =", tempo_total,"minutos")


### verificar os dados únicos

dados = pd.read_csv("Separados_corrupção.csv")
print(dados.info())

# print(dados['numero_processo'].value_counts())