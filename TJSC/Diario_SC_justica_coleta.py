import requests
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
from pathlib import Path
import sys, re, time, os, urllib.request


def baixar(path_final, link_inicial, cadernos, ed):

	print("Vamos tentar baixar os cadernos")
	for e in cadernos:
		try:
		    print(link_inicial % (str(ed), e))
		    response = urllib.request.urlopen(link_inicial % (str(ed), e), timeout = 5)
		    print("aguardando 2 seg") # caso não seja ele aguarda 15 seg
		    time.sleep(2)
		    file = open(path_final+"/"+ str(ed) + "_" + e + ".pdf", "wb")
		    file.write(response.read())
		    file.close()
		    time.sleep(1)
		except:
			print("*"*10)
			print("*"*10)
			print("*"*10)
			print()
			print("não conseguiu o caderno", e)
			print()
			print("*"*10)
			print("*"*10)
			print("*"*10)


def downloads_done(path_final, quantidade, ed, cadernos, link_inicial):
	
	
	cont = 0 # quantidade total de documentos
	desist = 0 # momento de desistência caso o site demore muito para responder
	
	while True:
		if cont == quantidade: # se a contagem identificar o mesmo número de item da quantidade total
			break # encerra o processo
		
		else:
			baixar(path_final, link_inicial, cadernos, ed)				
			
			print()
			print("estamos verificando na pasta:", path_final)
			
			cont = 0	
			for i in os.listdir(path_final): # caso haja downloads em curso ele verifica se todos já estão completos (extensão ".pdf")
				nome = str(i)
				if nome[-3:] == "pdf": 
					cont = cont+1  # E conta quantos tem depois de iterar todos os elementos da pasta

			
			print("Ainda falta(m)", quantidade-cont,"arquivos") # indica para o usuário quantos ainda faltam
			print("     ---------------      ")
			
			desist = desist + 1 # acrescenta 1 a desistência em cada verificação na pasta
			if desist == (quantidade+2): # se a desistência atingir a quantidade total + 2 elementos, ele desiste (ou seja, pelo menos 30s de tempo extra)
				cont = quantidade

					
	print("downloads finalizados!") # informa o encerramento do processo, acabado ou não.
	print("-----"*5)
	return


######################## função para gerar os números das edições de cada ano #################################

def gerar_numeros(ano):

    anos_todos = ["2012","2013","2014","2015","2016","2017","2018","2019","2020","2021"]
   
    linha = anos_todos.index(ano)
    arq = open('ANOS.txt', 'r') # abre o range das edições do ano escolhido pelo usuário no arquivo TXT
    linhas = arq.readlines() # lê o arquivo
    inic_fim = linhas[linha].split('-') # seleciona a linha do ano respectivo

    
    lista_num =[] #lista com os números do range do ano
    inicio = int(inic_fim[0])  # documento inicial disponível
    fim = int(inic_fim[1])# documento final disponível

    # gera o range do ano
    atual = 2760#inicio
    for k in range(2760, fim+1):
        lista_num.append(atual)
        atual = atual+1

    # retorna a lista    
    return lista_num    



####################### função para coletar os documentos  #####################################################

def main():

    # usuário escolhe o ano
    ano = input("Digite o ano com 4 dígitos (Ex: 2019):")

    # gera o diretório do ano
    dir_path = str(os.path.dirname(os.path.realpath(__file__)))
    path = dir_path + f'\Diarios_SC_'+ano
    Path(path).mkdir(parents=True, exist_ok=True)


    # gera o range do ano
    edicoes = gerar_numeros(ano)

    for ed in edicoes:

        # gera a pasta da edição

        print("baixando edição", ed, ' até a edição', edicoes[-1],"\n-------------")
        path_final = dir_path + f'\Diarios_SC_'+ano+'\\'+str(ed)
        Path(path_final).mkdir(parents=True, exist_ok=True)
        
        chromedriver_path = Path(str(Path(__file__).parent.resolve()) + '\software\chromedriver.exe')


        # configurações do Chrome para tamanho de tela, erros de certificado, driver e destino dos dowloads


        # faz o request do site
        link_inicial = "http://busca.tjsc.jus.br/dje-consulta/rest/diario/caderno?edicao=%s&cdCaderno=%s" # URL utilizada para baixar os cadernos.
        
        if int(ed) > 2413:
            cadernos = ["1","2","3"]
            quantidade = 3
        else:
            cadernos = ["5"]
            quantidade  = 1

        downloads_done(path_final, quantidade, ed, cadernos, link_inicial)

   
######################################       ***     ###################################################


if __name__ == "__main__":
    warnings.simplefilter('ignore', InsecureRequestWarning) # Retira a exibição dos erros de SSL.
    main()
