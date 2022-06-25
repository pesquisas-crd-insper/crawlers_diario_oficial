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



############################## função para cortar os textos dos diários ####################################################



def Separar_textos_paginas(ano):

	# seleciona a pasta de acordo com o ano
	diret = r'.\Diarios_AM_'+ano


	# listas as pastas
	pastas = os.listdir(diret)




	# iteração sobre os arquivos dentro das pastas

	for b in tqdm(range(len(pastas))):
		nome_pasta = os.path.join(diret, pastas[b])
		arquivos = os.listdir(nome_pasta)
		

		
		for a in range(len(arquivos)):

			# prepara as listas com os valores a serem usados
			numeros_paginas =[]
			nome_doc = []
			nomes_pastas =[]
			vlrs_unific= [] # lista que salva os valores que identificam os parágrafos
			txt_unific = []
			sem_lines = []
			posicao = []

			## lista para verificar as flags escolhidas
			caracteristicas =[]
			print(nome_pasta,":",arquivos[a])
			nome = os.path.join(nome_pasta, arquivos[a])
			# print(nome)

			num_pag = 0 # inicio da contagem da página

			with fitz.open(nome) as pdf:
				for pagina in pdf:
					num_pag = num_pag + 1
					blocks = pagina.get_text("dict")['blocks'] # organiza o texto na forma de dict e separa nas seções do documento

					# print(blocks)
					# z=input("")

					# itera para cada seção

					for o in range(len(blocks)):

						# só faz isso para as seções que possuem a subseção "lines"		
						try:
							lines = blocks[o]["lines"]

								# itera para cada linha

							txt_block = []
							for x in range(len(lines)):

								# dentro das linhas seleciona os spans

								spans = lines[x]["spans"]
								
								# para cada spam:
								
								for u in spans:

									tam = str(u['size']).split(".")[0]
									flag =str(u['flags'])
									posic = str(u['bbox'][0]).split(".")[0]
									posic = int(posic)
									# print(posic)
									# z=input("")

									## para o teste previo de verificar as flags (com posição pq esse bot utiliza na junção)	
									caracteristicas.append((tam,flag,posic))

									# caracteristicas.append((tam,flag))

									if tam == "7" and flag == "4" or tam == "7" and flag =="20" or tam == "8" and flag == "4": 
										txt_block.append(u['text'].strip()) # separa todos os textos de cada bloco e salva na lista para unificação


									# para verificar o que aparece nos padrões das flags
							
									# if tam == "7" and flag == "4":
									# 	print("\n\n PADRÃO 2\n\n",u['text'])
									# 	z = input("")
									# if tam == "9" and flag == "4":
										# print("\n\n PADRÃO 3\n\n",u['text'])	
										# z = input("")
									
									
							# unifica os blocos dos textos, salvando também os números das páginas, pastas e arquivos								

							if len(txt_block) > 0:
								
								txt_fim = " ".join(txt_block)
								txt_unific.append(txt_fim)
								numeros_paginas.append(num_pag)
								nomes_pastas.append(nome_pasta[-10:])
								nome_doc.append(arquivos[a])
								if posic < 300:
									posicao.append("lado A")
								else:
									posicao.append("lado B")
							
							# caso o texto do bloco seja vazio, unifica um texto vazio para manter a mesma quantidade d eitens da lista
							else:
								txt_fim = " "
								txt_unific.append(txt_fim)
								numeros_paginas.append(num_pag)
								nomes_pastas.append(nome_pasta[-10:])
								nome_doc.append(arquivos[a])
								if posic < 300:
									posicao.append("lado A")
								else:
									posicao.append("lado B")
							
								
						
						# caso não tenha a seção lines salva nessa outra lista o número do bloco (sem utilidade)
						except:
							sem_lines.append(blocks[o]["number"])


			## contabilização da quantidade de flags mais frequentes
									
			# nome_acao = pd.DataFrame()
			# nome_acao["Ação"] = caracteristicas							
			# nome_acao = pd.DataFrame(nome_acao.groupby(["Ação"])["Ação"].count())
			# nome_acao.columns = ["quantidade"]
			# nome_acao = nome_acao.reset_index()						

			# print(nome_acao.sort_values(by=['quantidade'],ascending=False))
			# nome_acao.sort_values(by=['quantidade'],ascending=False, inplace= True)
			# nome_acao.to_excel("valores_flags.xlsx", index = False)
			# z = input("")


			# função que faz a junção dos blocos com base no valor do parágrafo
			# print("Temos",len(txt_unific),"publicações")
			Juntar_blocks(numeros_paginas,nome_doc, nomes_pastas,txt_unific,ano,a,posicao)								
			
			# retorna as listas (antes de fazer a junção)
			# return numeros_paginas, nome_doc, nomes_pastas, vlrs_unific, txt_unific
	


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
		print("arquivo vazio!")
		z = input("")
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


		dir_path = str(os.path.dirname(os.path.realpath(__file__)))
		path = dir_path + f'\Diarios_processados_AM_csv_'+str(ano)
		Path(path).mkdir(parents=True, exist_ok=True)
		

		df_textos_paginas.to_csv(path+"\Diarios_publicacoes_AM_"+str(df_textos_paginas["nomes_pastas"][0])+'_'+str(num_arq)+".csv", index = False)

		time.sleep(0.5)

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