# Imports de bibliotecas
# Imports de bibliotecas
import os
import pandas as pd
from requests.models import get_auth_from_url
from tqdm import tqdm
import requests
from pathlib import Path
import time
from bs4 import BeautifulSoup
from lxml import etree
from fake_useragent import UserAgent
import urllib.request
from urllib import request
# Imports Selenium (Navegador Web)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PyPDF2 import PdfFileReader, PdfFileMerger
import shutil
import time
import datetime
from datetime import date
import shutil
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json



def quantidade_itens(url):

	html = request.urlopen(url).read()
	soup = BeautifulSoup(html,'html.parser')
	info = json.loads(soup.text)
	
	quantidade_itens = info["count"]

	quantidade_paginas = quantidade_itens//100
	if quantidade_itens%100 > 0:
		quantidade_paginas = quantidade_paginas +1

	return quantidade_paginas

##########################################################

def ler_json(url,n):
															# exemplo de URL para registro
	# url = 'https://comunicaapi.pje.jus.br/api/v1/comunicacao?pagina=1&itensPorPagina=5&siglaTribunal=TRF4&meio=D&dataDisponibilizacaoInicio=2021-01-18&dataDisponibilizacaoFim=2021-01-18'

	
	# faz a requisição na URL e guarda numa variável em formato JSON

	html = request.urlopen(url).read()
	soup = BeautifulSoup(html,'html.parser')
	info = json.loads(soup.text)

	
	list_itens = info["items"]

	
	df_textos_paginas = pd.DataFrame()
	# # itera sobre essa lista no JSON coletando os nomes dos documentos, data de publicação e link 
	for z in list_itens:
		dados = pd.DataFrame([z])
		df_textos_paginas = pd.concat([df_textos_paginas, dados])


	df_textos_paginas.rename(columns={'numero_processo': 'numero_processo_','numeroprocessocommascara':'numero_processo','texto': 'publicacao',
		'nomeClasse': 'tipos_processuais', "nomeOrgao": 'orgao_julgador',
		'destinatarioadvogados':'representantes', 'datadisponibilizacao': 'nomes_pastas'}, inplace= True)


	df_textos_paginas.reset_index(inplace=True)

	df_textos_paginas["numeros_paginas"] = str(n)
	df_textos_paginas["nome_documento"] = "DJEN"
	df_textos_paginas["estado"] = None
	df_textos_paginas["tribunal"] = "TRF1"
	df_textos_paginas["comarcas"] = None
	df_textos_paginas["assuntos"] = None
	df_textos_paginas["nomes_pastas"] = df_textos_paginas["nomes_pastas"].str.replace("/","-")	
	frag = df_textos_paginas["nomes_pastas"].str.split("-", n=2, expand = True)
	df_textos_paginas["dia"] = frag[0]
	df_textos_paginas["mes"] = frag[1]
	df_textos_paginas["ano"] = frag[2]
	df_textos_paginas["data_decisao"] = None
	df_textos_paginas["tipo_publicacao"] = None

	df_textos_paginas = df_textos_paginas[["numero_processo", "estado","publicacao","numeros_paginas","tipos_processuais","assuntos","comarcas",
			"representantes","dia", "mes","ano","nome_documento","nomes_pastas","data_decisao","orgao_julgador","tipo_publicacao","tribunal"]]

	return df_textos_paginas


##############################################################3

def main():

	ini = time.time()
	dir_path = str(os.path.dirname(os.path.realpath(__file__)))
	path = dir_path + f'\Diarios_processados_TRF1_DJEN_csv_2021'
	Path(path).mkdir(parents=True, exist_ok=True)
	url_1 = 'https://comunicaapi.pje.jus.br/api/v1/comunicacao?pagina=1&itensPorPagina=5&siglaTribunal=TRF1&meio=D&dataDisponibilizacaoInicio=2021-01-01&dataDisponibilizacaoFim=2021-12-31'
	quantidade_paginas = quantidade_itens(url_1)
	todos_dados_final = pd.DataFrame()
	for n in range(1,quantidade_paginas):
		url = 'https://comunicaapi.pje.jus.br/api/v1/comunicacao?pagina={}&itensPorPagina=100&siglaTribunal=TRF1&meio=D&dataDisponibilizacaoInicio=2021-01-01&dataDisponibilizacaoFim=2021-12-31'.format(n)
		df_textos_paginas = ler_json(url,n)

		# print(df_textos_paginas[["numero_processo","estado","publicacao","numeros_paginas","nomes_pastas"]])
		# print(df_textos_paginas["publicacao"][0])

		df_textos_paginas.to_csv(path+"\Diarios_publicacoes_TRF1_DJEN_2021_"+str(df_textos_paginas["nomes_pastas"][0])+'_'+str(n)+".csv", index = False)

	fim = time.time()
	tempo_total = (fim-ini)//60 #calcula o tempo decorrido
	print("O tempo de execução foi aproximadamente =", tempo_total,"minutos")

###################################################################

if __name__ == "__main__":
	main()