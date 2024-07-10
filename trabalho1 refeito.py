import io
import os
import sys
# CONSTANTES
SIZEOF_HEADER = 4
CABECA_LED_PADRAO = 4294967295

def leia_reg(entrada: io.TextIOWrapper):
    if entrada.tell() < SIZEOF_HEADER:
        entrada.seek(4, os.SEEK_SET) # Coloca o ponteiro no primeiro registro, pulando o header.
    offset = entrada.read(2) # É lido o offset (tamanho) do registro
    offset = int.from_bytes(offset)    # O tamanho do registro é transformado de binário para inteiro
    posicao_ponteiro = entrada.tell() # É guardada a posição que o ponteiro fica após ser lido o offset (marcando a chave primária do registro)
    ler_possivel_asterisco = entrada.read(1).decode() # É lido o primeiro caracter do campo após o offset do registro (chave primária)
    if ler_possivel_asterisco != '*': # Caso o caracter seja diferente de *, significa que o registro não foi removido
        entrada.seek(posicao_ponteiro, os.SEEK_SET) # Volta o ponteiro para o início do arquivo e reposiciona-o na chave primária do registro
        buffer = entrada.read(offset) # São lidos *offset* bytes do registro, ou seja, seu tamanho completo e armazenado em buffer
        buffer = buffer.decode() # O conteúdo de buffer é transformado de binário para string 
        return buffer, posicao_ponteiro # Devolve o registro decodificado e a posição do ponteiro antes da chave primária
    elif ler_possivel_asterisco == '*': # Caso o registro encontrado seja um registro removido
        entrada.seek(posicao_ponteiro) # O ponteiro é posicionado antes do caracter *
        entrada.read(offset) # São lidos *offset* (tamanho do registro) bytes
        return ler_possivel_asterisco, posicao_ponteiro # Devolve a '*' e a posição do ponteiro após ser lido o offset do registro
    else:
        return '', posicao_ponteiro


def busca_chave(entrada: io.TextIOWrapper, chave: str):
    achou = False
    registro, posicao_ponteiro = leia_reg(entrada) # É lido o primeiro registro e são guardadas a string devolvida e a posição do ponteiro após ser lido o offset do registro
    while registro != '' and not achou:
        if registro != '*': # Se o registro encontrado não for um registro removido
            identificador = registro.split(sep='|')[0] # Divide-se o registro em seus campos e, o primeiro campo (referente a chave primária) é armazenado em identificador
            if identificador == chave:
                achou = True
            else: # Caso o identificador encontrado não seja correspondente à chave primária buscada
                registro, posicao_ponteiro = leia_reg(entrada) # É feita a leitura do próximo registro
        else: # Caso se depare com um registro removido
            registro, posicao_ponteiro = leia_reg(entrada) # É lido o próximo arquivo 
    if achou == True: # Caso encontre o registro buscado
        registro = registro.split(sep='|') # registro é dividido em uma lista de strings (que representam seus campos)
        buffer = '' 
        for campo in registro:
            if campo != '':
                buffer = buffer + campo + '|' # Recompõe-se o registro completo
        offset = len(buffer) # É medido o offset (tamanho) do registro
        return buffer, posicao_ponteiro - 2, offset # Devolve o registro completo, posição do ponteiro antes mesmo de ser lido o offset do registro e seu próprio offset
    else: # Caso não encontre o registro buscado, levante o erro na busca
        raise('Erro! Identificador não encontrado.')  


def remover_registro(entrada: io.TextIOWrapper, chave: str):
    chave_removido, offset_removido, tam_removido = busca_chave(entrada,chave)
    entrada.seek(offset_removido, os.SEEK_SET) # Posiciona o ponteiro no início do reg a ser removido (antes mesmo de seu offset)
    entrada.seek(2, os.SEEK_CUR) # Posiciona o ponteiro após o offset do registro, em seu primeiro campo (chave primária) 
    entrada.write('*'.encode()) # Sobrescreve a chave primária com '*'
    entrada.seek(os.SEEK_SET) # Posiciona o ponteiro de L/E no 0.
    offset_primeiro_led = entrada.read(4) # Lê a cabeça da led no cabeçalho do arquivo e armazena em offset_primeiro_led
    led_anterior = offset_primeiro_led
    atual_led = offset_removido.to_bytes(4)
    entrada.seek(int.from_bytes(offset_primeiro_led),os.SEEK_SET)     
    if tam_removido >= int.from_bytes(entrada.read(2)):
        entrada.seek(os.SEEK_SET)
        entrada.write(atual_led)
    while int.from_bytes(offset_primeiro_led) != CABECA_LED_PADRAO:
        entrada.seek(int.from_bytes(offset_primeiro_led), os.SEEK_SET)
        tam_primeiroLED = int.from_bytes(entrada.read(2)) # Lê o tamanho do registro que está no topo da LED
        entrada.seek(int.from_bytes(atual_led) + 3, os.SEEK_SET)
        if tam_removido > tam_primeiroLED:
            entrada.write(offset_primeiro_led)
            entrada.seek(int.from_bytes(led_anterior) + 3, os.SEEK_SET)
            entrada.write(offset_primeiro_led)
            entrada.seek(int.from_bytes(offset_primeiro_led) + 3, os.SEEK_SET)
            led_anterior = offset_primeiro_led
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
    remover_registro(entrada,'2')
    remover_registro(entrada,'1')
    
    
    
      
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



