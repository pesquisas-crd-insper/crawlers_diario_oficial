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
from Diario_AM_justica_coleta import Baixar_diarios
from Diario_AM_justica_coleta import Gera_dias_uteis




def eliminar_vazias(path):

	corrompido = 0
	total = 0
	for i in os.listdir(path): #lista os arquivos
		nome = str(i)
		if "pdf" in nome:
			total = total + 1

	if total == 0:
		print("-"*10)
		print("pasta:",path,"vazia")
		print("-"*10)
		return -1
	else:
		return 1	


def eliminar_vazias_inacabadas(path):

	corrompido = 0
	total = 0
	for i in os.listdir(path): #lista os arquivos
		nome = str(i)
		if "crdownload" in nome: # verifica os concluídos
			corrompido = 1
		else:
			if "pdf" in nome:
				total = total + 1

	if corrompido == 1 or total == 0:
		# print("-"*10)
		# print("arquivo",path,"com download não terminado ou pasta vazia")
		# print("-"*10)
		return -1
	else:
		return 1	



#verifica se os arquivos estão corrompidos

def Verificar_validade(nome_pasta,arquivos,pasta_dia):


	
	for a in range(len(arquivos)):
		# print(arquivos[a])
		nome = os.path.join(nome_pasta, arquivos[a])

		# iteração sobre os pdf e as suas respectivas páginas coletando os dados
		# try:
		print(nome)
		with fitz.open(nome) as pdf:
			textos = []
			for pagina in pdf:
				texto = pagina.get_text()
				textos.append(texto)

			textos = " ".join(textos)	
			if len(textos) > 1:
				# print("ok")
				return 1
			else:
				# print("arquivo corrompido!") 
				return -1



def Main_Separacao(ano):

	datas = []

	# diretório
	diret = r'./Diarios_AM_'+ano

	dir_path = str(os.path.dirname(os.path.realpath(__file__)))
	path = dir_path + f'\Diarios_AM_erradas_'+str(ano)
	Path(path).mkdir(parents=True, exist_ok=True)

	# iteração sobre as páginas
	pastas = os.listdir(diret)



	# com a lista de datas verificar os arquivos

	# iteração sobre as patas e os arquivos
	for b in tqdm(range(len(pastas))):
		
		nome_pasta = os.path.join(diret, pastas[b])
		verif = eliminar_vazias_inacabadas(nome_pasta)


		if verif == 1:
			arquivos = os.listdir(nome_pasta)
			# verificar a validade
			validade = Verificar_validade(nome_pasta,arquivos,pastas[b])
			

			if validade == -1:			
				shutil.move(nome_pasta,path)
				
		else:		
			shutil.move(nome_pasta,path)


			

	# gera as datas faltantes
	dt = Gera_dias_uteis()
	dt = [data.replace("/","-") for data in dt]

	diferentes = [data for data in dt if data not in pastas]

	print(diferentes)

	for pst in diferentes:
		path_final = dir_path + f'\Diarios_AM_erradas_'+str(ano)+'\\'+pst
		Path(path_final).mkdir(parents=True, exist_ok=True)


	datas = os.listdir(dir_path + f'\Diarios_AM_erradas_'+str(ano))

	# datas = datas[0:1]
	Baixar_diarios(datas)


	# deletar o diretório das erradas
	shutil.rmtree(path)

	# z = input("")

	# criar de novo o diretório vaziodas erradas
	path = dir_path + f'\Diarios_AM_erradas_'+str(ano)
	Path(path).mkdir(parents=True, exist_ok=True)

	# conferir a validade de novo e criar um novo diretório de erradas definitivo 
	
	# z = input("")

	pastas = os.listdir(diret)

	for b in tqdm(range(len(pastas))):
		
		nome_pasta = os.path.join(diret, pastas[b])
		verif = eliminar_vazias_inacabadas(nome_pasta)


		if verif == 1:
			arquivos = os.listdir(nome_pasta)
			# verificar a validade
			validade = Verificar_validade(nome_pasta,arquivos,pastas[b])

			if validade == -1:			
				shutil.move(nome_pasta,path)
				
		else:		
			shutil.move(nome_pasta,path)


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
