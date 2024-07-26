﻿# lista-jogos
Trabalho da disciplina Organização e Recuperação de Dados.

Este repositório contém um exemplo de como ler e processar um arquivo de dados que armazena informações sobre jogos. O arquivo segue um formato específico com registros de tamanho variável e um cabeçalho fixo.

# Estrutura do Arquivo
O arquivo dados.dat é estruturado da seguinte forma:

Cabeçalho (4 bytes):
Contém informações meta sobre o arquivo, como o número total de registros ou outra informação relevante.
Campo de Tamanho dos Registros (2 bytes cada):

Cada registro de jogo é precedido por um campo de 2 bytes que indica o tamanho do registro.

Registro de Jogo:
Cada registro de jogo contém os seguintes campos:

IDENTIFICADOR: Chave primária do jogo.
TÍTULO: Título do jogo. 
ANO: Ano de lançamento do jogo. 
GÊNERO: Gênero do jogo. 
PRODUTORA: Nome da produtora do jogo. 
PLATAFORMA: Plataforma onde o jogo está disponível.

# Utilização do programa
Para a leitura do arquivo de operações:
*  $ python main.py -e arquivo_operacoes

Para a impressão da LED:
*  $ python main.py -p
