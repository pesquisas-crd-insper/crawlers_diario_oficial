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




def Baixar_diarios(ano):

	if int(ano) > 2019:
		colet_2020_adiante(ano)


def main():
	ano = input("digite o ano(ex: 2012):")
	Baixar_diarios(ano)

#################################

if __name__ == "__main__":
	main()