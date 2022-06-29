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
import jellyfish


##################################################################################################
def Caracteristicas(caracteristicas):

	caract = pd.DataFrame()
	caract["valores"] = caracteristicas							
	caract = pd.DataFrame(caract.groupby(["valores"])["valores"].count())
	caract.columns = ["quantidade"]
	caract = caract.sort_values(by=['quantidade'],ascending=False)						
	caract = caract.reset_index()

	print(caract)
	# print(caract.sort_values(by=['quantidade'],ascending=False))

	tam_1 = caract["valores"][0][0]
	# print(tam_1)
	# z= input("")
	flag_1 = caract["valores"][0][1]
	tam_2 = caract["valores"][1][0]
	flag_2 = caract["valores"][1][1]
	return 1, tam_1, flag_1, tam_2, flag_2



###################################################################################################

							# Função para separar os textos das publicações

def Separar_textos_paginas(ano):

	# diretório com as pastas e os dados

	diret = r'./Diarios_AM_'+ano

	pastas = os.listdir(diret)
	# print(pastas)


	# listas que receberão os dados

	# iteração das pastas para acessar os arquivos de PDF individualmente

	# falta de 0 a 10 em 2019

	for b in tqdm(range(len(pastas))):
		nome_pasta = os.path.join(diret, pastas[b])
		arquivos = os.listdir(nome_pasta)


		for a in range(len(arquivos)):
			
			print(nome_pasta,":",arquivos[a])
			nome = os.path.join(nome_pasta, arquivos[a])
			# print(nome)

			numeros_paginas, nome_doc, nomes_pastas, txt_unific, sem_lines, posicao = processa_texto(str(pastas[b]),ano,str(arquivos[a]),nome, 0)
			Juntar_blocks(numeros_paginas,nome_doc,nomes_pastas,txt_unific,ano,a, posicao)								
			# return numeros_paginas,	nome_doc, nomes_pastas, txt_unific



def processa_texto(pasta,ano,arquivo, nome, verif_caract, tam_1=0, flag_1=0,tam_2=0, flag_2=0):



	# print("os tamanhos são:",tam_1, flag_1,tam_2,flag_2)
	numeros_paginas =[]
	nome_doc = []
	nomes_pastas =[]
	txt_unific = []
	sem_lines = []
	posicao = []

	## lista para verificar as flags escolhidas
	caracteristicas =[]

	# contagem dos números das páginas
	num_pag = 0


	with fitz.open(nome) as pdf:
		for pagina in pdf:
			num_pag = num_pag + 1
			# print("\n\n\n Estamos na página",num_pag,"\n\n\n\n documento:",arquivos[a],"\n\n\n Na pasta:",nome_pasta,"\n\n\n")
			
			blocks = pagina.get_text("dict")['blocks'] # método que divide o texto em blocos no formato dict
			# print(blocks)
			# z= input("")

		
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
							posic = str(u['bbox'][0]).split(".")[0]
							posic = int(posic)
							caracteristicas.append((tam,flag))
							
							# if num_pag == 1:
							# 	print(u['text'])
							# 	z = input("")

									
							if verif_caract == 1:
								# print("***************")
								# print()
								# print("os tamanhos são:",tam_1, flag_1,tam_2,flag_2)
								# print()
								# print("***************")
								if tam == str(tam_1) and flag == str(flag_1) or tam == str(tam_2) and flag == str(flag_2):
									# print("Pegou!")
									txt_block.append(u['text'].strip())
							else:
								pass

						
								
	# 						
	# 						## para verificar o que aparece nos padrões das flags
					
	# 						# if tam == "7" and flag == "16":
	# 						# 	print("\n\n PADRÃO 2\n\n",num_pag,"\n\n",u['text'])
	# 						# 	z = input("")
	# 						# # if tam == "9" and flag == "4":
	# 						# 	print("\n\n PADRÃO 3\n\n",u['text'])	
	# 						# 	z = input("")

				
					if len(txt_block) > 0:
						txt_fim = " ".join(txt_block)
						txt_unific.append(str(txt_fim))
						numeros_paginas.append(num_pag)
						nome_doc.append(str(arquivo))
						nomes_pastas.append(pasta)
						if posic < 300:
							posicao.append("lado A")
						else:
							posicao.append("lado B")

				
					# caso o texto do bloco seja vazio, unifica um texto vazio para manter a mesma quantidade d eitens da lista
					else:	
						txt_fim = " "
						txt_unific.append(txt_fim)
						numeros_paginas.append(num_pag)
						nome_doc.append(str(arquivo))
						nomes_pastas.append(pasta)
						if posic < 300:
							posicao.append("lado A")
						else:
							posicao.append("lado B")

	# 			# se não tiver as linhas, salva em outra lista - somente para conferência, não tem utilidade.					
				
				except:
					sem_lines.append(blocks[o]["number"])

	if verif_caract == 0:				
		verif_caract, tam_1, flag_1,tam_2, flag_2 = Caracteristicas(caracteristicas)
		numeros_paginas, nome_doc, nomes_pastas, txt_unific, sem_lines, posicao = processa_texto(pasta,ano,arquivo, nome, verif_caract,tam_1, flag_1, tam_2, flag_2)
		# print(len(numeros_paginas))
		# print(len(nome_doc))
		# print(len(nomes_pastas))
		# print(len(txt_unific))
		# print(nomes_pastas)
		# z= input("")
		return numeros_paginas, nome_doc, nomes_pastas, txt_unific, sem_lines, posicao
	else:
		return numeros_paginas, nome_doc, nomes_pastas, txt_unific, sem_lines, posicao


