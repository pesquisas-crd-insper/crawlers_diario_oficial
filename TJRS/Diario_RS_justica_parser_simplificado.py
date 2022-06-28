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

	# print(dataFormatada)
	# z= input("")
	
	return dataFormatada


###################################################################################################################
def ajusta_lista(txt_block):

	# print("entrou")

	bloco = []
	resto = []
	for trecho in txt_block:
		if len(bloco) == 0:
			bloco.append(trecho[0])
			bloco.append(trecho[1])
			bloco.append(trecho[2])
		else:
			if trecho[0] == bloco[0]:
				bloco.append(trecho[2])
			else:
				resto.append(trecho)

	text = " ".join(bloco[2:])
	bloco[2] = text			
	bloco = bloco[:3]
	return bloco, resto



##################################################################################################################
def Organiza_blocos(txt_block):

	# print("entrou")


	# txt_block.sort()
	# print(txt_block)
	# print("------------")
	

	# z = input("")
	sub_blocks = []
	resto = [1]

	while True:
		# print(len(resto))
		# z = input("")
		if len(resto) == 0:
			break
		else:
			# print("aqui")
			bloco, resto = ajusta_lista(txt_block)
			txt_block = resto
			sub_blocks.append(bloco)


	# for item in sub_blocks:
	# 	print(item)
	# 	print("********")
	# 	z = input("")


	return sub_blocks	


###################################################################################################################

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

							# Função para separar os textos das publicações

def Separar_textos_paginas(ano):

	# diretório com as pastas e os dados

	diret = r'./Diarios_RS_'+ano

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
									# posic_1 = str(u['bbox'][0]).split(".")[0]
									# posic_2 = str(u['bbox'][1]).split(".")[0]

									# if tam == "7" and flag == "0" or tam == "7" and flag == "4":
									# 	# print("deu")
									# 	print(posic_1, posic_2, u['text'])
									# 	z = input('')
									

									# print(tam,flag)
									# print(posic_1,posic_2)
									# print(u['text'])
									# z = input("")

									if tam == "7" and flag == "0" or tam == "7" and flag == "4":
										# txt_block.append((posic_1, posic_2, u['text'].strip())) # separa todos os textos de cada bloco e salva na lista para unificação
										txt_block.append(u['text'].strip())
										# print(posic_1, posic_2, u['text'])
										# print(txt_block)
										# z = input('')
			# 						
			# 						## para verificar o que aparece nos padrões das flags
							
			# 						# if tam == "7" and flag == "16":
			# 						# 	print("\n\n PADRÃO 2\n\n",num_pag,"\n\n",u['text'])
			# 						# 	z = input("")
			# 						# # if tam == "9" and flag == "4":
			# 						# 	print("\n\n PADRÃO 3\n\n",u['text'])	
			# 						# 	z = input("")

						
							if len(txt_block) > 0:
								# print("tem")
								# blocos_finais = Organiza_blocos(txt_block)
								# for item in blocos_finais:
								# 	txt_unific.append(item)
								txt_fim = " ".join(txt_block)
								txt_unific.append(str(txt_fim))
								numeros_paginas.append(num_pag)
								nome_doc.append(str(arquivos[a]))
								nomes_pastas.append("01-01-2012")

						
							# caso o texto do bloco seja vazio, unifica um texto vazio para manter a mesma quantidade d eitens da lista
							else:
								
								txt_fim = "NADATEM"
								txt_unific.append([posic_1,posic_2,txt_fim])
								numeros_paginas.append(num_pag)
								nome_doc.append(str(arquivos[a]))
								nomes_pastas.append("01-01-2012")

								
					
							

			# 			# se não tiver as linhas, salva em outra lista - somente para conferência, não tem utilidade.					
						
						except:
							sem_lines.append(blocks[o]["number"])



			# # contabilização da quantidade de flags mais frequentes
									
			# nome_acao = pd.DataFrame()
			# nome_acao["Ação"] = caracteristicas							
			# nome_acao = pd.DataFrame(nome_acao.groupby(["Ação"])["Ação"].count())
			# nome_acao.columns = ["quantidade"]
			# nome_acao = nome_acao.reset_index()						

			# print(nome_acao.sort_values(by=['quantidade'],ascending=False))
			# z = input("")
			
			nomes_pastas = [data_ajust if value=="NADA" else value for value in nomes_pastas]
			# # print(nomes_pastas[:10])
				# txt_unific.sort()
			# for item in txt_unific:
			# 	print(item)
			# 	z = input("")
			Juntar_blocks(numeros_paginas,nome_doc,nomes_pastas,txt_unific,ano,a)								
			# return numeros_paginas,	nome_doc, nomes_pastas, txt_unific
	

