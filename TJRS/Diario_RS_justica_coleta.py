import requests
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
from pathlib import Path
import sys, re, time, os, urllib.request
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
import fitz

def downloads_done(path_final, quantidade):
	
	print()
	print("estamos verificando na pasta:", path_final)
	
	cont = 0 # quantidade total de documentos
	desist = 0 # momento de desistência caso o site demore muito para responder
	
	while True:
		if cont > quantidade: # se a contagem identificar o mesmo número de item da quantidade total
			break # encerra o processo
		
		else:
			print("aguardando 15 seg") # caso não seja ele aguarda 15 seg
			print("-----")
			time.sleep(4)
			cont = 0
			total = os.listdir(path_final) # faz a listagem da quantidade na pasta
			
			if len(total) == 0: 
				cont = quantidade # se depois de 15 seg ele verificar que não tem nada sendo baixado ele encerra o processo
			
			else:
				for i in os.listdir(path_final): # caso haja downloads em curso ele verifica se todos já estão completos (extensão ".pdf")
					nome = str(i)
					if nome[-3:] == "pdf": 
						cont = cont+1  # E conta quantos tem depois de iterar todos os elementos da pasta
	
				desist = desist + 1 # acrescenta 1 a desistência em cada verificação na pasta
				if desist == (quantidade+2): # se a desistência atingir a quantidade total + 2 elementos, ele desiste (ou seja, pelo menos 30s de tempo extra)
					cont = quantidade

				print("Ainda falta(m)", quantidade-cont,"arquivos") # indica para o usuário quantos ainda faltam
				print("---------------")

					
	print("downloads finalizados!") # informa o encerramento do processo, acabado ou não.
	return


######################## função para gerar os números das edições de cada ano #################################

def gerar_numeros(ano):

    anos_todos = ["2012","2013","2014","2015","2016","2017","2018","2019","2020","2021"]
   
    linha = anos_todos.index(ano)
    arq = open('ANOS.txt', 'r') # abre o range das edições do ano escolhido pelo usuário no arquivo TXT
    linhas = arq.readlines() # lê o arquivo
    inic_fim = linhas[linha].split('-') # seleciona a linha do ano respectivo

    
    lista_num =[] #lista com os números do range do ano
    inicio = int(inic_fim[0])  # documento inicial disponível
    fim = int(inic_fim[1])# documento final disponível

    # gera o range do ano
    atual = inicio
    for k in range(inicio, fim+1):
        lista_num.append(atual)
        atual = atual+1

    # retorna a lista    
    return lista_num    



####################### função para coletar os documentos  #####################################################

def main():

    # usuário escolhe o ano
    ano = input("Digite o ano com 4 dígitos (Ex: 2019):")

    # gera o diretório do ano
    dir_path = str(os.path.dirname(os.path.realpath(__file__)))
    path = dir_path + f'\Diarios_RS_'+ano
    Path(path).mkdir(parents=True, exist_ok=True)


    # gera o range do ano
    edicoes = gerar_numeros(ano)

    for ed in edicoes:

        # gera a pasta da edição

        print("baixando edição", ed, ' até a edição', edicoes[-1],"\n-------------")
        path_final = dir_path + f'\Diarios_RS_'+ano+'\\'+str(ed)
        Path(path_final).mkdir(parents=True, exist_ok=True)

        chromedriver_path = Path(str(Path(__file__).parent.resolve()) + '\software\chromedriver.exe')
        # configurações do Chrome para tamanho de tela, erros de certificado, driver e destino dos dowloads
        options = Options()
        prefs = {'download.default_directory' : path_final}
        options.add_experimental_option('prefs', prefs)
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--window-size=1920x1800")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(executable_path = chromedriver_path, options=options)
        ua = UserAgent()
        


        # configurações do Chrome para tamanho de tela, erros de certificado, driver e destino dos dowloads


        # faz o request do site
        link_inicial = "https://www.tjrs.jus.br/servicos/diario_justica/download_edicao.php?tp=%s&ed=%s" # URL utilizada para baixar os cadernos.
        
       	cadernos = ["0", "5", "7", "6"]
       	quantidade = 4

       	for e in cadernos:

            print(link_inicial % (e,str(ed)))
            driver.get(link_inicial % (e,str(ed)))
            time.sleep(2)
        
        # chama a função para verificar os andamentos dos downloads
        downloads_done(path_final, quantidade)
        
        # encerra a tela do Chrome
        driver.quit()

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
   
######################################       ***     ###################################################


if __name__ == "__main__":
    warnings.simplefilter('ignore', InsecureRequestWarning) # Retira a exibição dos erros de SSL.
    main()
