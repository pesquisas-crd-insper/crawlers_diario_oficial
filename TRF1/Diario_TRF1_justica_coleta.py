# Imports de bibliotecas
import os,re
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



def colet_2015_2020(ano):

	dir_path = str(os.path.dirname(os.path.realpath(__file__)))
	
	if int(ano) == 2015:
		inicio = 0
		fim = 34
	elif int(ano) == 2016:
		inicio = 11
		fim = 50
	elif int(ano) == 2017:
		inicio = 14
		fim = 55
	elif int(ano) == 2018:
		inicio = 111
		fim = 151
	elif int(ano) == 2019:
		inicio = 23
		fim = 66
	elif int(ano) == 2020:
		inicio = 28
		fim = 65

	for k in range(inicio,fim):
		url = 'https://sistemas.trf1.jus.br/edj/discover?rpp=100&etal=0&query={}&scope=123/1&group_by=none&page={}&sort_by=dc.date.issued_dt&order=asc&filtertype_0=title&filtertype_1=title&filter_relational_operator_1=contains&filter_relational_operator_0=contains&filter_1=&filter_0='.format(ano,k)
		response = urllib.request.urlopen(url)
		soup = BeautifulSoup(response, 'html.parser')
		base = 'https://sistemas.trf1.jus.br'
		# print(soup)


		for link in soup.find_all('a', attrs={'href': re.compile("edj/handle/123")}):
			text_link = link.get_text()
			if "dici" in text_link and str(ano) in text_link:
				print("-------------")
				print(text_link)
			# 	print("-----------------------")
			# else:
			# 	pass
				nome_link = link.get('href')
				link_final = base+nome_link

				textos = text_link.split(" ")

				estado = textos[3].replace("SJ","")
				itens_data = textos[-1].split("-")


				data_ajust = str(itens_data[2])+"-"+itens_data[1]+"-"+itens_data[0]

				
				print()
				print(estado)
				print(data_ajust)
				print(link_final)
				print()
				# print("-------------")

				response_2 = urllib.request.urlopen(link_final)
				soup_2 = BeautifulSoup(response_2, 'html.parser')
				count = 0

				base_2 = 'https://sistemas.trf1.jus.br'
				for link_2 in soup_2.find_all('a'):
					nome_link_pdf = link_2.get('href')
					if ".pdf" in str(nome_link_pdf) and count == 0:
						print(nome_link_pdf)
						count = 1

						partes = nome_link_pdf.split("/")
						nome_arquivo, nada = partes[-1].split('.pdf')

						link_final_pdf = base_2+nome_link_pdf
						
						path_final = dir_path + f'\Diarios_TRF1_'+str(estado)+"_"+str(itens_data[0])+'\\'+str(data_ajust)
						Path(path_final).mkdir(parents=True, exist_ok=True)

						response_3 = urllib.request.urlopen(link_final_pdf, timeout = 30)
						file = open(path_final+"/"+nome_arquivo+".pdf", "wb")
						file.write(response_3.read())
						time.sleep(2)
						file.close()
				print("-------------")		



