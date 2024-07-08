import io
import os

# CONSTANTES
SIZEOF_HEADER = 4
CABECA_LED_PADRAO = 4294967295

def leia_reg(entrada: io.TextIOWrapper):
    if entrada.tell() < SIZEOF_HEADER:
        entrada.seek(4, os.SEEK_SET) # Coloca o ponteiro no primeiro registro, pulando o header.
    offset = entrada.read(2)
    offset = int.from_bytes(offset)    
    posicao_ponteiro = entrada.tell()
    print(posicao_ponteiro)
    ler_possivel_asterisco = entrada.read(1).decode()
    if ler_possivel_asterisco != '*':
        entrada.seek(posicao_ponteiro, os.SEEK_SET)
        buffer = entrada.read(offset)
        buffer = buffer.decode()
        return buffer, posicao_ponteiro
    elif ler_possivel_asterisco == '*':
        entrada.seek(posicao_ponteiro)
        entrada.read(offset)
        return ler_possivel_asterisco, posicao_ponteiro
    else:
        return '', posicao_ponteiro


def busca_chave(entrada: io.TextIOWrapper, chave: str):
    achou = False
    registro, posicao_ponteiro = leia_reg(entrada)
    while registro != '' and not achou:
        if registro != '*':
            identificador = registro.split(sep='|')[0]
            if identificador == chave:
                achou = True
            else:
                registro, posicao_ponteiro = leia_reg(entrada)
        else:
            registro, posicao_ponteiro = leia_reg(entrada)
    if achou == True:
        registro = registro.split(sep='|')
        buffer = ''
        for campo in registro:
            if campo != '':
                buffer = buffer + campo + '|'
        offset = len(buffer)
        return buffer, posicao_ponteiro, offset
    else:
        raise('Erro! Identificador não encontrado.')  


def remover_registro(entrada: io.TextIOWrapper, chave: str):
    chave_removida, ponteiro_removido, offset_removido = busca_chave(entrada,chave)
    print(ponteiro_removido)
    entrada.seek(os.SEEK_SET)
    offset_led = entrada.read(4)
    #if int.from_bytes(offset_led) != CABECA_LED_PADRAO:
        #tamanho_led =
    entrada.seek(ponteiro_removido, os.SEEK_SET)
    entrada.write('*'.encode())
    entrada.write(offset_led)    
    entrada.seek(os.SEEK_SET)


with open('dados_copy.dat', 'rb+') as entrada:
    remover_registro(entrada,'7')
    remover_registro(entrada,'6')
