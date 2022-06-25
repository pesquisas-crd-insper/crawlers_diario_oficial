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




#################################################  Função que separa os textos dos diários  #################################################

def Separar_textos_paginas(ano):
	
	diret = r'./Diarios_AC_'+ano

	pastas = os.listdir(diret)



	## lista para verificar as flags escolhidas
	caracteristicas =[]

	# iteração sobre as pastas

	for b in tqdm(range(len(pastas))):
		nome_pasta = os.path.join(diret, pastas[b])
		arquivos = os.listdir(nome_pasta)
		# print(pastas[b])
		
		
		for a in range(len(arquivos)):
			numeros_paginas =[]
			nome_doc = []
			nomes_pastas =[]
			txt_unific = []
			sem_lines = []
	
			print(pastas[b],":",arquivos[a])

			nome = os.path.join(nome_pasta, arquivos[a])

			# print(nome)
			# z= input("")

			# controle dos números das páginas
			num_pag = 0

			# itera sobre os arquivos
			try:
				with fitz.open(nome) as pdf:
					for pagina in pdf:
						num_pag = num_pag + 1

						# separa o texto em blocos

						# blocks = pagina.get_text()

						blocks = pagina.get_text("dict")['blocks']
						
						# print(blocks)
						# z= input("")

						# para cada bloco, separa em linhas
						for o in range(len(blocks)):
							try:
								lines = blocks[o]["lines"]
								txt_block = []	

								# para cada	linhas, separa os spans
								for x in range(len(lines)):
									spans = lines[x]["spans"]

									# para cada span, separar os texto
									for u in spans:

										tam = str(u['size']).split(".")[0]
										flag =str(u['flags'])

										## para o teste previo de verificar as flags	
										caracteristicas.append((tam,flag))
										# if num_pag == 1:
										# 	print((tam,flag))
										# 	print(u['text'].strip())
										# 	z = input("")

										if tam == "7" and flag == "0" or tam == "7" and flag == "4" or tam == "7" and flag == "16" or tam == "8" and flag == "0": 
											txt_block.append(u['text'].strip())

								# if num_pag == 1:
								# print(txt_block)
								# z= input("")
										

										## para verificar o que aparece nos padrões das flags
								
										# if tam == "5" and flag == "16":
										# 	print("\n\n PADRÃO 2\n\n",u['text'])
										# 	z = input("")
										# if tam == "7" and flag == "16":
										# 	print("\n\n PADRÃO 3\n\n",u['text'])	
										# 	z = input("")
								
								# unifica os textos de um bloco e acrescenta o número das páginas, pastas e nomes dos arquivos 

								if len(txt_block) > 0:
									txt_fim = " ".join(txt_block)
									# if num_pag == 1:
									# 	print(txt_fim)
									# 	z= input("")
									txt_fim = txt_fim.replace("*","")
									txt_unific.append(txt_fim)
									numeros_paginas.append(num_pag)
									nomes_pastas.append(pastas[b])
									nome_doc.append(arquivos[a])
									
								# caso o texto do bloco seja vazio, unifica um texto vazio para manter a mesma quantidade de itens da lista
								else:
									txt_fim = " "
									# txt_fim = txt_fim.replace("*","")
									txt_unific.append(txt_fim)
									numeros_paginas.append(num_pag)
									nomes_pastas.append(pastas[b])
									nome_doc.append(arquivos[a])
									
							# controle dos casos que não foram, sem utilidade exceto conferência

							except:
								sem_lines.append(blocks[o]["number"])	


				# print(numeros_paginas)
				# print(nome_doc)
				# print(nomes_pastas)
				# print(txt_unific)
				# # print(sem_lines)	
				# z= input("")			
				
				# contabilização da quantidade de flags mais frequentes
									
				# nome_acao = pd.DataFrame()
				# nome_acao["caracteristicas"] = caracteristicas							
				# nome_acao = pd.DataFrame(nome_acao.groupby(["caracteristicas"])["caracteristicas"].count())
				# nome_acao.columns = ["quantidade"]
				# nome_acao = nome_acao.reset_index()						

				# print(nome_acao.sort_values(by=['quantidade'],ascending=False))
				# z = input("")						



				# função que junta os blocos						

				Juntar_blocks(numeros_paginas,nome_doc, nomes_pastas, txt_unific,ano,a)								
				# return numeros_paginas,nome_doc, nomes_pastas, txt_unific
			except:
				print(nome,"está corrompido!")

###############################################################################

