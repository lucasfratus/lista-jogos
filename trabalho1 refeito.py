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
        return buffer, posicao_ponteiro - 2, offset
    else:
        raise('Erro! Identificador não encontrado.')  


def remover_registro(entrada: io.TextIOWrapper, chave: str):
    chave_removido, offset_removido, tam_removido = busca_chave(entrada,chave)
    entrada.seek(offset_removido, os.SEEK_SET) # Posiciona o ponteiro no byte offset do reg removido.
    entrada.seek(2, os.SEEK_CUR)
    entrada.write('*'.encode())
    entrada.seek(os.SEEK_SET) # Posiciona o ponteiro de L/E no 0.
    offset_primeiro_led = entrada.read(4) # Lê a cabeça da led
    led_anterior = offset_primeiro_led
    atual_led = offset_removido.to_bytes(4)
    entrada.seek(int.from_bytes(offset_primeiro_led),os.SEEK_SET)     
    if tam_removido >= int.from_bytes(entrada.read(2)):
        entrada.seek(os.SEEK_SET)
        entrada.write(atual_led)
        entrada.seek(offset_removido + 3, os.SEEK_SET)
        entrada.write(offset_primeiro_led)
    while int.from_bytes(offset_primeiro_led) != CABECA_LED_PADRAO:
        entrada.seek(int.from_bytes(offset_primeiro_led), os.SEEK_SET)
        tam_primeiroLED = int.from_bytes(entrada.read(2)) # Lê o tamanho do registro que está no topo da LED
        entrada.seek(int.from_bytes(atual_led) + 3, os.SEEK_SET)
        if tam_removido >= tam_primeiroLED:
            entrada.write(offset_primeiro_led)
            entrada.seek(int.from_bytes(led_anterior), os.SEEK_SET)
            entrada.seek(int.from_bytes(offset_primeiro_led), os.SEEK_SET)
            offset_primeiro_led = offset_removido.to_bytes(4)
        else:
            entrada.seek(int.from_bytes(offset_primeiro_led)+3, os.SEEK_SET)
            led_anterior = offset_primeiro_led           
            offset_primeiro_led = entrada.read(4)
            if offset_primeiro_led == CABECA_LED_PADRAO.to_bytes(4):
                entrada.seek(int.from_bytes(led_anterior)+3, os.SEEK_SET)
                entrada.write(offset_removido.to_bytes(4))

    #print(int.from_bytes(atual_led))
    #print(int.from_bytes(offset_primeiro_led))
    entrada.seek(int.from_bytes(atual_led) + 3, os.SEEK_SET)
    entrada.write(offset_primeiro_led)
    entrada.seek(os.SEEK_SET)

    
    
    
with open('dados copy.dat', 'rb+') as entrada:
    remover_registro(entrada,'1')
    #remover_registro(entrada,'3')
    
    
    
      
    '''chave_removida, ponteiro_removido, tamanho_removido = busca_chave(entrada,chave)
    entrada.seek(os.SEEK_SET)
    offset_led = entrada.read(4)
    entrada.seek(ponteiro_removido, os.SEEK_SET)
    entrada.write('*'.encode())
    ponteiro_pre_offset = ponteiro_removido - 2
    entrada.seek(os.SEEK_SET)
    if int.from_bytes(entrada.read(4)) == CABECA_LED_PADRAO:
        entrada.seek(ponteiro_removido + 1, os.SEEK_SET)
        entrada.write(CABECA_LED_PADRAO.to_bytes(4))
        offset_led = ponteiro_pre_offset
        entrada.seek(os.SEEK_SET)
        entrada.write(offset_led.to_bytes(4))
        entrada.seek(os.SEEK_SET)
    else:
        while int.from_bytes(offset_led) != CABECA_LED_PADRAO:
            entrada.seek(int.from_bytes(offset_led), os.SEEK_SET)
            tamanho_atual_led = int.from_bytes(entrada.read(2))
            if tamanho_atual_led > tamanho_removido:
                entrada.seek(1)
                offset_led = entrada.read(4)
            else:
                offset_proximo = offset_led
                offset_led = (ponteiro_pre_offset).to_bytes(4)
                entrada.seek((ponteiro_pre_offset) + 3, os.SEEK_SET)
                entrada.write(offset_proximo)
                offset_led = offset_proximo
                print(int.from_bytes(offset_proximo))
    entrada.seek(os.SEEK_SET)'''



