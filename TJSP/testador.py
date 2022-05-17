import pandas as pd
import glob
import os
import time
import numpy as np
import scipy.stats as st


def unificador():

	lista_planilhas_a_ler = glob.glob("./*.csv")

	dados_planilhas_lidas = []

	todos_dados = pd.DataFrame()

	for planilha in lista_planilhas_a_ler:
		print("Nome da planilha a ler: ", planilha)
		dados_planilhas_lidas.append(pd.read_csv(planilha, dtype="object"))
		print("Lida!")

	todos_dados = todos_dados.append(dados_planilhas_lidas, ignore_index=True, sort=False)


	todos_dados.to_csv("planilhas_agrupadas_SP.csv", index=False)

# unificador()


def amostra():

	planilha = pd.read_csv("planilhas_agrupadas_SP.csv")

	print(planilha.head())

	pastas = pd.DataFrame(planilha.groupby(["nomes_pastas"])["nomes_pastas"].count())
	pastas.columns = ["quantidade"]

	pastas = pastas.reset_index()



	selct = pastas["nomes_pastas"].to_list()


	qtdade_certas = []
	qtade_erradas = []
	datas = []


	amostras = pd.DataFrame()
	for pasta in selct:
		erradas = 0
		certas = 0
		df_filter = planilha["nomes_pastas"] == pasta
		planilha_1 = planilha[df_filter]

		#### mude a quantidade de  amostra aqui ###
		      ##############################
		amostra_pasta = planilha_1.sample(100)
	
			 ###############################	

		amostras = pd.concat([amostras,amostra_pasta])

		for pub,pst in zip(amostra_pasta["publicacao"],amostra_pasta["nomes_pastas"]):
			try:
				print(pst)
				print(pub)
				print("\n ********** \n")
			except:
				print("erro no arquivo", pst, "verifique")
			else:
				z = input("Certo? Digite 'n' para errado")
				if z == "n":
					erradas = erradas+1
				else:
					certas = certas+1
		qtdade_certas.append(certas)
		qtade_erradas.append(erradas)
		datas.append(pst)

	df_teste = pd.DataFrame({"Datas": datas,"Certas":qtdade_certas,"Erradas":qtade_erradas})


	intervalo = st.t.interval(alpha=0.95, df=len(qtade_erradas)-1, loc=np.mean(qtade_erradas), scale=st.sem(qtade_erradas)) 
	erro = (intervalo[1] - intervalo[0])/2

	qtdade_total = len(amostras["publicacao"])
	erro_amostral = (sum(qtade_erradas)*100)/qtdade_total  


	print(df_teste)
	print("o intervalo de confiança é",intervalo,"com nível de confiança de 95%")
	print()
	print("O erro amostral é", erro)
	print()
	print("o percentual de erro nessa amostra foi", erro_amostral ,"%. Foram testadas", qtdade_total,"publicações")



	amostras.to_excel("Amostra_teste.xlsx", index = False)

amostra()