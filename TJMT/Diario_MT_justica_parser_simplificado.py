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

	# diretório com as pastas e os dados

	diret = r'./Diarios_MT_'+ano

	pastas = os.listdir(diret)



	# iteração das pastas para acessar os arquivos de PDF individualmente

	for b in tqdm(range(len(pastas))):
		
		nome_pasta = os.path.join(diret, pastas[b])
		arquivos = os.listdir(nome_pasta)
		
		# listas que receberão os dados

		

		for a in range(len(arquivos)):
			
			if "ministrativo" in arquivos[a] or "MINISTRATIVO" in arquivos[a]:
				print(arquivos[a],"é administrativo")
				pass 
			else:
				print(nome_pasta,arquivos[a])
				
				numeros_paginas =[]
				nome_doc = []
				nomes_pastas =[]
				txt_unific = []
				sem_lines = []

				## lista para verificar as flags escolhidas
				caracteristicas =[]


				nome = os.path.join(nome_pasta, arquivos[a])


				# contagem dos números das páginas
				num_pag = 0


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

										## para o teste previo de verificar as flags	
										caracteristicas.append((tam,flag))
										# if num_pag == 20:# and re.search("o presente termo",u['text'], re.IGNORECASE):
										# 	print(tam,flag)
										# 	print(u['text'])
										# 	z= input("") 
											
										if tam == "7" and flag == "0" or tam == "7" and flag =="16" or tam =="10" and flag == "0" or tam == "8" and flag =="0": 
											txt_block.append(u['text'].strip()) # separa todos os textos de cada bloco e salva na lista para unificação
									

										## para verificar o que aparece nos padrões das flags
								
										# if tam == "9" and flag == "0":
										# 	print("\n\n PADRÃO 2\n\n",u['text'])
										# 	z = input("")
										# # if tam == "9" and flag == "4":
										# 	print("\n\n PADRÃO 3\n\n",u['text'])	
										# 	z = input("")

								# unifica os textos de cada bloco e salva o número da página, nome do arquivo e a data
								if len(txt_block) > 0:
									txt_fim = " ".join(txt_block)
									txt_unific.append(str(txt_fim))
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


						
								

							# se não tiver as linhas, salva em outra lista - somente para conferência, não tem utilidade.					
							
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

				
				Juntar_blocks(numeros_paginas,nome_doc, nomes_pastas, txt_unific, ano, a)								
				# return numeros_paginas,	nome_doc, nomes_pastas, txt_unific
	

###############################################################################

 			###### Função para separar, unificar e selecionar as publicações de interesse e Gerar um Banco de dados em excel #########

def separacao_padroes(num_caract,txt):

	
	# insere o caracter final e orgniza a lista com os indices dos caracteres iniciais dos numeros dos processos em ordem
	num_caract.append(len(txt))	
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
		trecho = txt [num_comec:num_caract[h]]
		trecho = trecho.strip()
		publis.append(trecho)
		num_comec = num_caract [h]

	publis_l = []	
	for pub in publis:
		if re.search("XXXXX|\*\*\*\*\*\*\*\*\*\*\*\*\*\*|¯¯¯¯¯¯¯¯¯¯¯¯", pub):
			pedac = re.split("XXXXX|\*\*\*\*\*\*\*\*\*\*\*\*\*\*|¯¯¯¯¯¯¯¯¯¯¯¯",pub)
			# print(pedac)
			# z= input("")
			for ped in pedac:
				if len(ped)> 5:
					# print(ped)
					# z= input("")s
					ped = ped.strip()	
					publis_l.append(ped)
		else:
			publis_l.append(pub)		
	# print("vários")

	return publis_l


