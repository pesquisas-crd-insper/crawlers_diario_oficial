# Imports de bibliotecas
import pandas as pd
from tqdm import tqdm
from PyPDF2 import PdfFileReader, PdfFileMerger
import os, re
import fitz
import random
from datetime import datetime
import json
import time
from pathlib import Path


def Coleta_data(tam,flag,text_dt):
	

	if tam == "8" and flag == "0" or tam == "9" and flag == "4":
		dt_diario = re.search('Disponibilização:(\s*.*\d)|disponibilização:(\s.*\.\s)\.*',text_dt).group()
		# print("está é a string:",dt_diario)
		pattern_dt = re.compile("(D|d)isponibilização:")
		dt_diario = pattern_dt.sub("",dt_diario).strip()
		data_ajust = Convert_data(dt_diario)

	# print(data_ajust)
	return data_ajust		

####################### função para converter a data ####################

def Convert_data(dt_ext):
	
	meses = {
        '1': 'janeiro',
        '2': 'fevereiro',
        '3': 'março',
        '4': 'abril',
        '5': 'maio',
        '6': 'junho',
        '7': 'julho',
        '8': 'agosto',
        '9': 'setembro',
        '10': 'outubro',
        '11': 'novembro',
        '12': 'dezembro'        
    }

	
    #separa o nome do mês e verifica a numeração dele no dict

	nome_mes = re.findall('\sde\s(.*)\sde',dt_ext)[0].strip()
	for key in meses:
		if meses[key] == nome_mes:
			mes = key

	# print(mes)

	#separa o dia		
	dia = re.findall(',\s*(.\d{1,2}\s)',dt_ext)[0].strip()
	# print(dia)

	#separa o trecho do ano e depois o ano		
	trch = dt_ext[-6:]
	ano_ajus = re.findall('(\d{4})',trch)[0]
	
	# print(ano_ajus)
	### ajustar pra virar um DTtime
	
	# junta a string
	data_ajus = dia+"-"+mes+"-"+ano_ajus
	# print(data_ajus)

	#converte a string em data
	date = datetime.strptime(data_ajus, '%d-%m-%Y').date()

	#formata a data	
	dataFormatada = date.strftime('%d-%m-%Y')

	# print(dataFormatada)
	# z= input("")
	
	return dataFormatada


##################################################################################################

							# Função para separar os textos das publicações

