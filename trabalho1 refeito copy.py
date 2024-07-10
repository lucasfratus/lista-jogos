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
        print('Erro! Identificador não encontrado.')  


def remover_registro(entrada: io.TextIOWrapper, chave: str):
    ponteiro_removido = busca_chave(entrada, chave)[1]
    print(ponteiro_removido)
    tamanho_removido = entrada.read(2)
    entrada.seek(0, os.SEEK_SET)
    offset_led = entrada.read(4)
    offset_led = int.from_bytes(offset_led)
    entrada.seek(offset_led, os.SEEK_SET)
    tamanho_chave_led = entrada.read(2)
    entrada.seek(ponteiro_removido, os.SEEK_SET)
    offset_cabecaLED = entrada.tell()
    entrada.write('*'.encode())
    if offset_led == CABECA_LED_PADRAO:
        entrada.write(offset_led.to_bytes(4))
        offset_led = offset_cabecaLED
        entrada.seek(os.SEEK_SET)
        entrada.write(offset_led.to_bytes(4))
    else:
        while offset_led != CABECA_LED_PADRAO:
            if tamanho_removido > tamanho_chave_led:
                entrada.write(offset_led.to_bytes(4))
                offset_led = ponteiro_removido
                tamanho_chave_led = tamanho_removido
            else:
                entrada.seek(offset_led.from_bytes(offset_led), os.SEEK_SET)
                tamanho_proximo = entrada.read(2)
                entrada.seek(1)
                if tamanho_removido > tamanho_proximo:
                    entrada.write(ponteiro_removido.to_bytes(4))
                else:
                    offset_led = entrada.read(4)
                    #entrada.write(offset_led.to_bytes(4))
        offset_led = offset_cabecaLED
        entrada.seek(os.SEEK_SET)
        entrada.write(offset_led.to_bytes(4))  

with open('dados copy.dat', 'rb+') as entrada:
    #remover_registro(entrada,'1')
    busca_chave(entrada, '2')
