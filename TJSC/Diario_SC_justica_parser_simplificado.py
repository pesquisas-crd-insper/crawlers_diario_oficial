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
	dia = re.findall(',*\s*(.\d{1,2}\s)',dt_ext)[0].strip()
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

	print(dataFormatada)
	# z= input("")
	
	return dataFormatada


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
		pub = pub.strip()	
		publis_l.append(pub)
		
	# print("vários")

	return publis_l


##################################################################################################
def Caracteristicas(caracteristicas):

	caract = pd.DataFrame()
	caract["valores"] = caracteristicas							
	caract = pd.DataFrame(caract.groupby(["valores"])["valores"].count())
	caract.columns = ["quantidade"]
	caract = caract.sort_values(by=['quantidade'],ascending=False)						
	caract = caract.reset_index()

	# print(caract)
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

	diret = r'./Diarios_SC_'+ano

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

			numeros_paginas, nome_doc, nomes_pastas, txt_unific, sem_lines = processa_texto(ano,str(arquivos[a]),nome, 0)
			data_ajust = nomes_pastas[-1]
			nomes_pastas = [data_ajust if value=="NADA" else value for value in nomes_pastas]
			Juntar_blocks(numeros_paginas,nome_doc,nomes_pastas,txt_unific,ano,a)								
			# return numeros_paginas,	nome_doc, nomes_pastas, txt_unific



