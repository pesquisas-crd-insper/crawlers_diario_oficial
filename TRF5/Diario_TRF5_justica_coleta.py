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
from selenium.webdriver.support.ui import Select
import random




###############  Função que confere se os download terminaram ######################

def downloads_done(path_final):
	print()
	print("estamos verificando na pasta:", path_final)
	cont = 0
	desist = 0
	while True:
		if cont == 1 or desist == 4:  # limite de 3 documentos ou 4 tentativas
			break
		else:
			print("aguardando 7 seg") # 15 segundos para cada tentativa
			print("-----")
			time.sleep(7)
			cont = 0
			# total = os.listdir(path_final) # lista os donwloads em andamento
			
			# if len(total) == 0: # se nada estiver sendo baixado, cancela o processo.
			# 	cont = 1
			# else:
			for i in os.listdir(path_final):
				nome = str(i)
				if "crdown" not in nome and nome[-3:] == "pdf":  # confere os downloads finalizados
					cont = cont+1
					
			# desist = desist + 1 # conta as tentativas

			print("Ainda falta(m)", 1-cont,"arquivos")
			print("---------------")
					
	print("downloads finalizados")
	return


#####################################################################################################################

def Baixar_diarios(ano):


	# separa o ano e cria o diretório, caso não exista
	dir_path = str(os.path.dirname(os.path.realpath(__file__)))
	path = dir_path + f'\Diarios_TRF5_provisorio'+str(ano)
	Path(path).mkdir(parents=True, exist_ok=True)
    
	chromedriver_path = Path(str(Path(__file__).parent.resolve()) + '\software\chromedriver.exe')

	## configurações do driver
	options = Options()
	prefs = {'download.default_directory' : path}
	options.add_experimental_option('prefs', prefs)
	options.add_argument('--ignore-certificate-errors')
	options.add_argument("--window-size=1920x1800")
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	driver = webdriver.Chrome(executable_path = chromedriver_path, options=options)
	ua = UserAgent()
	url = 'https://diariointernet.trf5.jus.br/diarioeletinternet/paginas/consultas/consultaDiario.faces'
	driver.get(url)
	time.sleep(4)
	html_source = driver.page_source

	# meses = ['01','02','03','04','05','06','07','08','09','10','11','12']
	meses = ['01','02','03','04']
	# meses = ['02']
	tribunais = ['5','80','81','82','83','84','85']
	# meses = ['10']
	# tribunais = ['84','85']
	nomes_tribunais =["TRF5","AL","CE","PB","PE","RN","SE"]
	# nomes_tribunais =["RN","SE"]
	
	cadernos = ['1']
	
	for mes in meses:
		for tribunal in tribunais:
			for caderno in cadernos:
				if ano == '2010' and mes == '01' and tribunal == '5' and caderno == '1':
					form_tribunal = Select(driver.find_elements_by_xpath('//*[@id="frmVisao:orgao"]')[0])
					form_tribunal.select_by_value(tribunal)
					time.sleep(1)
					form_caderno = Select(driver.find_elements_by_xpath('//*[@id="frmVisao:edicao"]')[0])
					form_caderno.select_by_value(caderno)
					time.sleep(1)
					form_ano = Select(driver.find_elements_by_xpath('//*[@id="frmVisao:periodo"]')[0])
					form_ano.select_by_value(ano)
					time.sleep(1)
					driver.find_elements_by_xpath('//*[@id="frmVisao:j_id48"]')[0].click()
					try:
					    Select(driver.find_elements_by_xpath('//*[@id="frmPesquisa:quantidadeRegistros"]')[0]).select_by_value('100')
					except:
					    continue
					time.sleep(3)
					if len(driver.find_elements_by_xpath('//*[@href="#"]')) > 2 :
					    lista = driver.find_elements_by_xpath('//*[@href="#"]')[2:]
					    for link in lista:
					        link.click()
					        time.sleep(2)
				else:
				    form_tribunal = Select(driver.find_elements_by_xpath('//*[@id="frmVisao:orgao"]')[0])
				    form_tribunal.select_by_value(tribunal)
				    time.sleep(1)
				    form_caderno = Select(driver.find_elements_by_xpath('//*[@id="frmVisao:edicao"]')[0])
				    form_caderno.select_by_value(caderno)
				    time.sleep(1)
				    form_ano = Select(driver.find_elements_by_xpath('//*[@id="frmVisao:periodo"]')[0])
				    form_ano.select_by_value(ano)
				    time.sleep(1)
				    form_mes = Select(driver.find_element_by_xpath('//*[@id="frmVisao:meses"]'))
				    form_mes.select_by_value(mes)
				    time.sleep(2)
				    driver.find_elements_by_xpath('//*[@id="frmVisao:j_id48"]')[0].click()
				    try:
				        Select(driver.find_elements_by_xpath('//*[@id="frmPesquisa:quantidadeRegistros"]')[0]).select_by_value('100')
				    except:
				        continue
				    time.sleep(3)
				    if len(driver.find_elements_by_xpath('//*[@href="#"]')) > 2 :
				        lista = driver.find_elements_by_xpath('//*[@href="#"]')[2:]
				        datas = driver.find_elements_by_xpath("/html/body/div/div/div[4]/form[2]/div/table/tbody/tr/td/table/tbody/tr")
				        
				        # pega o nome do tribunal
				        index_trib = tribunais.index(tribunal)
				        nome_tribunal = nomes_tribunais[index_trib]
				        print("***********************")
				        print(nome_tribunal)
				        print()
				        print("***********************")
				        for link,data in zip(lista,datas):
				        	texto_data = str(data.text.encode("utf-8").decode("utf-8"))
				        	data_ajus = texto_data.split(" ")[-1]
				        	data_ajus = data_ajus.replace("/","-")
				        	print(data_ajus)
				        	# print(texto_data)
				        	
				        	# cria o diretório da pasta
				        	path_final = dir_path + f'\Diarios_TRF5_'+nome_tribunal+"_"+ano+'\\'+data_ajus
				        	Path(path_final).mkdir(parents=True, exist_ok=True)
				        	# clica para baixar o arquivo
				        	link.click()
				        	time.sleep(2)
				        	# verifica se o download acabou
				        	downloads_done(path)
				        	# move o arquivo para o diretório da data
				        	
				        	for i in os.listdir(path):
				        		nome = str(i)
				        		if nome[-3:] == "pdf":  # confere os downloads finalizados
				        			source = os.path.join(path, nome)
				        			try:
				        				nome_final = os.path.join(path,nome_tribunal+"_"+ano+'_'+data_ajus+".pdf")
				        				os.rename(source,nome_final)
				        				shutil.move(nome_final,path_final)
				        			except:
				        				n = random.randint(0,5000)
				        				nome_final_n = os.path.join(path,nome_tribunal+"_"+ano+'_'+data_ajus+"_"+str(n)+".pdf")
				        				os.rename(nome_final,nome_final_n)
				        				shutil.move(nome_final_n,path_final)
				        	time.sleep(4)
				        	print("                ---------------------------")		
                            

	driver.quit()                        


# Chama as funções


def main():
	ano = input("digite o ano(ex: 2012):")
	Baixar_diarios(ano)

#################################

if __name__ == "__main__":
	main()