def Separar_textos_paginas(ano):

	# diretório com as pastas e os dados

	diret = r'./Diarios_BA_'+ano

	pastas = os.listdir(diret)
	# print(pastas)


	# listas que receberão os dados

	# iteração das pastas para acessar os arquivos de PDF individualmente

	for b in tqdm(range(len(pastas))):
		nome_pasta = os.path.join(diret, pastas[b])
		arquivos = os.listdir(nome_pasta)


		## lista para verificar as flags escolhidas
		caracteristicas =[]

		for a in range(len(arquivos)):
			
			numeros_paginas =[]
			nome_doc = []
			nomes_pastas =[]
			txt_unific = []
			sem_lines = []
			
			print(arquivos[a])
			nome = os.path.join(nome_pasta, arquivos[a])


			# contagem dos números das páginas
			num_pag = 0
			data_ajust = 'NADA'

			with fitz.open(nome) as pdf:
				for pagina in pdf:
					num_pag = num_pag + 1
					# print("\n\n\n Estamos na página",num_pag,"\n\n\n\n documento:",arquivos[a],"\n\n\n Na pasta:",nome_pasta,"\n\n\n")
					
					blocks = pagina.get_text("dict")['blocks'] # método que divide o texto em blocos no formato dict
	
				
					for o in range(len(blocks)):
						
											
						# print(blocks[o])
						# z= input("")
						try: # elimina os blocos que não contém "lines" e consequentemente não tem textos
							
							lines = blocks[o]["lines"] # separa as linhas
							
							txt_block = []	
							
							for x in range(len(lines)):
								spans = lines[x]["spans"] # separa os spans
								
								for u in spans:
									tam = str(u['size']).split(".")[0]
									flag =str(u['flags'])

									if num_pag == 1:
										if re.search('Disponibilização:(\s*.*\d)|disponibilização:(\s.*\.\s)\.*',u['text']):
											data_ajust = Coleta_data(tam,flag,str(u['text']))
										
									## para o teste previo de verificar as flags	
									caracteristicas.append((tam,flag)) 

									if tam == "8" and flag == "0" or tam == "9" and flag == "0" or tam == "9" and flag == "4":
										# if num_pag == 1:
										# print(u['text']) 
										txt_block.append(u['text'].strip()) # separa todos os textos de cada bloco e salva na lista para unificação
										# print(txt_block)
										# z = input('')
								

									## para verificar o que aparece nos padrões das flags
							
									# if num_pag == 1 and tam == "8" and flag == "4":
									# 	print("\n\n PADRÃO 2\n\n",num_pag,"\n\n",u['text'])
									# 	z = input("")
									# # if tam == "9" and flag == "4":
									# 	print("\n\n PADRÃO 3\n\n",u['text'])	
									# 	z = input("")

						
							if len(txt_block) > 0:
								txt_fim = " ".join(txt_block)
								# if num_pag == 1:
								# 	# print(tam, flag)
								# 	print(txt_fim)
								# 	z= input("")
								txt_unific.append(txt_fim)
								numeros_paginas.append(num_pag)
								nome_doc.append(str(arquivos[a]))
								nomes_pastas.append(data_ajust)

								# if len(txt_unific) != len(nomes_pastas):
								# 	print("parou!")
								# 	print(len(txt_unific))
								# 	print(len(nomes_pastas))
								# 	print("------------")
								# 	z= input("")

							# caso o texto do bloco seja vazio, unifica um texto vazio para manter a mesma quantidade d eitens da lista
							else:
								# print("entrou no vazio!")
								txt_fim = "NADATEM"
								txt_unific.append(txt_fim)
								numeros_paginas.append(num_pag)
								nome_doc.append(str(arquivos[a]))
								nomes_pastas.append(data_ajust)

								# if len(txt_unific) != len(nomes_pastas):
								# 	print(len(txt_unific))
								# 	print(len(nomes_pastas))
								# 	print("------------")
								# 	print("parou aqui!")
								# 	z= input("")
					
							

						# se não tiver as linhas, salva em outra lista - somente para conferência, não tem utilidade.					
						
						except:
							sem_lines.append(blocks[o]["number"])



			## contabilização da quantidade de flags mais frequentes
									
			# nome_acao = pd.DataFrame()
			# nome_acao["Ação"] = caracteristicas							
			# nome_acao = pd.DataFrame(nome_acao.groupby(["Ação"])["Ação"].count())
			# nome_acao.columns = ["quantidade"]
			# nome_acao = nome_acao.reset_index()						

			# print(nome_acao.sort_values(by=['quantidade'],ascending=False))
			# z = input("")

			# print(len(txt_unific))
			# print(len(nome_doc))
			# # z= input("")
			# for item in txt_unific:
			# 	print(item)
			# 	z= input("")
			
			nomes_pastas = [data_ajust if value=="NADA" else value for value in nomes_pastas]
			# print(nomes_pastas[:10])
			# z = input("")
			Juntar_blocks(numeros_paginas,nome_doc,nomes_pastas,txt_unific,ano,a)								
			# return numeros_paginas,	nome_doc, nomes_pastas, txt_unific
	

###############################################################################

 			###### Função para separar, unificar e selecionar as publicações de interesse e Gerar um Banco de dados em JSON #########