def Juntar_blocks(numeros_paginas,nome_doc, nomes_pastas,txt_unific,ano, num_arq):

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
	# z = input("")


	for txt,num,doc,pst in zip(txt_unific,numeros_paginas,nome_doc,nomes_pastas):
		
		## regra da pesquisa do número CNJ dentro do texto da publicação
		txt_1 = txt.replace("\n",'')
		patter_regex = re.compile('(?i)Protocolo Número/Ano:|XXXXXXXXXXXXXXXXXXXXXXXX|Processo Número:|\*\s\d\s-\s\d{1,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}[^,]|N*\.* \d{1,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}[^,]|Classe: CNJ-\d{1,5}\s|CLASSE CNJ|N(°|º) \d{1,7}(?:-|.{2}).\d{2}\.\d{4}\.\d{3}\.\d{4}[^,]|Protocolo:\s\d{3,6}\W\d{4}|intimação da parte autora\s*\n*|intimação das partes\s*\n*|intimação para advogado|N\. \d{1,7}(?:-|.{2}).\d{2}\.\d{4}|Intimação da Parte Requerida\s*\n*')
		pattern_num = re.compile("\d{3,6}\W\d{4}|\d{1,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{3,6}\s*\W\s*\d{4}|\d{1,7}(?:-|.{2}).\d{2}\.\d{4}\.\d{3}\.\d{4}|\d{1,7}(?:-|.{2}).\d{2}\.\d{4}")
		
			
		
	

		if re.search(patter_regex,txt):
			
			# if num == 131:
			# 	print(txt)
			# 	# print(numer_2)
			# 	z= input("")


			if re.search('Protocolo:\s\d{3,6}\W\d{4}',txt):
	
				numer = re.search('Protocolo:\s\d{3,6}\W\d{4}',txt).start()
				if len(publicacoes) > 0 and re.search('Protocolo:\s\d{3,6}\W\d{4}',txt[:40]) == None:
					publicacoes[-1] = publicacoes[-1]+" "+txt[0:numer-1]
				
				txt = txt[numer:]
				list_numbers = re.findall('Protocolo:\s\d{3,6}\W\d{4}',txt)

			else:
				list_numbers = []					

			numer_2 = re.findall('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX|N\. *\d{1,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}[^,]', txt)
			numer_3 = re.findall('Classe: CNJ-\d{3}\s|CLASSE CNJ', txt,re.IGNORECASE)
			numer_4 = re.findall('N(°|º) \d{1,7}(?:-|.{2}).\d{2}\.\d{4}\.\d{3}\.\d{4}[^,]', txt, re.IGNORECASE)
			numer_5 = re.findall("intimação da parte Autora\s\s|intimação das partes\s*\n*|intimação para advogado(a)|Intimação da Parte Requerida\s*\n*", txt, re.IGNORECASE)
			numer_6 = re.findall('N*\.* \d{1,7}(?:-|.{2}).\d{2}\.\d{4}[^,]', txt, re.IGNORECASE)
			numer_7 = re.findall('\d*\s-\s\d{1,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}[^,]',txt, re.IGNORECASE)
			list_numbers_2 = re.findall('Protocolo Número/Ano:|Processo Número:',txt)			


			# if num == 131:
			# 	# print(txt)
			# 	print(numer_2)
			# 	z= input("")

			numer_2 = list_numbers + list_numbers_2 + numer_2 + numer_5
			numer_3 = numer_3 + numer_4 + numer_6 + numer_7
	
			

			# gera uma lista com a posição do caracter onde está cada número CNJ
			num_caract_1 = []
			for item in numer_2:
				num_caracter = txt.find(item)
				if num_caracter not in num_caract_1:
					num_caract_1.append(num_caracter)

				# tratamento para o caso de termos dois números CNJ iguaus na mesma página, ele verifica a próxima posição
				else:
					num_caracter = txt.find(item,num_caract_1[-1]+28,len(txt)) # por default são 28, porque é maior que um número CNJ
					num_caract_1.append(num_caracter)
			
			num_caract_2 = []
			for item in numer_3:
				num_caracter = txt.find(item)
				if num_caracter not in num_caract_2:
					num_caract_2.append(num_caracter-43)

				# tratamento para o caso de termos dois números CNJ iguaus na mesma página, ele verifica a próxima posição
				else:
					num_caracter = txt.find(item,num_caract_2[-1]+28,len(txt)) # por default são 28, porque é maior que um número CNJ
					num_caract_2.append(num_caracter-43)


			num_caract = num_caract_1 + num_caract_2
			num_caract = [0 if numero < 0 else numero for numero in num_caract]	
			# if num == 14:
			# 	print(num_caract)
			# 	z= input("")
						
			publis = separacao_padroes(num_caract,txt)
			# if num == 14:
			# 	for item in publis:
			# 		print(item)
			# 		z= input("")


		else:
			publis = [txt]
			# if num == 14:
			# 	print(publis)
			# print("descartado")
		



		## início da busca

		for item in publis:
			# if num == 131:
			# 	# if re.search('N\.\s*\d{1,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', item):
			# 	print(item)
			# 	z = input("")
			inic_text = item[:90]
		

		
			if re.search(patter_regex,inic_text): # pesquisa o padrão em todas as linhas da publicação (dentro do limite de caracteres)
				
				# salva nas listas a publicação e as demais informações dela (página, documento, pasta)	
				if len(publicacoes) > 0 and len(publicacoes[-1])< 155:
					publicacoes[-1] = publicacoes[-1]+' '+item
					pula = False
				else:
					publicacoes.append(item)			
					num_pags.append(num)
					nome_docs.append(doc)
					nome_pst.append(pst)
					pula = False
		
			# caso ele não encontre o padrão CNJ e essa publicação não seja a primeira da lista 
			else:
				if re.search("Portaria|Despachos|Edital de|Atos do",txt[:40], re.IGNORECASE):
					pula = True
				
				else:	
					if len(publicacoes)>0 and re.search("^Disponibilizado -|PORTARIA\s*Nº",inic_text,re.IGNORECASE) == None and pula == False: #verifica se atingiu a quantidade máxima de unificações (4) sem encontrar um padrão CNJ ou se é a primeira da lista
						item = publicacoes[-1]+" "+item  # unifica o texto atual com a publicação anterior
						del publicacoes[-1] # deleta da lista a publicação anterior
						publicacoes.append(item) # junta a nova publicação unificada na lista (o número da página e o nome do doc se mantém onde a publicação começa)
							
					else:
						pass
		
		



	##################   FIM DO TRECHO PARA CONFERÊNCIA ##############################

	if len(publicacoes) == 0:
		print("arquivo", num_arq, "vazio")
	else:
		# print("tínhamos", len(publicacoes))
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


		# print("agora temos",len(publicacoes_l))


	###### PARA CONFERÊNCIA - DESCOMENTAR CASO QUEIRA VERIFICAR O CORTE FINAL DAS PUBLICAÇÕES NA ORDEM - APERTAR ENTER A CADA PUBLICAÇÃO

		# qtdade = 0
		# for item,num in zip(publicacoes_l,num_pags_l):
		# 	qtdade = qtdade+1
		# 	print("Quantidade avaliada:",qtdade)
		# 	#287
		# 	if num > 130:
		# 		print("página", num)
		# 		print(item)
		# 		print("-----------------")
		# 		z = input('')

		# gera o DF com as publicações e as demais informações

		# print(publicacoes_l[-1])

		df_textos_paginas = pd.DataFrame()
		df_textos_paginas["numero_processo"] = num_process_l
		df_textos_paginas["publicacao"] = publicacoes_l
		df_textos_paginas["numeros_paginas"] = num_pags_l
		df_textos_paginas["nome_documento"] = nome_docs_l
		df_textos_paginas["nomes_pastas"] = nome_pst_l
		df_textos_paginas["estado"] = "MT"	
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
		df_textos_paginas["tipos_processuais"] = None
		df_textos_paginas["comarcas"] = None
		df_textos_paginas["representantes"] = None
		df_textos_paginas["assuntos"] = None

		df_textos_paginas = df_textos_paginas[["numero_processo", "estado","publicacao","numeros_paginas","tipos_processuais","assuntos","comarcas",
		"representantes","dia", "mes","ano","nome_documento","nomes_pastas","data_decisao","orgao_julgador","tipo_publicacao"]]

		# gera o excel com o DF final
		# cria o diretório

		dir_path = str(os.path.dirname(os.path.realpath(__file__)))
		path = dir_path + f'\Diarios_processados_MT_csv_'+str(ano)
		Path(path).mkdir(parents=True, exist_ok=True)

		# print(df_textos_paginas[["numero_processo", "estado","publicacao","numeros_paginas"]])

		# gera o excel e o csv com o DF final

		df_textos_paginas.to_csv(path+"\Diarios_publicacoes_MT_"+str(df_textos_paginas["nomes_pastas"][0])+"_"+str(num_arq)+".csv", index = False)
		# df_textos_paginas.to_excel(path+"\Diarios_publicacoes_MT_"+str(df_textos_paginas["nomes_pastas"][0])+"_"+str(num_arq)+".xlsx", index = False)

		

		# converte para JSON

		# result = df_textos_paginas.to_json(orient="records", force_ascii = False)
		# parsed = json.loads(result)
		# with open('data_MT_'+str(nome_pst[0])+'_'+str(num_arq)+'.json', 'w', encoding ='utf-8') as fp:
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