def processa_texto(ano,arquivo, nome, verif_caract, tam_1=0, flag_1=0,tam_2=0, flag_2=0):

	# print("os tamanhos são:",tam_1, flag_1,tam_2,flag_2)
	numeros_paginas =[]
	nome_doc = []
	nomes_pastas =[]
	txt_unific = []
	sem_lines = []

	## lista para verificar as flags escolhidas
	caracteristicas =[]

	# contagem dos números das páginas
	num_pag = 0
	data_ajust = 'NADA'

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
							caracteristicas.append((tam,flag))
							
							# if num_pag == 1:
							# 	print(u['text'])
							# 	z = input("")
						
							if num_pag == 1:
								if int(ano) <= 2013:
									if re.search('\d\sde\s.+de\s\d{4}',u['text']) and tam == "10" and flag =="4":
										data_ajust = Convert_data(str(u['text']))
								else:	
									if re.search('\d{1,2}\sde\s.+',u['text']):
										parte_data = re.search('\d{1,2}\sde\s.+',u['text']).group().strip()
										str_data = parte_data+" de "+str(ano)
										# print(str_data)
										# z= input("")
										data_ajust = Convert_data(str_data)

									
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

							# if tam == "7" and flag == "0" or tam == "7" and flag == "4":
							# 	txt_block.append(u['text'].strip())
								
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
						nomes_pastas.append(data_ajust)

				
					# caso o texto do bloco seja vazio, unifica um texto vazio para manter a mesma quantidade d eitens da lista
					else:	
						txt_fim = "NADATEM"
						txt_unific.append(txt_fim)
						numeros_paginas.append(num_pag)
						nome_doc.append(str(arquivo))
						nomes_pastas.append(data_ajust)

	# 			# se não tiver as linhas, salva em outra lista - somente para conferência, não tem utilidade.					
				
				except:
					sem_lines.append(blocks[o]["number"])

	if verif_caract == 0:				
		verif_caract, tam_1, flag_1,tam_2, flag_2 = Caracteristicas(caracteristicas)
		numeros_paginas, nome_doc, nomes_pastas, txt_unific, sem_lines = processa_texto(ano,arquivo, nome, verif_caract,tam_1, flag_1, tam_2, flag_2)
		# print(len(numeros_paginas))
		# print(len(nome_doc))
		# print(len(nomes_pastas))
		# print(len(txt_unific))
		# print(nomes_pastas)
		# z= input("")
		return numeros_paginas, nome_doc, nomes_pastas, txt_unific, sem_lines
	else:
		return numeros_paginas, nome_doc, nomes_pastas, txt_unific, sem_lines


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
	# z = input("")

	pattern_sepa = re.compile("\s---\s|----\s*\d{1,2}\s*-|\d{1,2}\s*-\s*Ed. \d{3,5}-\d{2}|\d{1,2}-Ed\.\d{4,6}|\d{1,2}\s*-\s*Ed. \d{3,5}\/\d{2}")
	pattern_init = re.compile('ADV:|\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{4}\.\d{3,7}-.*\d|\d{4}\.\d{3,7}-\s*\d|\d{2,4}\.\d{2}\.\d{3,7}-\s*\d')
	pattern_num = re.compile('\d{2,7}(?:-|.{2}).\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}|\d{4}\.\d{3,7}-\d|\d{2,3}\.\d{2}\.{3,7}-\d|\d{4}\.\d{3,7}-\s*\d|\d{2,4}\.\d{2}\.\d{3,7}-\s*\d')


	for txt,num,doc,pst in zip(txt_unific,numeros_paginas,nome_doc,nomes_pastas):
	
		## regra da pesquisa do número CNJ dentro do texto da publicação
		# if num > 2293:
		# 	# if re.search('\d{2,4}\.\d{2}\.\d{3,7}-\s*\d', txt.replace("\n","")):
		# 	print(txt)
		# 	z= input("")

		if re.search(pattern_init, txt.replace("\n","")): # pesquisa o padrão em todas as linhas da publicação (dentro do limite de caracteres)
			
			# if num > 2293:
			# 	print("----",txt)
			# 	z= input("")

			if re.search(pattern_sepa,txt[25:].replace("\n","")):

				separacoes = re.findall(pattern_sepa,txt)

				num_caract = []
				for item in separacoes:
					num_caracter = txt.find(item)
					if num_caracter not in num_caract:
						num_caract.append(num_caracter)

					# tratamento para o caso de termos dois números CNJ iguaus na mesma página, ele verifica a próxima posição
					else:
						num_caracter = txt.find(item,num_caract[-1]+28,len(txt)) # por default são 28, porque é maior que um número CNJ
						num_caract.append(num_caracter)
				
				num_caract = [0 if numero < 0 else numero for numero in num_caract]
				partes = separacao_padroes(num_caract,txt)


				for f in range(len(partes)):
					if re.search(pattern_sepa,partes[f][:20]):
						publicacoes.append(partes[f]) 
						num_pags.append(num)
						nome_docs.append(doc)
						nome_pst.append(pst)
						pular = False
					else:
						if len(publicacoes) > 0:
							partes[f] = publicacoes[-1]+" "+partes[f]  # unifica o texto atual com a publicação anterior
							del publicacoes[-1] # deleta da lista a publicação anterior
							publicacoes.append(partes[f])
						else:
							publicacoes.append(partes[f]) 
							num_pags.append(num)
							nome_docs.append(doc)
							nome_pst.append(pst)
							pular = False		
					
			else:
				publicacoes.append(txt) 
				num_pags.append(num)
				nome_docs.append(doc)
				nome_pst.append(pst)
				pular = False

			
	
		# caso ele não encontre o padrão CNJ e essa publicação não seja a primeira da lista 
		else:
			if re.search("^Portaria|^ATO|E D I T A L|PORTARIA N.",txt,re.IGNORECASE):
				pular = True
			else:
				if len(publicacoes)>=1 and re.search("NADATEM",txt,re.IGNORECASE) == None and pular == False: #verifica se atingiu a quantidade máxima de unificações (4) sem encontrar um padrão CNJ ou se é a primeira da lista
					txt = publicacoes[-1]+" "+txt  # unifica o texto atual com a publicação anterior
					del publicacoes[-1] # deleta da lista a publicação anterior
					publicacoes.append(txt) # junta a nova publicação unificada na lista (o número da página e o nome do doc se mantém onde a publicação começa)
						
				else:
					pass
				
		


	


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
			
			if len(publicacoes_l) > 0 and re.search(r"----\s*\d{1,2}\s*-",publicacoes_l[-1]):
				#270
				try:
					nm_proc = re.search(pattern_num,publicacoes[n][:100]).group().replace(" ","")
					if len(num_process_l) > 0:
						proces_ant = num_process_l[-1]
						if proces_ant == nm_proc or len(publicacoes_l[-1]) < 210:
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
					if len(publicacoes_l) >0:
						publicacoes[n] = publicacoes_l[-1]+" "+publicacoes[n]  # unifica o texto atual com a publicação anterior
						del publicacoes_l[-1] # deleta da lista a publicação anterior
						publicacoes_l.append(publicacoes[n])		


			else:
				try:
					nm_proc = re.search(pattern_num,publicacoes[n][:420]).group().replace(" ","") # se encontrar o padrão completo, separa o número
					# print(nm_proc)
					if len(num_process_l) > 0:
						proces_ant = num_process_l[-1]
						if proces_ant == nm_proc or len(publicacoes_l[-1]) < 210:
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
					if len(publicacoes_l) >0:
						publicacoes[n] = publicacoes_l[-1]+" "+publicacoes[n]  # unifica o texto atual com a publicação anterior
						del publicacoes_l[-1] # deleta da lista a publicação anterior
						publicacoes_l.append(publicacoes[n])
				
		# print("agora temos",len(publicacoes_l))
		# print(publicacoes_l[-1])


		##### PARA CONFERÊNCIA - DESCOMENTAR CASO QUEIRA VERIFICAR O CORTE FINAL DAS PUBLICAÇÕES NA ORDEM - APERTAR ENTER A CADA PUBLICAÇÃO
		# qtdade = 0
		# for item,num in zip(publicacoes_l,num_pags_l):
		# 	qtdade = qtdade+1
		# 	print("Quantidade avaliada:",qtdade)
		# 	if num > 329:
		# 		print("página", num)
		# 		print(item)
		# 		print("-----------------")
		# 		z = input('')
		
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
		df_textos_paginas["estado"] = "SC"
		df_textos_paginas["tipos_processuais"] = None
		df_textos_paginas["comarcas"] = None
		df_textos_paginas["representantes"] = None
		df_textos_paginas["assuntos"] = None

		# print(df_textos_paginas[["numero_processo", "publicacao","numeros_paginas","nomes_pastas"]])
		# print("Temos",len(df_textos_paginas),"nesse data frame")


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
		path = dir_path + f'\Diarios_processados_SC_csv_'+str(ano)
		Path(path).mkdir(parents=True, exist_ok=True)

		# gera o excel com o DF final

		df_textos_paginas.to_csv(path+"\Diarios_publicacoes_SC_"+str(df_textos_paginas["nomes_pastas"][0])+"_"+str(num_arq)+".csv", index = False)
		# df_textos_paginas.to_excel(path+"\Diarios_publicacoes_SC_"+str(df_textos_paginas["nomes_pastas"][0])+"_"+str(num_arq)+".xlsx", index = False)

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