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
import fitz




def colet_2020_adiante(ano):

	# separa o ano e cria o diretório, caso não exista
	dir_path = str(os.path.dirname(os.path.realpath(__file__)))

    
	chromedriver_path = Path(str(Path(__file__).parent.resolve()) + '\software\chromedriver.exe')

	url = 'https://portal.trf1.jus.br/portaltrf1/publicacoes/edjf1/edjf1.htm'
	response = urllib.request.urlopen(url)
	soup = BeautifulSoup(response, 'html.parser')


	for link in soup.find_all('a'):
		if "Caderno" in str(link):
			nome_link = link.get('href')
			# print(nome_link)
			partes = nome_link.split("/")
			nome_arquivo = partes[-1]
			nome_parseado = nome_arquivo.split("_")
			estado = nome_parseado [1]
			data = nome_parseado[2]
			itens_data = data.split("-")

			if itens_data[0] == ano and "EDT" not in str(link):
				data_ajust = str(itens_data[2])+"-"+itens_data[1]+"-"+itens_data[0]
				print("-------------")
				print()
				print(data_ajust)
				print(nome_arquivo)
				print()
				print("-------------")
				path_final = dir_path + f'\Diarios_TRF1_'+str(estado)+"_"+str(itens_data[0])+'\\'+str(data_ajust)
				Path(path_final).mkdir(parents=True, exist_ok=True)
				link_ajust = nome_link.replace("../../..", "https://portal.trf1.jus.br")
				
				response_2 = urllib.request.urlopen(link_ajust, timeout = 30)
				file = open(path_final+"/"+nome_arquivo+".pdf", "wb")
				file.write(response_2.read())
				time.sleep(2)
				file.close()	
			# z= input("")


def colet_2015_2020(ano):

	dir_path = str(os.path.dirname(os.path.realpath(__file__)))

	for k in range(1252,1350):#26653):
		url = 'https://sistemas.trf1.jus.br/edj/handle/123/'+str(k)
		print("--------------------")
		print()
		print(url)
		try:
			response = urllib.request.urlopen(url)
			soup = BeautifulSoup(response, 'html.parser')
			# print(soup)
			# z = input("")
			base = 'https://sistemas.trf1.jus.br'
			count = 0
			for link in soup.find_all('a'):
				nome_link = link.get('href')
				if "Caderno" in str(nome_link) and count == 0 and ano in str(nome_link):
					print(nome_link)
					count = 1
					# z= input("")
					link_final = base+nome_link
					partes = nome_link.split("/")
					nome_arquivo, nada = partes[-1].split('.pdf')
					nome_parseado = nome_arquivo.split("_")
					estado = nome_parseado [2]
					data = nome_parseado[3]
					itens_data = data.split("-")
					data_ajust = str(itens_data[2])+"-"+itens_data[1]+"-"+itens_data[0]

					if "JUD" in nome_arquivo:
						print("-------------")
						print()
						print(data_ajust)
						print(nome_arquivo)
						print()
						print("-------------")
						path_final = dir_path + f'\Diarios_TRF1_'+str(estado)+"_"+str(itens_data[0])+'\\'+str(data_ajust)
						Path(path_final).mkdir(parents=True, exist_ok=True)
											
						response_2 = urllib.request.urlopen(link_final, timeout = 30)
						file = open(path_final+"/"+nome_arquivo+".pdf", "wb")
						file.write(response_2.read())
						time.sleep(2)
						file.close()
				# else:
					# print("link que não remete ao documento ou que não pertence ao ano buscado")
		except:
			pass
			# print("não possui link válido")




def Baixar_diarios(ano):

	if int(ano) > 2020:
		colet_2020_adiante(ano)
	elif int(ano) == 2020:
		colet_2020_adiante(ano)
		colet_2015_2020(ano)
	elif 2015 < int(ano) < 2020:
		colet_2015_2020(ano)
	elif int(ano) == 2015:
		colet_2015_2020(ano)
		print("e o outro abaixo")
	elif int(ano) < 2015:
		print("ainda vai ser feito!")


def main():
	ano = input("digite o ano(ex: 2012):")
	Baixar_diarios(ano)

#################################

if __name__ == "__main__":
	main()