def Juntar_blocks(numeros_paginas,nome_doc, nomes_pastas, txt_unific, ano,num_arq):


	publicacoes = []
	num_pags = []
	nome_docs = []
	nome_pst = []
	num_process =[]


	control =0
	for txt,num,doc,pst in zip(txt_unific,numeros_paginas,nome_doc,nomes_pastas):
		
		## regra da pesquisa do número CNJ dentro do texto da publicação
		txt = txt.replace("\n","")
		inici_txt = txt[:150]
		# print(inici_txt)
		# # print(txt)
		# z= input("")


		
		if re.search('Classe:|Acórdão n.º|Acórdão nº:|Nº \d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|nº \d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|Classe :',inici_txt, re.IGNORECASE): # pesquisa o padrão na primeira linha da publicação
			
			try:
				nm_proc = re.search('\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}',inici_txt, re.IGNORECASE).group().replace(" ","") # se encontrar o padrão completo, separa o número
				# num_process.append(nm_proc) # salva na lista
				# salva nas listas a publicação e as demais informações dela (página, documento, pasta)	
				publicacoes.append(txt.strip()) 
				num_pags.append(num)
				nome_docs.append(doc)
				nome_pst.append(pst)
				control = 0
			except:

				publicacoes.append(txt.strip()) 
				num_pags.append(num)
				nome_docs.append(doc)
				nome_pst.append(pst)
				control = 1
				# print(txt)
				# z= input("")


		
		else:	
		
			rgx = re.compile('\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}')
			numeracoes = rgx.findall(txt[:120])
			
			if len(numeracoes) > 1:
				if len(publicacoes)>=1 and re.search("^Disponibilizado -",inici_txt,re.IGNORECASE) == None: #verifica se atingiu a quantidade máxima de unificações (4) sem encontrar um padrão CNJ ou se é a primeira da lista
					txt = publicacoes[-1]+" "+txt  # unifica o texto atual com a publicação anterior
					del publicacoes[-1] # deleta da lista a publicação anterior
					publicacoes.append(txt.strip()) # junta a nova publicação unificada na lista (o número da página e o nome do doc se mantém onde a publicação começa)
						


			else:
				if re.search('\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}',txt[:60], re.IGNORECASE): # pesquisa o padrão na primeira linha da publicação
					# nm_proc = re.search('\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}',txt[:60], re.IGNORECASE).group().replace(" ","") # se encontrar o padrão completo, separa o número
					# num_process.append(nm_proc) # salva na lista
			

					# salva nas listas a publicação e as demais informações dela (página, documento, pasta)	
					publicacoes.append(txt.strip()) 
					num_pags.append(num)
					nome_docs.append(doc)
					nome_pst.append(pst)
					control = 0
			
				# caso ele não encontre o padrão CNJ e essa publicação não seja a primeira da lista 
				else:
					if re.search('ADV:',inici_txt, re.IGNORECASE): 
						# print(txt)
						publicacoes.append(txt.strip()) 
						num_pags.append(num)
						nome_docs.append(doc)
						nome_pst.append(pst)
						# z= input("")
						control = 0


					else:
						if control == 1:
							txt = publicacoes[-1]+" "+txt  # unifica o texto atual com a publicação anterior
							del publicacoes[-1] # deleta da lista a publicação anterior
							publicacoes.append(txt.strip()) # junta a nova publicação unificada na lista (o número da página e o nome do doc se mantém onde a publicação começa)
						else:
							if len(publicacoes)>=1 and re.search("^Disponibilizado -",txt,re.IGNORECASE) == None:
								txt = publicacoes[-1]+" "+txt  # unifica o texto atual com a publicação anterior
								del publicacoes[-1] # deleta da lista a publicação anterior
								publicacoes.append(txt.strip()) # junta a nova publicação unificada na lista (o número da página e o nome do doc se mantém onde a publicação começa)
										
							else:
								pass

		
	if len(publicacoes) == 0:
		print(num_arq,"vazio!")
	
	else:
		publicacoes_l = []
		num_pags_l = []
		nome_docs_l = []
		nome_pst_l = []
		num_process_l =[]			
		for n in range(len(publicacoes)):
			try:
				nm_proc = re.search('\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{4}\.\d{6}-\d|\d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}',publicacoes[n], re.IGNORECASE).group().replace(" ","") # se encontrar o padrão completo, separa o número
				num_process_l.append(nm_proc) # salva na lista
				publicacoes_l.append(publicacoes[n])
				num_pags_l.append(num_pags[n])
				nome_docs_l.append(nome_docs[n])
				nome_pst_l.append(nome_pst[n])	
			except:
				pass

		# print(len(num_process))
		# print(len(publicacoes_l))
		# print(len(num_pags_l))
		# print(len(nome_docs_l))
		# print(len(nome_pst_l))

	

		# #### PARA CONFERÊNCIA - DESCOMENTAR CASO QUEIRA VERIFICAR O CORTE FINAL DAS PUBLICAÇÕES NA ORDEM - APERTAR ENTER A CADA PUBLICAÇÃO
		# qtdade = 0
		# for item,num in zip(publicacoes,num_pags):
		# 	qtdade = qtdade+1
		# 	print("Quantidade avaliada:",qtdade)
		# 	print("página", num)
		# 	print(item)
		# 	print("-----------------")
		# 	z = input('')


		##################   FIM DO TRECHO PARA CONFERÊNCIA ##############################



		# gera o DF com as publicações e as demais informações

		df_textos_paginas = pd.DataFrame()
		df_textos_paginas["numero_processo"] = num_process_l
		df_textos_paginas["publicacao"] = publicacoes_l
		df_textos_paginas["numeros_paginas"] = num_pags_l
		df_textos_paginas["nome_documento"] = nome_docs_l
		df_textos_paginas["nomes_pastas"] = nome_pst_l
		df_textos_paginas["estado"] = "AC"	

	


		############ CONFERÊNCIA AMOSTRAL ALEATÓRIA - DESCOMENTAR CASO QUEIRA UMA AMOSTRA ALEATÓRIA DOS RECORTES  - APERTAR ENTER A CADA PUBLICAÇÃO


		# # agrupa por nome do documento
		# doc_agrup = pd.DataFrame(df_textos_paginas.groupby(["nome_documento"])["nome_documento"].count())
		# doc_agrup.columns = ["quantidade"]
		# doc_agrup = doc_agrup.reset_index()

		# # converte os nomes em uma lista e depois embaralha os nomes em uma ordem indeterminada
		# lista_nomes_docs = doc_agrup["nome_documento"].tolist()
		# random.shuffle(lista_nomes_docs)


		# Gera uma amostra aleatória de X publicações por documento para facilitar a conferência
		# for docu in lista_nomes_docs :
		# 	df_filter = df_textos_paginas["nome_documento"] == docu
		# 	amostra_trib = df_textos_paginas[df_filter]

		# 	amostra_trib = amostra_trib.sample(30)  # escolher a quantidade da amostra
		# 	for pub,doc,pag in zip(amostra_trib["publicacao"],amostra_trib["nome_documento"],amostra_trib["numeros_paginas"]):
		# 		print("documento:\t",doc,"\nPágina:\t",pag,"\nTexto publicação:\n",pub,"\n--------------")
				# z= input("")

	##################   FIM DO TRECHO PARA CONFERÊNCIA ##############################

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


		df_textos_paginas = df_textos_paginas[["numero_processo", "estado","publicacao","numeros_paginas","tipos_processuais","assuntos","comarcas",
		"representantes","dia", "mes","ano","nome_documento","nomes_pastas","data_decisao","orgao_julgador","tipo_publicacao"]]


		dir_path = str(os.path.dirname(os.path.realpath(__file__)))
		path = dir_path + f'\Diarios_processados_AC_csv_'+str(ano)
		Path(path).mkdir(parents=True, exist_ok=True)

		# gera o excel com o DF final

		# print(df_textos_paginas)
		
		df_textos_paginas.to_csv(path+"\Diarios_publicacoes_AC_"+str(df_textos_paginas["nomes_pastas"][0])+'_'+str(num_arq)+".csv", index = False)

		time.sleep(0.5)

		# converte para JSON

		# result = df_textos_paginas.to_json(orient="records", force_ascii = False)
		# parsed = json.loads(result)
		# with open('data_AC_'+str(nome_pst[0])+'_'+str(num_arq)+'.json', 'w', encoding ='utf-8') as fp:
		# 	json.dump(parsed, fp)


		# time.sleep(5)	

		# with open('data_AC.json', 'r', encoding ='utf-8') as fp:
		# 	data = json.loads(fp.read())
		# 	print(json.dumps(data, indent = 4, ensure_ascii=False))

		# print(json.dumps(parsed, ensure_ascii=False, indent=4)) 



##################################         Função principal que chama as demais   ###################################################

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