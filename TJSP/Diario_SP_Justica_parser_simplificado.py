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

import os, re
import datetime
import pandas as pd
import numpy as np
import shutil
from bs4 import BeautifulSoup
import fitz
from tqdm import tqdm
# from PDF_diario import Baixar_diarios_ajuste
import time
import json
# from array_Estados import Comarcas
# from tipos_processuais import tipos_processuais
# from assuntos import assuntos_proc



############################## função para separar os representantes (AOB/Estado) ####################################################

def sep_representante(public):

	rgx_estad = "(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO|DP)"

	# limpar o texto do ponto para separar melhor o número da OAB
	text_ajust = public.replace(".","")
	text_ajust = text_ajust.replace("\n","")
	# print(text_ajust)


	oabs = []
	# print(public)

	oab_compile = re.compile("\d{3,10}(?:[A-Z]/|/.|/|[A-Z]/.)[A-Z][A-Z]")
	oab_comp = oab_compile.findall(public)
	# print(len(oab_comp))
	# z=input("")
	if len(oab_comp) > 0:
		for item in oab_comp:
			oabs.append(item)
	else:
		partes = re.split("oab",text_ajust, flags=re.IGNORECASE)[1:]
		# print(partes)
		# z=input("")
		for item in partes:
			item = item.strip()
			try:
				# print("o item é:\n",item[:10],"\n ***************")
				num_oab = re.findall('\d{3,10}',item[:14])
				estado_oab = re.findall(rgx_estad,item[:14])
				# print("a OAB é:",num_oab,"\nE o Estado é:",estado_oab,"\n ----------------")
				oabs.append(str(num_oab[0]+"/"+estado_oab[0]))
			except:
				try:
					# print("o item é:\n",item[:],"\n ***************")
					num_oab = re.findall('\d{3,10}',item[:])
					estado_oab = re.findall(rgx_estad,item[:])
					# print("a OAB é:",num_oab,"\nE o Estado é:",estado_oab,"\n ----------------")		
					oabs.append(str(num_oab[0]+"/"+estado_oab[0]))
				except:
					pass
	

	# print(oabs)
	return oabs


############################################### # função que separa os textos dos PDF em páginas ######################################

def Separar_textos_paginas(nome_pasta,arquivos,pasta_dia):

		
	# lista onde os DF serão armazenados
	data_frames=[]	
	
	for a in range(len(arquivos)):
		print(nome_pasta)
		print(arquivos[a])
		nome = os.path.join(nome_pasta, arquivos[a])

		# listas que armazenarão os dados básicos 
		textos_paginas =[]
		numeros_paginas =[]
		nome_doc = []
		nomes_pastas =[]


		# iteração sobre os pdf e as suas respectivas páginas coletando os dados
		with fitz.open(nome) as pdf:
		    num_pag = 1
		    for pagina in pdf:
		        texto = pagina.get_text()
		        textos_paginas.append(texto)
		        numeros_paginas.append(num_pag)
		        nome_doc.append(arquivos[a])
		        nomes_pastas.append(pasta_dia)
		        num_pag = num_pag+1

		# para cada PDF gera um DF armazenado na lista
		    df_textos_paginas = pd.DataFrame()    
		    df_textos_paginas["textos_paginas"] = textos_paginas
		    df_textos_paginas["numeros_paginas"] = numeros_paginas
		    df_textos_paginas["nome_documento"] = nome_doc
		    df_textos_paginas["nomes_pastas"] = nomes_pastas

		    data_frames.append(df_textos_paginas)

	
	# print("temos",len(data_frames),"data Frames")

	# retorna os DFs	    
	return data_frames


##################################################### Função que corta as publicações  ###########################################################


