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

def Separar_textos_paginas(ano):
	
	diret = r'./Diarios_CE_'+ano

	pastas = os.listdir(diret)


	# itera sobre as pastas e os arquivos

	for b in tqdm(range(len(pastas))):
		nome_pasta = os.path.join(diret, pastas[b])
		arquivos = os.listdir(nome_pasta)
		

		numeros_paginas =[]
		nome_doc = []
		nomes_pastas =[]
		txt_unific = []
		sem_lines = []

		## lista para verificar as flags escolhidas
		caracteristicas =[]
		

		for a in range(len(arquivos)):
			print(arquivos[a])
			nome = os.path.join(nome_pasta, arquivos[a])


			# controla o número das páginas
			num_pag = 0

			# itera sobre os Pdfs
			with fitz.open(nome) as pdf:
				for pagina in pdf:
					num_pag = num_pag + 1

					# separa o texto em blocos
					blocks = pagina.get_text("dict")['blocks']					
					for o in range(len(blocks)):

					# separa os blocos em linhas				
						try:
							lines = blocks[o]["lines"]
							txt_block = []

							# separa as linhas em spans	
							for x in range(len(lines)):
								spans = lines[x]["spans"]

								# separa os spans em textos 
								for u in spans:
									tam = str(u['size']).split(".")[0]
									flag =str(u['flags'])

									## para o teste previo de verificar as flags	
									caracteristicas.append((tam,flag))


									txt_block.append(u['text'])

									## para verificar o que aparece nos padrões das flags
							
									# if tam == "8" and flag == "4":
									# 	print("\n\n PADRÃO 2\n\n",u['text'])
									# 	z = input("")
									# if tam == "8" and flag == "20":
									# 	print("\n\n PADRÃO 3\n\n",u['text'])	
									# 	z = input("")
							
							# unifica os textos dos blocos, inserindo também os números de páginas, pastas, arquivos	
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
								
						# função apenas de conferência, sem utilidade				
						except:
							sem_lines.append(blocks[o]["number"])	



			# contabilização da quantidade de flags mais frequentes
									
			# nome_acao = pd.DataFrame()
			# nome_acao["Ação"] = caracteristicas							
			# nome_acao = pd.DataFrame(nome_acao.groupby(["Ação"])["Ação"].count())
			# nome_acao.columns = ["quantidade"]
			# nome_acao = nome_acao.reset_index()						

			# print(nome_acao.sort_values(by=['quantidade'],ascending=False))
			# z = input("")
			

			# função para organizar os blocos							
			Juntar_blocks(numeros_paginas,nome_doc, nomes_pastas, txt_unific, ano,a)								
			
			# return numeros_paginas,	nome_doc, nomes_pastas, txt_unific




########################  Função que organiza o texto em blocos ################################
	