###############################  Função para juntar os blocos dos textos ################################################

def Juntar_blocks(numeros_paginas,nome_doc, nomes_pastas, txt_unific,ano,num_arq, posicao_publis):


	publicacoes = []
	num_pags = []
	nome_docs = []
	nome_pst = []
	num_process =[]
	posicao_atual = []
	


	vlr_cort = 0
	for txt,num,doc,pst,pos in zip(txt_unific,numeros_paginas,nome_doc,nomes_pastas,posicao_publis):

		## regra da pesquisa do número CNJ dentro do texto da publicação

		text = txt[:260].replace("\n","")
		# print(text)
	

		## incício da busca

		
		if re.search('\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{4}\.\d{6}-\s*\d',text, re.IGNORECASE.MULTILINE): # pesquisa o padrão em todas as linhas da publicação (dentro do limite de caracteres)
			nm_proc = re.search('\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{4}\.\d{6}-\s*\d',text, re.IGNORECASE.MULTILINE).group().replace(" ","") # se encontrar o padrão completo, separa o número
			num_process.append(nm_proc) # salva na lista
			# print(nm_proc)
			# print("*"*8)
			# z = input("")

			# salva nas listas a publicação e as demais informações dela (página, documento, pasta)	
			publicacoes.append(txt) 
			num_pags.append(num)
			nome_docs.append(doc)
			nome_pst.append(pst)
			posicao_atual.append(pos)


		# caso ele não encontre o padrão CNJ e essa publicação não seja a primeira da lista 

		### se o bbox for do outro lado ele aceita uma...tenho que inserir esse atributo na característica
		else:
			try:
				pag_anter = num_pags[-1]
				pos_anter = posicao_atual[-1]
				if num == pag_anter and pos_anter == pos:
					pass
				else:
					if len(publicacoes)>=1 and re.search("^Disponibilizado -",txt,re.IGNORECASE) == None:
						txt = publicacoes[-1]+" "+txt  # unifica o texto atual com a publicação anterior
						del publicacoes[-1] # deleta da lista a publicação anterior
						publicacoes.append(txt) # junta a nova publicação unificada na lista (o número da página e o nome do doc se mantém onde a publicação começa)
			except:
				pass

		
		
		


	###### PARA CONFERÊNCIA - DESCOMENTAR CASO QUEIRA VERIFICAR O CORTE FINAL DAS PUBLICAÇÕES NA ORDEM - APERTAR ENTER A CADA PUBLICAÇÃO
	# qtdade = 0
	# for item,num,pos in zip(publicacoes,num_pags,posicao_atual):
	# 	qtdade = qtdade+1
	# 	print("Quantidade avaliada:",qtdade)
	# 	print("página", num,"posição",pos)
	# 	print(item)
	# 	print("-----------------")
	# 	z = input('')
	##################   FIM DO TRECHO PARA CONFERÊNCIA ##############################


	# gera o DF com as publicações e as demais informações

	df_textos_paginas = pd.DataFrame()
	df_textos_paginas["numero_processo"] = num_process
	df_textos_paginas["publicacao"] = publicacoes
	df_textos_paginas["numeros_paginas"] = num_pags
	df_textos_paginas["nome_documento"] = nome_docs
	df_textos_paginas["nomes_pastas"] = nome_pst
	df_textos_paginas["estado"] = "AM"	

	


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

	if len(df_textos_paginas["nomes_pastas"]) == 0:
		print("arquivo",num_arq,"vazio")
	else:	

		frag = df_textos_paginas["nomes_pastas"].str.split("-", n=2, expand = True)
		df_textos_paginas["dia"] = frag[0]
		df_textos_paginas["mes"] = frag[1]
		df_textos_paginas["ano"] = frag[2]

		df_textos_paginas["data_decisao"] = None
		df_textos_paginas["orgao_julgador"] = None
		df_textos_paginas["tipo_publicacao"] = None
		df_textos_paginas["tipos_processuais"] = None
		df_textos_paginas["comarcas"] = None
		df_textos_paginas["representantes"] = None
		df_textos_paginas["assuntos"] = None

		df_textos_paginas = df_textos_paginas[["numero_processo", "estado","publicacao","numeros_paginas","tipos_processuais", "assuntos","comarcas",
		"representantes","dia", "mes","ano","nome_documento","nomes_pastas","data_decisao","orgao_julgador","tipo_publicacao"]]

		# gera o csv com o DF final

		print(df_textos_paginas[["numero_processo", "estado","publicacao","numeros_paginas"]])

		dir_path = str(os.path.dirname(os.path.realpath(__file__)))
		path = dir_path + f'\Diarios_processados_AM_csv_'+str(ano)
		Path(path).mkdir(parents=True, exist_ok=True)
		

		df_textos_paginas.to_csv(path+"\Diarios_publicacoes_AM_"+str(df_textos_paginas["nomes_pastas"][0])+'_'+str(num_arq)+".csv", index = False)


		# converte para JSON

		# result = df_textos_paginas.to_json(orient="records", force_ascii = False)
		# parsed = json.loads(result)
		# with open('data_AM_'+ano+'_'str(nome_pst[0])+'_'+str(num_arq)+'.json', 'w', encoding ='utf-8') as fp:
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