def Cortar_publicacoes(df_textos_paginas):

	## listas onde serão armazenados os dados
	datas = []
	numeros_paginas =[]
	numeros_certos =[]
	trechos_certos = []
	docs_certos = []
	paginas_erros = []
	publis_erros = []
	datas_erros = []
	docs_errados = []
	pastas = []
	comarcas =[]
	oabs =[]
	tipos_proces =[]
	assuntos = []

	# termos = tipos_processuais()
	# # print(termos)

	# assuntos_list = assuntos_proc()

	# indica a quantidade de páginas do DF
	qtdade_paginas = df_textos_paginas["textos_paginas"] 


	# variável que armazena a parte do texto quado a publicação está dividida em mais de uma página (começa vazia)
	continuacao = ""

	# iteração sobre os elementos do DF (publicação, número, documento e pasta)
	for public, numero, doc, pasta in tqdm(zip(df_textos_paginas["textos_paginas"],df_textos_paginas["numeros_paginas"], df_textos_paginas["nome_documento"], df_textos_paginas["nomes_pastas"])):
		texto = str(public)
		num_pag = numero
		pasta = str(pasta)


		###################### versão anterior

		# Encontra os padrões textuais dos números CNJ nas publicações e retorna esses números

		numer = re.findall("\n\d{1,3}\. Processo \d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", texto)
		numer_2 = re.findall("\nProcesso \d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", texto)
		numer_3 = re.findall("\nNº \d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", texto)
		numer_4 = re.findall("\nProcesso: \d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", texto)
		numer_5 = re.findall("\n\d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}; Processo", texto)
		numer_6 = re.findall("\nN° \d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", texto)
		numer_7 = re.findall("\nPROCESSO\s\n:\d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", texto)
		numer_8 = re.findall("\n\d{3}\.\d{2}\.\d{4}\.\d{5,8}.\d{1,2}", texto)
		numer_9 = re.findall("\nPROCESSO:\d{3}\.\d{2}\.\d{4}\.\d{5,8}", texto)
		numer_10 = re.findall("\nProcesso nº.:.\d{3}\.\d{2}\.\d{4}\.\d{5,8}.\d{1,2}",texto)

		

		# unifica todos os números numa lista com todos os padrões
		numeros = numer + numer_2 + numer_3 +numer_4 + numer_5 + numer_6 + numer_7 + numer_8 + numer_9+numer_10

		##########################################
	

		# encontra os numeros dos processos para fazer o corte de acordo com a posição inicial do caracter
		# gera uma lista com a posição do caracter onde está cada número CNJ
		num_caract = []
		for item in numeros:
			num_caracter = texto.find(item)
			if num_caracter not in num_caract:
				num_caract.append(num_caracter)

			# tratamento para o caso de termos dois números CNJ iguaus na mesma página, ele verifica a próxima posição
			else:
				num_caracter = texto.find(item,num_caract[-1]+28,len(texto)) # por default são 28, porque é maior que um número CNJ
				num_caract.append(num_caracter)


		# insere o caracter final e orgniza a lista com os indices dos caracteres iniciais dos numeros dos processos em ordem
		num_caract.append(len(texto)-1)	
		num_caract.sort()
			

		#elimina os caracteres duplicados, se houver
		df_caract = pd.DataFrame()
		df_caract ["caracter"] = num_caract
		df_caract = df_caract.drop_duplicates(subset = "caracter")


		# transforma numa lista
		num_caract = df_caract ["caracter"].to_list()



		# gera a lista com os números dos caracteres para fazer os cortes e gera a lista com as publis separadas
		# aqui teremos o número do caracter do começo e do final para cada recorte
		publis = []
		num_comec = 0
		for h in range(len(num_caract)):
			trecho = texto [num_comec:num_caract[h]]
			trecho = trecho.strip()
			publis.append(trecho)
			num_comec = num_caract [h]


		# limpa o cabeçalho
		padroes = ["Publicação Oficial do Tribunal de Justiça.+\n","Disponibilização:.+\n","Diário da Justiça.+\n",".+Edição.+"]
		for item in padroes:
			elim = re.findall(item,publis[0])
			if len(elim) > 0:
				for p in elim:
					publis[0] = publis[0].replace(p,"")	


		# ajusta o número para que a publis unificada (quando exceder mais uma página) receba sempre o número da página onde começou		
		if num_pag == 1:
			del publis[0]
			data = "nada"
		elif num_pag == 2:
			for w in range(len(datas)):
				item = datas[w]
				if item == "nada":
					datas[w] = data
			
		
		# unifica o pedaço anterior com o atual	nas publicações que excedem mais de uma página
		if len(continuacao) > 2:
			publis[0] = continuacao + publis[0]
			# print("juntou o pedaço anterior")


		### separa os dados das publis cortadas
		for o in range(len(publis)):

	

			## regra da pesquisa do número CNJ dentro do texto da publicação

			if len(publis[o]) <= 1000: # se a publicação tiver até 1000 caracteres, procura no texto todo
				trecho_publis = publis [o]
			else:	
				vlr = int(len(publis[o])*0.10)
				if vlr < 400: # se tiver mais de mil até 4000, procura nos 4000 primeiro caracteres
					vlr = 400
				trecho_publis = publis[o][0:vlr] # fora isso, pesquisar nos 10% primeiros caracteres da publicação
			trecho_publis = trecho_publis.replace("\n"," ").lower()	


			# se não for a última página
			if num_pag != len(qtdade_paginas):

				# se não for a última publicação da página
				if o != len(publis)-1:

					try:
						# separa o padrão CNJ
						numer = re.search('\d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{3}\.\d{2}\.\d{4}\.\d{5,8}.\d{1,2}|\d{3}\.\d{2}\.\d{4}\.\d{5,8}',trecho_publis).group()

						# print(numer)
		

						# se for a primeira publicação da página e não for a primeira página
						if o == 0 and num_pag != 1:
							numeros_paginas.append(num_pag_ant) # insere o numero da pagina publicação anterior

						# caso contrário insere o número da própria página	
						else:
							numeros_paginas.append(num_pag)

						# insere os demais dados dessa publicação
						numeros_certos.append(numer) # insere o número
						trechos_certos.append(publis[o])
						docs_certos.append(doc)
						pastas.append(pasta)
						

					## havendo algum erro acrescenta na planilha de publicações erradas para conferência posterior	
					except:
						# print(publis[o])
						publis_erros.append(publis[o])
						print("publicação", o)
						print("da página", num_pag)

						paginas_erros.append(num_pag)
						docs_errados.append(doc)
						# z = input("verificar")

				
				# se for a última publicação da página, junta na variável continuação para depois ser ajustada no recorte
				# caso ela exceda mais de uma página		
				else:
					if num_pag == len(qtdade_paginas) and o == len(publis)-1:
						numer = re.search('\d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}',trecho_publis).group()
						numeros_certos.append(numer)	
						numeros_paginas.append(num_pag_ant)
						trechos_certos.append(publis[o])
						docs_certos.append(doc)
						pastas.append(pasta)

					else:
						continuacao = publis[o]
						if len(publis) > 1:
							num_pag_ant = num_pag
						elif len(publis) == 1:
							pass

			# se for a última página já unifica diretamente, porque não terá a variável "continuação" nem publis cortadas
			else:
				numer = re.search('\d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{3}\.\d{2}\.\d{4}\.\d{5,8}.\d{1,2}|\d{3}\.\d{2}\.\d{4}\.\d{5,8}',trecho_publis).group()
				numeros_certos.append(numer)	
				numeros_paginas.append(num_pag_ant)
				trechos_certos.append(publis[o])
				docs_certos.append(doc)
				pastas.append(pasta)

	# retorna a lista com os dados separados			
	return trechos_certos, numeros_certos, datas, numeros_paginas, docs_certos, paginas_erros, publis_erros, datas_erros, docs_errados, pastas, comarcas, tipos_proces, assuntos, oabs