def Juntar_blocks(numeros_paginas,nome_doc,nomes_pastas,txt_unific,ano,num_arq):

	num_process =[]
	publicacoes = []
	num_pags = []
	nome_docs = []
	nome_pst = []

	
	# print("a página maior é",max(numeros_paginas))
	# print('qtdade textos',len(txt_unific))
	# print('qtdade num_pag',len(numeros_paginas))
	# print('qtdade nomes_docs',len(nome_doc))
	# print('qtadade nomes_pastas',len(nomes_pastas))

	# # print(numeros_paginas[-1])
	# print(txt_unific[0])
	# z= input("")
	
	pattern_init = re.compile('ADV:|\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d{3}\.\d{4}')
	pattern_num = re.compile('\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d{3}\.\d{4}')


	for txt,num,doc,pst in zip(txt_unific,numeros_paginas,nome_doc,nomes_pastas):
	
		## regra da pesquisa do número CNJ dentro do texto da publicação

		if len(txt) <= 1000: # se a publicação tiver até 1000 caracteres, procura no texto todo
			text = txt
		else:	
			vlr = int(len(txt)*0.10)
			if vlr < 400: # se tiver mais de mil até 4000, procura nos 4000 primeiro caracteres
				vlr = 400
			text = txt[0:vlr] # fora isso, pesquisar nos 10% primeiros caracteres da publicação


		# if num == 1:
		# 	print(txt)
		# 	z= input("")
		# 	if re.search('d{2,7}', txt):
		# 		print(txt)
		##início da busca

		
		if re.search(pattern_init, text): # pesquisa o padrão em todas as linhas da publicação (dentro do limite de caracteres)

			# if num == 1:
			# 	print(txt)
			# 	z= input("")
			# # salva nas listas a publicação e as demais informações dela (página, documento, pasta)


			publicacoes.append(txt) 
			num_pags.append(num)
			nome_docs.append(doc)
			nome_pst.append(pst)
			pular = False

			
	
		# caso ele não encontre o padrão CNJ e essa publicação não seja a primeira da lista 
		else:
			if re.search("NUBENTE:|CONVIVENTE:",txt,re.IGNORECASE):
				pular = True
			else:
				if len(publicacoes)>=1 and re.search("^Disponibilização|NADATEM",txt,re.IGNORECASE) == None and pular == False: #verifica se atingiu a quantidade máxima de unificações (4) sem encontrar um padrão CNJ ou se é a primeira da lista
					txt = publicacoes[-1]+" "+txt  # unifica o texto atual com a publicação anterior
					del publicacoes[-1] # deleta da lista a publicação anterior
					publicacoes.append(txt) # junta a nova publicação unificada na lista (o número da página e o nome do doc se mantém onde a publicação começa)
						
				else:
					pass
		
		


	###### PARA CONFERÊNCIA - DESCOMENTAR CASO QUEIRA VERIFICAR O CORTE FINAL DAS PUBLICAÇÕES NA ORDEM - APERTAR ENTER A CADA PUBLICAÇÃO
	# qtdade = 0
	# for item,num in zip(publicacoes,num_pags):
	# 	qtdade = qtdade+1
	# 	print("Quantidade avaliada:",qtdade)
	# 	print("página", num)
	# 	print(item)
	# 	print("-----------------")
	# 	z = input('')


	##################   FIM DO TRECHO PARA CONFERÊNCIA ##############################
	if len(publicacoes) == 0:
		print("arquivo", num_arq,"vazio")
	else:
		print("tinhamos", len(publicacoes))
		publicacoes_l = []
		num_pags_l = []
		nome_docs_l = []
		nome_pst_l = []
		num_process_l =[]			
		for n in range(len(publicacoes)):
			try:
				nm_proc = re.search(pattern_num,publicacoes[n]).group().replace(" ","") # se encontrar o padrão completo, separa o número
				# print(nm_proc)
				if len(num_process_l) > 0:
					proces_ant = num_process_l[-1]
					if proces_ant == nm_proc:
						publicacoes[n] = publicacoes_l[-1]+" "+publicacoes[n]  # unifica o texto atual com a publicação anterior
						del publicacoes_l[-1] # deleta da lista a publicação anterior
						publicacoes_l.append(publicacoes[n]) # junta a nova publicação unificada na lista (o número da página e o nome do doc se mantém onde a publicação começa)
					else:	
						num_process_l.append(nm_proc) # salva na lista
						publicacoes_l.append(publicacoes[n])
						num_pags_l.append(num_pags[n])
						nome_docs_l.append(nome_docs[n])
						nome_pst_l.append(nome_pst[n])	
				else:
					num_process_l.append(nm_proc) # salva na lista
					publicacoes_l.append(publicacoes[n])
					num_pags_l.append(num_pags[n])
					nome_docs_l.append(nome_docs[n])
					nome_pst_l.append(nome_pst[n])
			except:
				pass
		print("agora temos",len(publicacoes_l))
		
		# print(num_pags_l[-1])
		# print(publicacoes_l[-1])
		# z= input("")
		# gera o DF com as publicações e as demais informações

		df_textos_paginas = pd.DataFrame()
		df_textos_paginas["numero_processo"] = num_process_l
		df_textos_paginas["publicacao"] = publicacoes_l
		df_textos_paginas["numeros_paginas"] = num_pags_l
		df_textos_paginas["nome_documento"] = nome_docs_l
		df_textos_paginas["nomes_pastas"] = nome_pst_l
		df_textos_paginas["estado"] = "BA"
		df_textos_paginas["tipos_processuais"] = None
		df_textos_paginas["comarcas"] = None
		df_textos_paginas["representantes"] = None
		df_textos_paginas["assuntos"] = None

		print(df_textos_paginas[["numero_processo", "publicacao","numeros_paginas","nome_documento"]])
		print("Temos",len(df_textos_paginas),"nesse data frame")


		############ CONFERÊNCIA AMOSTRAL ALEATÓRIA - DESCOMENTAR CASO QUEIRA UMA AMOSTRA ALEATÓRIA DOS RECORTES  - APERTAR ENTER A CADA PUBLICAÇÃO


		# # # agrupa por nome do documento
		# doc_agrup = pd.DataFrame(df_textos_paginas.groupby(["nome_documento"])["nome_documento"].count())
		# doc_agrup.columns = ["quantidade"]
		# doc_agrup = doc_agrup.reset_index()

		# # converte os nomes em uma lista e depois embaralha os nomes em uma ordem indeterminada
		# lista_nomes_docs = doc_agrup["nome_documento"].tolist()
		# random.shuffle(lista_nomes_docs)


		# # Gera uma amostra aleatória de X publicações por documento para facilitar a conferência
		# for docu in lista_nomes_docs :
		# 	df_filter = df_textos_paginas["nome_documento"] == docu
		# 	amostra_trib = df_textos_paginas[df_filter]

		# 	amostra_trib = amostra_trib.sample(10)  # escolher a quantidade da amostra
		# 	for pub,doc,pag in zip(amostra_trib["publicacoes"],amostra_trib["nome_documento"],amostra_trib["numeros_paginas"]):
		# 		print("documento:\t",doc,"\nPágina:\t",pag,"\nTexto publicação:\n",pub,"\n--------------")
		# 		z= input("")

		##################   FIM DO TRECHO PARA CONFERÊNCIA ##############################


		frag = df_textos_paginas["nomes_pastas"].str.split("-", n=2, expand = True)
		df_textos_paginas["dia"] = frag[0]
		df_textos_paginas["mes"] = frag[1]
		df_textos_paginas["ano"] = frag[2]

		df_textos_paginas["data_decisao"] = None
		df_textos_paginas["orgao_julgador"] = None
		df_textos_paginas["tipo_publicacao"] = None

		df_textos_paginas = df_textos_paginas[["numero_processo", "estado","publicacao","numeros_paginas","tipos_processuais","assuntos","comarcas",
		"representantes","dia", "mes","ano","nome_documento","nomes_pastas","data_decisao","orgao_julgador","tipo_publicacao"]]


		dir_path = str(os.path.dirname(os.path.realpath(__file__)))
		path = dir_path + f'\Diarios_processados_BA_csv_'+str(ano)
		Path(path).mkdir(parents=True, exist_ok=True)

		# gera o excel com o DF final

		df_textos_paginas.to_csv(path+"\Diarios_publicacoes_BA_"+str(df_textos_paginas["nomes_pastas"][0])+"_"+str(num_arq)+".csv", index = False)
		# df_textos_paginas.to_excel(path+"\Diarios_publicacoes_BA_"+str(df_textos_paginas["nomes_pastas"][0])+"_"+str(num_arq)+".xlsx", index = False)

		# converte para JSON

		# result = df_textos_paginas.to_json(orient="records", force_ascii = False)
		# parsed = json.loads(result)
		# with open('data_BA_'+str(nome_pst[0])+'_'+str(num_arq)+'.json', 'w', encoding ='utf-8') as fp:
		# 	json.dump(parsed, fp)

		# with open('data_BA.json', 'r', encoding ='utf-8') as fp:
		# 	data = json.loads(fp.read())
		# 	print(json.dumps(data, indent = 4, ensure_ascii=False))

		# print(json.dumps(parsed, ensure_ascii=False, indent=4)) 



################################################################################################################

def main():
	
	ini = time.time()
	ano = input("Digite o ano com 4 dígitos (Ex:2012):")
	data_frames = Separar_textos_paginas(ano)
	fim = time.time()
	tempo_total = (fim-ini)//60 #calcula o tempo decorrido
	print("O tempo de execução foi aproximadamente =", tempo_total,"minutos")

################################################################################################################


if __name__ == "__main__":
	main()