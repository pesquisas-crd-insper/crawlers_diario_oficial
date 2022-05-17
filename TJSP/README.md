### TJSP - Metodologia

#### 1. Coleta

Este sistema coleta os cadernos 11, 12, 13, 15, 18 do diário de justiça.

Para dar inicio ao processo é necessário inserir a data de início e de final.

##### Importante:

O formato da data a ser inserida é MÊS-DIA-ANO

Recomedamos selecionar o período de um ano por vez.


#### 2. Parser

O Parser de SP leva em consideração 7 padrões diferentes encontrados nas publicações.

"\n\d{1,3}\. Processo \d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"
"\nProcesso \d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"
"\nNº \d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"
"\nProcesso: \d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"
"\n\d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}; Processo"
"\nN° \d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"
"\nPROCESSO\s\n:\d{2,7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"


O cortador encontra os números nos padrões e depois encontra os caracteres iniciais de cada um desses números, utilizando 
esse número do caracter inicial como critério do corte (ele tem mecanismos para não ser enganado por números repetidos na mesma página).
O cortador também identifica e agrupa publicações que excedem mais de uma página.

Como o critério de corte é a numeração CNJ, algumas publicações podem vir com alguns cabeçalhos de seções do PDF.

ex:

JUÍZO DE DIREITO DA 4ª VARA CÍVEL
JUIZ(A) DE DIREITO ARTHUR DE PAULA GONÇALVES
ESCRIVÃ(O) JUDICIAL ANTONIO JOSE CRUZ DE SOUSA
EDITAL DE INTIMAÇÃO DE ADVOGADOS
RELAÇÃO Nº 0117/2013

Mas como são trechos curtos, acreditamos que eles tem pouco impacto no resultado.



#### 3. Teste

No teste foi escolhido aleatoriamente 1 dia por ano. Foram testados todos os anos entre 2012 e 2021.
De cada dia foram processados os 5 diários e escolhidas aleatoriamente 100 publicações.
Logo, nesse teste foram avaliadas 1000 publicações e a margem de erro foi 0%.

A planilha e o código do teste estão disponíveis na pasta.

A tabela abaixo mostra os resultados de cada dia.


       Datas  Certas  Erradas
0  04-09-2019     100        0
1  05-05-2020     100        0
2  05-06-2012     100        0
3  07-01-2016     100        0
4  07-10-2015     100        0
5  09-05-2017     100        0
6  09-09-2021     100        0
7  10-07-2018     100        0
8  11-07-2014     100        0
9  29-10-2013     100        0