###############################################################################

 			###### Função para separar, unificar e selecionar as publicações de interesse e Gerar um Banco de dados em JSON #########


def Juntar_blocks(numeros_paginas,nome_doc, nomes_pastas, txt_unific,ano,num_arq):


	publicacoes = []
	num_pags = []
	nome_docs = []
	nome_pst = []
	num_process =[]
	posicao_atual = []
	


	print("a página maior é",max(numeros_paginas))
	# print('qtdade textos',len(txt_unific))
	# print('qtdade num_pag',len(numeros_paginas))
	# print('qtdade nomes_docs',len(nome_doc))
	# print('qtadade nomes_pastas',len(nomes_pastas))
	# z = input("")

	pattern_sepa = re.compile('CNJ:*\s*\d{2,7}(?:-|.{2}).\d{2}\.\s*\d{4}\.\s*\d\.\s*\d{2}\.\s*\d{4}')
	pattern_init = re.compile('\d{2,7}(?:-|.{2}).\d{2}\.\s*\d{4}\.\s*\d\.\s*\d{2}\.\s*\d{4}')
	

	for txt,num,doc,pst in zip(txt_unific,numeros_paginas,nome_doc,nomes_pastas):

		## regra da pesquisa do número CNJ dentro do texto da publicação

		text = txt[:150].replace("\n","")
		# if num_arq == 1:
		# 	print(text)
		# 	z = input("")
		
		# if num == 4:
		# 	print(txt)
		# 	z = input("")
	
		## início da busca
		# txt = txt.replace("\n","")
		
		if re.search(pattern_init,text): # pesquisa o padrão em todas as linhas da publicação (dentro do limite de caracteres)

			separacoes = re.findall(pattern_sepa,txt[150:])
			if len(separacoes) > 0:
				# if num == 4:
				# print(num)
				# print(separacoes)
				# z = input("")
			
				
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
					if re.search(pattern_init,partes[f][:40]):
						nm_proc = re.search(pattern_init,partes[f][:40]).group().replace(" ","") # se encontrar o padrão completo, separa o número
						num_process.append(nm_proc) # salva na lista
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

				nm_proc = re.search(pattern_init,txt).group().replace(" ","") # se encontrar o padrão completo, separa o número
				num_process.append(nm_proc) # salva na lista			
				publicacoes.append(txt) 
				num_pags.append(num)
				nome_docs.append(doc)
				nome_pst.append(pst)
				pular = False					


		# caso ele não encontre o padrão CNJ e essa publicação não seja a primeira da lista 

		### se o bbox for do outro lado ele aceita uma...tenho que inserir esse atributo na característica
		else:	
			if re.search("NADATEM",txt,re.IGNORECASE):
				pular == True 
			else:	
				if len(publicacoes)>=1 and pular == False:
					# if num == 15:
					# 	print("*****",txt)
					txt = publicacoes[-1]+" "+txt  # unifica o texto atual com a publicação anterior
					del publicacoes[-1] # deleta da lista a publicação anterior
					publicacoes.append(txt) # junta a nova publicação unificada na lista (o número da página e o nome do doc se mantém onde a publicação começa)
			

		
		
		


	###### PARA CONFERÊNCIA - DESCOMENTAR CASO QUEIRA VERIFICAR O CORTE FINAL DAS PUBLICAÇÕES NA ORDEM - APERTAR ENTER A CADA PUBLICAÇÃO
	# qtdade = 0
	# for item,num in zip(publicacoes,num_pags):
	# 	qtdade = qtdade+1
	# 	print("Quantidade avaliada:",qtdade)
	# 	print("página:",num)
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
	df_textos_paginas["estado"] = "RS"	

	


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
		print(num_arq,"vazio!")
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
		path = dir_path + f'\Diarios_processados_RS_csv_'+str(ano)
		Path(path).mkdir(parents=True, exist_ok=True)
		

		df_textos_paginas.to_csv(path+"\Diarios_publicacoes_RS_"+str(df_textos_paginas["nomes_pastas"][0])+'_'+str(num_arq)+".csv", index = False)

		
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