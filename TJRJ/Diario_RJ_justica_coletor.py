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

# Imports Selenium (Navegador Web)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PyPDF2 import PdfFileReader, PdfFileMerger
import shutil
import time
import datetime
from datetime import date
from datetime import datetime
from workalendar.america import Brazil
import shutil
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


#############################################  Função que baixa os diários #####################################

def Baixar_diarios(datas):


	# formata o ano e cria o diretório
	ano = str(datas[0][-4:])
	dir_path = str(os.path.dirname(os.path.realpath(__file__)))
	path = dir_path + f'\Diarios_RJ_'+ano
	Path(path).mkdir(parents=True, exist_ok=True)


	# itera sobre cada data 
	for data in datas:

		# configurações do Chrome driver
		chromedriver_path = Path(str(Path(__file__).parent.resolve()) + '\software\chromedriver.exe')

		#formata a data e cria o diretório
		data_pasta = data.replace("/","-")
		path_final = dir_path + f'\Diarios_RJ_'+ano+'\\'+data_pasta
		Path(path_final).mkdir(parents=True, exist_ok=True)
		# faz o request do site
		link_inicial ="https://www3.tjrj.jus.br/consultadje/pdf.aspx?dtPub={}&caderno={}&pagina=-1&dc=" # URL utilizada para baixar os cadernos.

		cadernos = ["S", "C", "I"]

		print(data)
		for cad in cadernos:
			try:
				print(link_inicial.format(data, cad))
				response = urllib.request.urlopen(link_inicial.format(data, cad), timeout = 30)
				file = open(path_final+"/"+ str(data.replace("/","-")) + "_" + cad + ".pdf", "wb")
				file.write(response.read())
				time.sleep(1)
				file.close()
			except:
				print("não tem o caderno", cad)  
        
		# iteração sobre as páginas
        arquivos = os.listdir(path_final)

        for b in tqdm(range(len(arquivos))):
        
            nome_arquivo = os.path.join(path_final, arquivos[b])
            try:
                with fitz.open(nome_arquivo) as pdf:
                    textos = []
                    for n in range(1):
                        texto = pdf[n].get_text()
                        textos.append(texto)
            except:
                print("arquivo", arquivos[b],"corrompido. Apagado!")
                os.remove(nome_arquivo)  


#####################################################

def Gera_dias_uteis():

	# usuário escolhe as datas inicias e finais

	inicial = input("digite a data inicial(dd-mm-aaaa): ")
	final = input("digite a data final(dd-mm-aaaa): ")

	# converte as strings da data para o formato data

	data_inicial = datetime.strptime(inicial, '%d-%m-%Y').date()
	data_final = datetime.strptime(final, '%d-%m-%Y').date()

	date_list = pd.date_range(start= data_inicial, end = data_final) # gera a lista de datas
	# print(date_list)

	ano = int(date_list[0].strftime("%Y")) #separa o ano
	

	# seleciona as datas do calendário brasileiro do ano
	cal = Brazil()
	cal.holidays(ano)


	# gera a lista de datas com os dias úteis
	datas = []
	for item in date_list:
		ano = int(item.strftime("%Y"))
		mes = int(item.strftime("%m"))
		dia = int(item.strftime("%d"))
		if cal.is_working_day(date(ano,mes,dia)):
			data = item.strftime("%d/%m/%Y")
			# print("date:",data)
			datas.append(data)

	# print(datas)
	return datas


######################################################

def Main():
	# chama as funções
	datas = Gera_dias_uteis()			
	Baixar_diarios(datas)


##########################

if __name__ == "__main__":
	Main()