# ################################################### Função que inicia o processo  ###########################################

def Main_Separacao(ano):

	# diretório
	diret = r'./Diarios_SP_'+ano


	# iteração sobre as páginas
	pastas = os.listdir(diret)



	# iteração sobre as patas e os arquivos
	for b in tqdm(range(len(pastas))):
		
		nome_pasta = os.path.join(diret, pastas[b])
		arquivos = os.listdir(nome_pasta)

		# Separar_textos_paginas()
		data_frames = Separar_textos_paginas(nome_pasta,arquivos,pastas[b])
	

		# itera sobre os DF
		for m in tqdm(range(len(data_frames))):
			trechos_certos, numeros_certos, datas, numeros_paginas, docs_certos, paginas_erros, publis_erros, datas_erros, docs_errados, pasta_atual,comarcas, tipos_proces, assuntos, oabs = Cortar_publicacoes(data_frames[m])


			#criando o objeto dataframe
			df_certos = pd.DataFrame()
			r = pd.Series(numeros_certos)
			y = pd.Series(trechos_certos)
			x = pd.Series(numeros_paginas)
			h = pd.Series(docs_certos)
			i = pd.Series(pasta_atual)
			d = pd.Series(comarcas)
			e = pd.Series(tipos_proces)
			f = pd.Series(assuntos)
			g = pd.Series(oabs)
			
			df_certos = pd.concat([r,y,x,h,i,d,e,f,g], axis=1,keys=["numero_processo","publicacao","numeros_paginas","nome_documento", "nomes_pastas",
				"comarcas","tipos_processuais","assuntos","representantes"])

			# ajuste da data

			frag = df_certos["nomes_pastas"].str.split("-", expand = True)

			df_certos ["dia"] = frag[0]
			df_certos ["mes"] = frag[1]
			df_certos ["ano"] = frag[2]
			df_certos ["estado"] = "SP"
			# df_certos["instancia"] = np.where(df_certos["nome_documento"].str.contains("2ªInstancia"), "2ª Instancia", "1ª Instancia")

			# ajusta a última publicação que vem com o sumário

			corte = re.split(r"(?i)SUM(A|Á)RIO", df_certos["publicacao"].iloc[-1])

			df_certos["publicacao"].iloc[-1] = corte[0]

			######################
			

			df_certos["data_decisao"] = None
			df_certos["orgao_julgador"] = None
			df_certos["tipo_publicacao"] = None

			df_certos = df_certos[["numero_processo", "estado","publicacao","numeros_paginas","tipos_processuais","assuntos","comarcas",
			"representantes","dia", "mes","ano","nome_documento","nomes_pastas","data_decisao","orgao_julgador", 'tipo_publicacao']]



			# cria o diretório

			dir_path = str(os.path.dirname(os.path.realpath(__file__)))
			path = dir_path + f'\Diarios_processados_csv_'+str(ano)
			Path(path).mkdir(parents=True, exist_ok=True)


			# transforma num csv
			df_certos.to_csv(path+"\Diarios_publicacoes_SP_"+str(df_certos["nomes_pastas"][0])+"_"+str(m)+".csv", index = False)
			# anterior_errados.to_excel("Erros_publicacoes.xlsx", index = False)		

################################################################

#chama a função


def main():
	
	ini = time.time()
	ano = input("Digite o ano com 4 dígitos (Ex:2012):")
	data_frames = Main_Separacao(ano)
	fim = time.time()
	tempo_total = (fim-ini)//60 #calcula o tempo decorrido
	print("O tempo de execução foi aproximadamente =", tempo_total,"minutos")

	

################################################################################################################


if __name__ == "__main__":
	main()