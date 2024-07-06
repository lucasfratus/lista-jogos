import io
import os
# Constantes
SIZEOF_HEADER=4
entrada = open('dados_copy.dat', 'rb+')


def leia_reg(entrada: io.TextIOWrapper):
    if entrada.tell() < SIZEOF_HEADER:
        entrada.seek(4)             # Coloca o ponteiro no primeiro registro, pulando o header.
    offset = entrada.read(2)        # Leitura do byte offset
    posicao_ponteiro = entrada.tell()   # Guarda a posição do ponteiro após a leitura do byteoffset
    offset = int.from_bytes(offset)  # Transforma o offset(que está em bytes) em int.
    if offset > 0:
        buffer = entrada.read(offset)
        buffer = buffer.decode()
        return buffer, posicao_ponteiro
    else:
        return '', posicao_ponteiro
    
    
def busca_chave(entrada: io.TextIOWrapper, chave: str):
    achou = False
    registro, posicao_ponteiro_Id = leia_reg(entrada)
    while registro != '' and not achou:
        identificador = registro.split(sep='|')[0]
        if identificador == chave:
            achou = True
        else:
            registro, posicao_ponteiro_Id = leia_reg(entrada)
    if achou == True:
        registro = registro.split(sep='|')
        buffer = ''
        for campo in registro:
            if campo != '':
                buffer = buffer + campo + '|'
        offset = len(buffer)
        return buffer, posicao_ponteiro_Id, offset    
    else:
        print('Erro! Identificador não encontrado.')


def verifica_cabecaLED(entrada: io.TextIOWrapper, chave: str, cabeca_led: bytes):
    ponteiro_Id = busca_chave(entrada, chave)[1]
    ponteiro_Id -= 2    # Volta dois bytes
    entrada.seek(ponteiro_Id, os.SEEK_SET)      # Posiciona o ponteiro de L/E antes do byte offset
    offset = entrada.tell()
    tam = int.from_bytes(entrada.read(2))
    entrada.seek(cabeca_led, os.SEEK_SET)
    tamanho_cabeca = entrada.read(2)
    if tam > int.from_bytes(tamanho_cabeca):
        cabeca_led = offset
    return cabeca_led


#def verifica_tamanho(registro: tuple):

cabeca = 4
cabeca = verifica_cabecaLED(entrada, '3', cabeca)
print(cabeca)