def Juntar_blocks(numeros_paginas,nome_doc, nomes_pastas, txt_unific,ano, num_arq):


	publicacoes = []
	num_pags = []
	nome_docs = []
	nome_pst = []
	num_process=[]



	for txt,num,doc,pst in zip(txt_unific,numeros_paginas,nome_doc,nomes_pastas):
		
		## regra da pesquisa do número CNJ dentro do texto da publicação

		txt_inic = txt[:90]



		## incício da busca

		
		if re.search('\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{2,3}-\d{2}.\d{4}\.\d\.\d{2}\.\d{4}',txt_inic, re.IGNORECASE.MULTILINE): # pesquisa o padrão em todas as linhas da publicação (dentro do limite de caracteres)
			nm_proc = re.search('\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{2,3}-\d{2}.\d{4}\.\d\.\d{2}\.\d{4}',txt_inic, re.IGNORECASE.MULTILINE).group().replace(" ","") # se encontrar o padrão completo, separa o número
			
			if len(num_process) > 1:
				proces_ant = num_process[-1]
				if proces_ant == nm_proc:
					txt = publicacoes[-1]+" "+txt  # unifica o texto atual com a publicação anterior
					del publicacoes[-1] # deleta da lista a publicação anterior
					publicacoes.append(txt) # junta a nova publicação unificada na lista (o número da página e o nome do doc se mantém onde a publicação começa)
					pula = False

				else:	
					num_process.append(nm_proc) # salva na lista
					# salva nas listas a publicação e as demais informações dela (página, documento, pasta)	
					publicacoes.append(txt) 
					num_pags.append(num)
					nome_docs.append(doc)
					nome_pst.append(pst)
					pula = False
					
			else:
				num_process.append(nm_proc) # salva na lista
				# salva nas listas a publicação e as demais informações dela (página, documento, pasta)	
				publicacoes.append(txt) 
				num_pags.append(num)
				nome_docs.append(doc)
				nome_pst.append(pst)
				pula = False
				
				
	
		# caso ele não encontre o padrão CNJ e essa publicação não seja a primeira da lista 
		else:
			if re.search("Atas das sessões",txt_inic, re.IGNORECASE):
				pula = True

			else:
				try:
					pag_anter = num_pags[-1]
					if num == pag_anter and re.search(r"Ementa:|\d{1,2}(\s\W|\.|-)",txt_inic[:10],re.IGNORECASE) == None:
						num_juntado = ""

					else:
						# if num == 12:
						# 	print(txt_inic)
						# 	z= input("")
						if re.search(r"Ementa:|\d{1,2}(\s\W|\.|-)",txt_inic[:10],re.IGNORECASE) or len(publicacoes)>=1 and re.search("Disponibilização:|Publicação Oficial do Tribunal",txt,re.IGNORECASE) == None and num_juntado != num and pula != True:
							txt = publicacoes[-1]+" "+txt  # unifica o texto atual com a publicação anterior
							del publicacoes[-1] # deleta da lista a publicação anterior
							publicacoes.append(txt) # junta a nova publicação unificada na lista (o número da página e o nome do doc se mantém onde a publicação começa)
							num_juntado = num
				except:
					pass

		
		


	###### PARA CONFERÊNCIA - DESCOMENTAR CASO QUEIRA VERIFICAR O CORTE FINAL DAS PUBLICAÇÕES NA ORDEM - APERTAR ENTER A CADA PUBLICAÇÃO
	qtdade = 0
	for item,num in zip(publicacoes,num_pags):
		qtdade = qtdade+1
		print("Quantidade avaliada:",qtdade)
		print("página", num)
		print(item)
		print("-----------------")
		z = input('')
	##################   FIM DO TRECHO PARA CONFERÊNCIA ##############################


	# gera o DF com as publicações e as demais informações

	df_textos_paginas = pd.DataFrame()
	df_textos_paginas["numero_processo"] = num_process
	df_textos_paginas["publicacao"] = publicacoes
	df_textos_paginas["numeros_paginas"] = num_pags
	df_textos_paginas["nome_documento"] = nome_docs
	df_textos_paginas["nomes_pastas"] = nome_pst
	df_textos_paginas["estado"] = "CE"	

	


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

	df_textos_paginas = df_textos_paginas[["numero_processo", "estado","publicacao","numeros_paginas","tipos_processuais", "assuntos","comarcas",
	"representantes","dia", "mes","ano","nome_documento","nomes_pastas","data_decisao","orgao_julgador", "tipo_publicacao"]]

	# gera o excel com o DF final


	# cria o diretório

	dir_path = str(os.path.dirname(os.path.realpath(__file__)))
	path = dir_path + f'\Diarios_processados_CE_csv_'+str(ano)
	Path(path).mkdir(parents=True, exist_ok=True)



	# gera o excel com o DF final




	df_textos_paginas.to_csv(path+"\Diarios_publicacoes_CE_"+str(df_textos_paginas["nomes_pastas"][0])+"_"+str(num_arq)+".csv", index = False)
	df_textos_paginas.to_excel(path+"\Diarios_publicacoes_CE_"+str(df_textos_paginas["nomes_pastas"][0])+"_"+str(num_arq)+".xlsx", index = False)


	# converte para JSON

	# result = df_textos_paginas.to_json(orient="records", force_ascii = False)
	# parsed = json.loads(result)
	# with open('data_CE_'+str(nome_pst[0])+'_'+str(num_arq)+'.json', 'w', encoding ='utf-8') as fp:
	# 	json.dump(parsed, fp)
	# # df_textos_paginas.to_excel("Diarios_publicacoes_AM_"+ano+".xlsx", index = False)

	# # converte para JSON

	# result = df_textos_paginas.to_json(orient="records", force_ascii = False)
	# parsed = json.loads(result)
	# with open('data_CE.json', 'w', encoding ='utf-8') as fp:
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