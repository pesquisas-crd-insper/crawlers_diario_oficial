# Imports de bibliotecas
import pandas as pd
from tqdm import tqdm
from PyPDF2 import PdfFileReader, PdfFileMerger
import os, re
import fitz
import random
import json
import time
from pathlib import Path




##################################################################################################

									# Função para separar os textos das publicações

def Separar_textos_paginas(ano):


	diret = r'./Diarios_MS_'+ano

	pastas = os.listdir(diret)


	# iteração das pastas para acessar os arquivos de PDF individualmente

	for b in tqdm(range(2)):#len(pastas))):
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
			print(arquivos[a], nome_pasta)
			nome = os.path.join(nome_pasta, arquivos[a])


			# contagem dos números das páginas
			num_pag = 0


			with fitz.open(nome) as pdf:
				for pagina in pdf:
					num_pag = num_pag + 1
					blocks = pagina.get_text("dict")['blocks'] # método que divide o texto em blocos no formato dict
				

					for o in range(len(blocks)):
				
						try: # elimina os blocos que não contém "lines" e consequentemente não tem textos

							lines = blocks[o]["lines"] # separa as linhas
							txt_block = []
							cabec =[]	
					
							for x in range(len(lines)):
								spans = lines[x]["spans"] # separa os spans
								for u in spans:
									tam = str(u['size']).split(".")[0]
									flag =str(u['flags'])


									## para o teste previo de verificar as flags
									caracteristicas.append((tam,flag))

									if tam == "8" and flag == "0" or tam == "8" and flag =="16": 
										txt_block.append(u['text'].strip()) # separa todos os textos de cada bloco e salva na lista para unificação
										
								
									## para verificar o que aparece nos padrões das flags
							
									# if tam == "8" and flag == "16":
									# 	print("\n\n PADRÃO 2\n\n",u['text'])
									# 	z = input("")
									# elif tam == "8" and flag == "0":
									# 	print("\n\n PADRÃO 3\n\n",u['text'])	
									# 	z = input("")
									# elif tam == "5" and flag == "0":
									# 	print("\n\n PADRÃO 4\n\n",u['text'])	
									# 	z = input("")
							

							# unifica os textos de cada bloco e salva o número da página, nome do arquivo, a data e o cabeçalho separado

							if len(txt_block) > 0:
								txt_fim = " ".join(txt_block)
								txt_unific.append(txt_fim)
								numeros_paginas.append(num_pag)
								nomes_pastas.append(nome_pasta[-10:])
								nome_doc.append(arquivos[a])

							# caso o texto do bloco seja vazio, unifica um texto vazio para manter a mesma quantidade d eitens da lista
							else:
								txt_fim = " "
								txt_unific.append(txt_fim)
								numeros_paginas.append(num_pag)
								nomes_pastas.append(nome_pasta[-10:])
								nome_doc.append(arquivos[a])
								
							if len(cabec) > 0:	
								cabecalhos.append(cabec[0])
							else:
								cabec =[" "]
								cabecalhos.append(cabec[0])
										
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


			Juntar_blocks(numeros_paginas,nome_doc, nomes_pastas, txt_unific,ano,a)								
			# return numeros_paginas,	nome_doc, nomes_pastas, txt_unific
	

###############################################################################

###### Função para separar, unificar e selecionar as publicações de interesse e Gerar um Banco de dados em excel #########

def Juntar_blocks(numeros_paginas,nome_doc, nomes_pastas, txt_unific,ano,num_arq):


	publicacoes = []
	num_pags = []
	nome_docs = []
	nome_pst = []
	num_process =[]
	

	# print("a página maior é",max(numeros_paginas))
	# print('qtdade textos',len(txt_unific))
	# print('qtdade num_pag',len(numeros_paginas))
	# print('qtdade nomes_docs',len(nome_doc))
	# print('qtadade nomes_pastas',len(nomes_pastas))

	# z= input("")


	for txt,num,doc,pst in zip(txt_unific,numeros_paginas,nome_doc,nomes_pastas):

		## regra da pesquisa do número CNJ dentro do texto da publicação

		# if len(txt) <= 1000: # se a publicação tiver até 1000 caracteres, procura no texto todo
		# 	text = txt
		# else:	
		# 	vlr = int(len(txt)*0.10)
		# 	if vlr < 400: # se tiver mais de mil até 4000, procura nos 4000 primeiro caracteres
		# 		vlr = 400
		# 	text = txt[0:vlr] # fora isso, pesquisar nos 10% primeiros caracteres da publicação
		text = txt[:90]

		## incício da busca

		
		if re.search('\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}',text, re.IGNORECASE.MULTILINE): # pesquisa o padrão em todas as linhas da publicação (dentro do limite de caracteres)
			nm_proc = re.search('\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}',text, re.IGNORECASE.MULTILINE).group().replace(" ","") # se encontrar o padrão completo, separa o número
			num_process.append(nm_proc) # salva na lista
			

			# salva nas listas a publicação e as demais informações dela (página, documento, pasta)	
			publicacoes.append(txt) 
			num_pags.append(num)
			nome_docs.append(doc)
			nome_pst.append(pst)
			
	
		# caso ele não encontre o padrão CNJ e essa publicação não seja a primeira da lista 
		else:
		
			if len(publicacoes)>=1 and re.search("Disponibilização:",txt,re.IGNORECASE) == None: #verifica se atingiu a quantidade máxima de unificações (4) sem encontrar um padrão CNJ ou se é a primeira da lista
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
			
		# print(publicacoes[-1])
		# z=input('')

		# gera o DF com as publicações e as demais informações

		df_textos_paginas = pd.DataFrame()
		df_textos_paginas["numero_processo"] = num_process
		df_textos_paginas["publicacao"] = publicacoes
		df_textos_paginas["numeros_paginas"] = num_pags
		df_textos_paginas["nome_documento"] = nome_docs
		df_textos_paginas["nomes_pastas"] = nome_pst
		df_textos_paginas["estado"] = "MS"
		df_textos_paginas["tipos_processuais"] = None
		df_textos_paginas["comarcas"] = None
		df_textos_paginas["representantes"] = None
		df_textos_paginas["assuntos"] = None

		


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

		# gera o excel com o DF final

		print(df_textos_paginas[["numero_processo", "publicacao","numeros_paginas","nome_documento"]])
		

		dir_path = str(os.path.dirname(os.path.realpath(__file__)))
		path = dir_path + f'\Diarios_processados_MS_csv_'+str(ano)
		Path(path).mkdir(parents=True, exist_ok=True)

		df_textos_paginas.to_csv(path+"\Diarios_publicacoes_MS_"+str(df_textos_paginas["nomes_pastas"][0])+"_"+str(num_arq)+".csv", index = False)
		# df_textos_paginas.to_excel(path+"\Diarios_publicacoes_MS_"+str(df_textos_paginas["nomes_pastas"][0])+"_"+str(num_arq)+".xlsx", index = False)

		# converte para JSON

		# result = df_textos_paginas.to_json(orient="records", force_ascii = False)
		# parsed = json.loads(result)
		# with open('data_MS_'+str(nome_pst[0])+'_'+str(num_arq)+'.json', 'w', encoding ='utf-8') as fp:
		# 	json.dump(parsed, fp)

		# time.sleep(5)	

		# with open('data_AM.json', 'r', encoding ='utf-8') as fp:
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