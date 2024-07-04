import io
import os
# Constantes
SIZEOF_HEADER=4
entrada = open('dados.dat', 'rb')


def leia_reg(entrada):
    if entrada.tell() < SIZEOF_HEADER:
        entrada.seek(4)             # Coloca o ponteiro no primeiro registro, pulando o header.
    offset = entrada.read(2)        # Leitura do byte offset
    offset = int.from_bytes(offset)
    if offset > 0:
        buffer = entrada.read(offset)
        buffer = buffer.decode()
        return buffer
    else:
        return ''
    
    
def busca_chave(entrada, chave: str):
    achou = False
    registro = leia_reg(entrada)
    while registro != '' and not achou:
        identificador = registro.split(sep='|')[0]
        if identificador == chave:
            achou = True
        else:
            registro = leia_reg(entrada)
    if achou == True:
        registro = registro.split(sep='|')
        buffer = ''
        for campo in registro:
            if campo != '':
                buffer = buffer + campo + '|'
        print(f'{buffer} {len(buffer)} bytes')
        return buffer       
    else:
        print('Erro! Identificador não encontrado.')

busca_chave(entrada,'9')