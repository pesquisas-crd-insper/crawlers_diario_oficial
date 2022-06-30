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
import base64
import fitz
import shutil


#####################################################################


def Convert_data(data):
   
    data_ajus = data[6:8]+"-"+data[4:6]+"-"+data[0:4]
    # print(data_ajus)

    # print(data_ajus)
    # z= input("")
    
    return data_ajus

######################  Função que verifica se os downloads acabaram #######################

def downloads_done(path_final):

    print()
    print("estamos verificando na pasta:", path_final)
    cont = 0
    desist = 0
    while True:
        if cont == 1 or desist == 4:  # contagem do documento ou das desistências
            break
        else:
            print("aguardando 6 seg")   # tempo de 15 segundos para cada tentativa
            print("-----")
            time.sleep(6)
            cont = 0
            total = os.listdir(path_final) #lista os casos no diretório
            
            if len(total) == 0: # se nada estiver em processo, cancelar.
                cont = 1
            else:
                for i in os.listdir(path_final):
                    nome = str(i)
                    if nome[-3:] == "pdf":  # verifica se o documento foi baixado
                        cont = cont+1
                        print("temos", cont, "arquivos baixados")
                desist = desist + 1

                print("Download em andamento. Aguarde")
                print("---------------")
                    
    print("downloads finalizados")
    return


######################## função para gerar os números das edições de cada ano #################################

def gerar_numeros():

    linha = 0
    arq = open('EDICOES.txt', 'r') # abre o range das edições do ano escolhido pelo usuário no arquivo TXT
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
    pst = "todos"

    # gera o diretório do ano
    dir_path = str(os.path.dirname(os.path.realpath(__file__)))
    path = dir_path + f'\Diarios_TRF4_'+pst
    Path(path).mkdir(parents=True, exist_ok=True)


    # gera o range do ano
    edicoes = gerar_numeros()

    for ed in edicoes:

        # configurações do Chrome
        chromedriver_path = Path(str(Path(__file__).parent.resolve()) + '\software\chromedriver.exe')
        

        # cria o diretório com o nome da data
        path_final = dir_path + f'\Diarios_TRF4_'+str(pst)+'\\'+str(ed)
        Path(path_final).mkdir(parents=True, exist_ok=True)
        
        # Configurações do Chrome driver
        options = Options()
        prefs = {'download.default_directory' : path_final}
        options.add_experimental_option('prefs', prefs)
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--window-size=1920x1800")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(executable_path = chromedriver_path, options=options)
        ua = UserAgent()

        # URL recebendo os elemento da data e o link
        link_final = 'https://www.trf4.jus.br/trf4/diario/download.php?id_publicacao='+str(ed)
        print(link_final)
        

        # requisição do site 
        driver.get(link_final)
        time.sleep(3)


        # verifica o download
        downloads_done(path_final)

        # encerra o processo
        driver.quit()


    # verifica a data e se é adm pelo nome do arquivo e move a pasta para o diretório do ano
        # iteração sobre as páginas
        arquivos = os.listdir(path_final)
        for item in arquivos:
            if "adm" in item:
                nome_arquivo = os.path.join(path_final, item)
                os.remove(nome_arquivo)
                print("arquivo administrativo. Deletado!")

        arquivos = os.listdir(path_final)
        if len(arquivos) > 0:        
            for b in range(len(arquivos)):
                parts = arquivos[b].split("_")
                # print(parts)
                data = parts[2][:8]
                # print(data)
                # z= input("")
                data_format = Convert_data(data)

                path_anual = dir_path + f'\Diarios_TRF4_'+data[:4]+'\\'+str(data_format)
                Path(path_anual).mkdir(parents=True, exist_ok=True)

                nome_arquivo = os.path.join(path_final, arquivos[b])
                shutil.move(nome_arquivo,path_anual)
                os.rmdir(path_final)



                # nome_arquivo = os.path.join(path_final, arquivos[b])
                # with fitz.open(nome_arquivo) as pdf:    
                #     for n in range(1):

                #         blocks = pdf[n].get_text("dict")['blocks']

                #         for o in range(len(blocks)): 
                #             # print(blocks[o])
                #             # z= input("")
                #             try: # elimina os blocos que não contém "lines" e consequentemente não tem textos
                                
                #                 lines = blocks[o]["lines"] # separa as linhas
                                
                #                 txt_block = []  
                                
                #                 for x in range(len(lines)):
                #                     spans = lines[x]["spans"] # separa os spans
                                    
                #                     for u in spans:
                #                         print(u['text'])
                #                         z= input("")

                #                         # if re.search('disponibiliza(ção|çã):*',u['text'], re.IGNORECASE):

                #                                     # função para pegar a data e retorna a data
                #                                      # cria o diretório do ano se não existir
                #                                     # move para o diretório do ano
                #             except:
                #                 pass
        else:
            print("pasta vazia. Diretório removido!")
            os.rmdir(path_final)                        
                       

######################################       ***     ###################################################


if __name__ == "__main__":
    main()