def colet_2020_adiante(ano):

	regex_estado = re.compile(r"AC|AP|AM|BA|DF|GO|MA|MT|MG|PA|PI|RO|RR|TO|TRF")

	# separa o ano e cria o diretório, caso não exista
	dir_path = str(os.path.dirname(os.path.realpath(__file__)))

    
	chromedriver_path = Path(str(Path(__file__).parent.resolve()) + '\software\chromedriver.exe')

	url = 'https://portal.trf1.jus.br/portaltrf1/publicacoes/edjf1/edjf1.htm'
	response = urllib.request.urlopen(url)
	soup = BeautifulSoup(response, 'html.parser')


	cont = 0
	for link in soup.find_all('a', attrs={'href': re.compile("derno")}):
		print("estamos no link",cont)
		texto = link.get_text()
		if str(ano) in texto and "ditais" not in texto:
			print("-------------")
			print(texto)
			partes_txt = texto.split(" ")
			for item in partes_txt:
				if re.search(r"\/",item):
					data_ajust = item.replace("/","-")
			
			nome_link = link.get('href')
			partes = nome_link.split("/")
			nome_arquivo = partes[-1]
			nome_parseado = nome_arquivo.split("_")
			for part in nome_parseado:
				if re.search(regex_estado,part):
					estado = part

			# print("-------------")
			print()
			print(estado)
			print(data_ajust)
			print(nome_arquivo)
			print()
			print("-------------")
			path_final = dir_path + f'\Diarios_TRF1_'+str(estado)+"_"+str(ano)+'\\'+str(data_ajust)
			Path(path_final).mkdir(parents=True, exist_ok=True)		
			link_ajust = nome_link.replace("../../..", "https://portal.trf1.jus.br")

			response_2 = urllib.request.urlopen(link_ajust, timeout = 30)
			file = open(path_final+"/"+nome_arquivo+".pdf", "wb")
			file.write(response_2.read())
			time.sleep(2)
			file.close()
		cont = cont+1


def colet_2009_2015(ano):

	dir_path = str(os.path.dirname(os.path.realpath(__file__)))
	
	for k in range(0,601,100):
		# print(k)
		url = 'https://portal.trf1.jus.br/dspace/simple-search?query=&filter_field_1=dateIssued&filter_type_1=equals&filter_value_1={}&sort_by=score&simple-search-type=null&custom-query=null&order=desc&rpp=100&etal=0&start={}'.format(ano,k)
		response = urllib.request.urlopen(url)
		soup = BeautifulSoup(response, 'html.parser')
		base = 'https://portal.trf1.jus.br'
		# print(soup)


		for link in soup.find_all('a', attrs={'href': re.compile("dspace/handle/123")}):
			text_link = link.get_text()
			if str(ano) in text_link and "iário" in text_link:
				print("-------------")
				print(text_link)
			# 	print("-----------------------")
			# else:
			# 	pass
				nome_link = link.get('href')
				link_final = base+nome_link
				# print(link_final)
				textos = text_link.split(" ")

				estado = "TRF"
				data_ajust = textos[-1].replace("/","-")
				
				print()
				print(estado)
				print(data_ajust)
				print(link_final)
				print()
				# print("-------------")

				response_2 = urllib.request.urlopen(link_final)
				soup_2 = BeautifulSoup(response_2, 'html.parser')
				count = 0

				base_2 = 'https://portal.trf1.jus.br'
				for link_2 in soup_2.find_all('a'):
					nome_link_pdf = link_2.get('href')
					if ".pdf" in str(nome_link_pdf) and count == 0:
						print(nome_link_pdf)
						count = 1

						partes = nome_link_pdf.split("/")
						nome_arquivo, nada = partes[-1].split('.pdf')

						link_final_pdf = base_2+nome_link_pdf
						
						path_final = dir_path + f'\Diarios_TRF1_'+str(estado)+"_"+str(ano)+'\\'+str(data_ajust)
						Path(path_final).mkdir(parents=True, exist_ok=True)

						response_3 = urllib.request.urlopen(link_final_pdf, timeout = 30)
						file = open(path_final+"/"+nome_arquivo+".pdf", "wb")
						file.write(response_3.read())
						time.sleep(2)
						file.close()
				print("-------------")



def Baixar_diarios(ano):

	if int(ano) > 2020:
		colet_2020_adiante(ano)
	elif int(ano) == 2020:
		colet_2020_adiante(ano)
		colet_2015_2020()
	elif 2015 < int(ano) < 2020:
		colet_2015_2020(ano)
	elif int(ano) == 2015:
		colet_2015_2020(ano)
		colet_2009_2015(ano)
	elif int(ano) < 2015:
		colet_2009_2015(ano)
		


def main():
	ano = input("digite o ano(ex: 2012):")
	Baixar_diarios(ano)

#################################

if __name__ == "__main__":
	main()