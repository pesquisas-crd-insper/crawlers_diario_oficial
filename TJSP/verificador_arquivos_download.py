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
from workalendar.america import Brazil
import shutil
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PyPDF2 import PdfFileReader, PdfFileMerger
import shutil
import time
import os, re
import numpy as np
import fitz
from Diario_SP_justica_coleta import Baixar_diarios



## verifica a quantidade de arquivos pdf na pasta

def verificar_quantidade_arq(path):

	cont = 0
	for i in os.listdir(path): #lista os arquivos
		nome = str(i)
		if nome[-3:] == "pdf": # verifica os concluídos
			cont = cont+1

	if cont < 5:
		return -1
	else:
		return 1		



#verifica se os arquivos estão corrompidos

def Verificar_validade(nome_pasta,arquivos,pasta_dia):

	
	for a in range(len(arquivos)):
		# print(arquivos[a])
		nome = os.path.join(nome_pasta, arquivos[a])

		# iteração sobre os pdf e as suas respectivas páginas coletando os dados
		try:
			with fitz.open(nome) as pdf:
			    for pagina in pdf:
			        texto = pagina.get_text()
			    return 1
		except:
			return -1



#separa as datas com problemas e faz a coleta novamente

def Main_Separacao(ano):

	datas = []

	# diretório
	diret = r'./Diarios_SP_'+ano


	# iteração sobre as páginas
	pastas = os.listdir(diret)



	# iteração sobre as patas e os arquivos
	for b in tqdm(range(len(pastas))):
		
		nome_pasta = os.path.join(diret, pastas[b])
		verif = verificar_quantidade_arq(nome_pasta)
		if verif == 1:
			arquivos = os.listdir(nome_pasta)

			# verificar a validade
			validade = Verificar_validade(nome_pasta,arquivos,pastas[b])
			if validade != 1:
				data = data.replace("/","-")
				ano_pasta = str(data[-4:])		
				dir_path = str(os.path.dirname(os.path.realpath(__file__)))
				path = dir_path + f'\Diarios_SP_erradas_'+ano_pasta
				Path(path).mkdir(parents=True, exist_ok=True)
				shutil.move(nome_pasta,path)
				datas.append(pastas[b])


		else:
			data = pastas[b].replace("/","-")
			ano_pasta = str(data[-4:])		
			dir_path = str(os.path.dirname(os.path.realpath(__file__)))
			path = dir_path + f'\Diarios_SP_erradas_'+ano_pasta
			Path(path).mkdir(parents=True, exist_ok=True)
			shutil.move(nome_pasta,path)
			datas.append(data)


	Baixar_diarios(datas)


#inicia o processo

def main():

	ini = time.time()
	ano = input("Digite o ano com 4 dígitos (Ex:2012):")
	data_frames = Main_Separacao(ano)
	fim = time.time()
	tempo_total = (fim-ini)//60 #calcula o tempo decorrido
	print("O tempo de execução foi aproximadamente =", tempo_total,"minutos")


if __name__ == "__main__":
	main()




