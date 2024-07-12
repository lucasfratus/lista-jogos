import io
import os
from sys import argv
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
    entrada.seek(os.SEEK_SET) # Coloca, por garantia, o ponteiro no começo do arquivo
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
        return buffer, posicao_ponteiro - 2, offset # Devolve o registro completo, byteoffset do registro e seu próprio offset (tamanho)
    else: # Caso não encontre o registro buscado, levante o erro na busca
        raise('Erro! Identificador não encontrado.')  


def remover_registro(entrada: io.TextIOWrapper, chave: str):
    entrada.seek(os.SEEK_SET) # Coloca, por garantia, o ponteiro no começo do arquivo
    chave_removido, byteOffset_removido, tam_removido = busca_chave(entrada,chave)
    entrada.seek(byteOffset_removido, os.SEEK_SET) # Posiciona o ponteiro no byteoffset do reg a ser removido
    entrada.seek(2, os.SEEK_CUR) # Posiciona o ponteiro após o offset do registro, em seu primeiro campo (chave primária) 
    entrada.write('*'.encode()) # Sobrescreve a chave primária com '*'
    entrada.seek(os.SEEK_SET) # Posiciona o ponteiro de L/E no 0.
    headLed = int.from_bytes(entrada.read(4)) # Lê a cabeça da led no cabeçalho do arquivo e armazena em headLed
    if headLed == CABECA_LED_PADRAO:
        entrada.seek(os.SEEK_SET) # Posiciona o ponteiro de volta no início do arquivo
        entrada.write(byteOffset_removido.to_bytes(4)) # É escrito na cabeça da LED o byte offset do último removido
        entrada.seek(byteOffset_removido+3, os.SEEK_SET) # Posiciona-se o ponteiro mais uma vez em 0 e o avança para a posição após o * do último registro removido
        entrada.write(headLed.to_bytes(4)) # Escreve a última cabeça da LED (byte offset do removido anterior) no último registro removido
    else: # headLed != CABECA_LED_PADRAO:
        entrada.seek(headLed, os.SEEK_SET)
        tam_headLed = int.from_bytes(entrada.read(2))
        if tam_headLed <= tam_removido:
            entrada.seek(os.SEEK_SET) # Posiciona o ponteiro de volta no início do arquivo
            entrada.write(byteOffset_removido.to_bytes(4)) # É escrito na cabeça da LED o byte offset do último removido
            entrada.seek(byteOffset_removido+3, os.SEEK_SET) # Posiciona-se o ponteiro mais uma vez em 0 e o avança para a posição após o * do último registro removido
            entrada.write(headLed.to_bytes(4)) # Escreve a última cabeça da LED (byte offset do removido anterior) no último registro removido
        else: # tam_headLed > tam_removido:
            while tam_headLed > tam_removido:
                headLed_ant = headLed # Guarda o registro que ocupava a cabeça da LED anteriormente ao atual
                entrada.seek(1, os.SEEK_CUR) # Pula o '*'
                headLed = entrada.read(4) # Lê o byteoffset do próximo removido (menor que o anterior)
                headLed = int.from_bytes(headLed) # Converte o byteoffset para inteiro
                entrada.seek(headLed, os.SEEK_SET) # Posiciona o ponteiro na posição do registro indicado pela cabeça da LED
                tam_headLed = int.from_bytes(entrada.read(2)) # Guarda o tamanho do registro indicado pela cabeça da LED
            entrada.seek(headLed_ant+3, os.SEEK_SET) # Posiciona o ponteiro após o '*' do menor registro maior que o último removido
            entrada.write(byteOffset_removido.to_bytes(4)) # Escreve no menor registro maior que o último removido o byteoffset do último removido
            entrada.seek(byteOffset_removido+3, os.SEEK_SET) # Posiciona o ponteiro após o '*' do último registro removido
            entrada.write(headLed.to_bytes(4))  # Escreve após o '*' do último registro removido o próximo espaço disponível menor que ele (se não houver, escreve -1)
    entrada.seek(os.SEEK_SET)   # Reposiciona o ponteiro no início do arquivo após a operação


def inserir_registro(entrada: io.TextIOWrapper, registro: str):
    entrada.seek(os.SEEK_SET)
    headLed = int.from_bytes(entrada.read(4)) # Lê a cabeça da led no cabeçalho do arquivo e armazena em headLed
    entrada.seek(headLed, os.SEEK_SET)
    tam_headLed = int.from_bytes(entrada.read(2))
    reg = registro.encode()
    tam_reg = len(registro) # Soma o tamanho do registro mais um espaço de dois bytes em que ficará seu offset 
    if tam_headLed >= tam_reg:
        entrada.seek(headLed+3, os.SEEK_SET)
        headLed_ant = entrada.read(4)
        novoOfsset_removido = (headLed + tam_reg + 2).to_bytes(4)
        entrada.seek(headLed+2, os.SEEK_SET)
        resto_removido = entrada.read(5)
        entrada.seek(headLed, os.SEEK_SET)
        entrada.write(tam_reg.to_bytes(2))
        entrada.write(reg)
        tam_sobra = tam_headLed - tam_reg - 2
        entrada.seek(int.from_bytes(headLed_ant), os.SEEK_SET)
        tam_headLed_ant = int.from_bytes(entrada.read(2))
        if tam_sobra > tam_headLed_ant:
            entrada.seek(os.SEEK_SET)
            entrada.write(novoOfsset_removido)
            entrada.seek(int.from_bytes(novoOfsset_removido), os.SEEK_SET)
            entrada.write(tam_sobra.to_bytes(2))
            entrada.write(resto_removido)
        elif tam_sobra > 10:
            entrada.seek(os.SEEK_SET)
            entrada.write(headLed_ant)
            entrada.seek(int.from_bytes(novoOfsset_removido), os.SEEK_SET)
            entrada.write(tam_sobra.to_bytes(2))
            entrada.write('*'.encode())
            headLed = headLed_ant
            tam_headLed = tam_headLed_ant
            entrada.seek(int.from_bytes(headLed)+3, os.SEEK_SET)
            headLed_ant = int.from_bytes(entrada.read(4))
            entrada.seek(headLed_ant, os.SEEK_SET)
            tam_headLed_ant = int.from_bytes(entrada.read(2))
            cabeca = headLed
            while tam_headLed > tam_sobra:
                cabeca = headLed
                headLed = headLed_ant
                entrada.seek(headLed, os.SEEK_SET)
                tam_headLed = int.from_bytes(entrada.read(2))
                entrada.seek(1, os.SEEK_CUR)
                headLed_ant = int.from_bytes(entrada.read(4))
            entrada.seek(int.from_bytes(novoOfsset_removido)+3, os.SEEK_SET)
            entrada.write(headLed.to_bytes(4))
            entrada.seek(cabeca+3, os.SEEK_SET)
            entrada.write(novoOfsset_removido)

        else: # tam_sobra < 10:
            entrada.seek(os.SEEK_SET)
            entrada.write(headLed_ant)
            entrada.seek(int.from_bytes(novoOfsset_removido), os.SEEK_SET)
            entrada.write(resto_removido)

    else: # O tamanho do novo registro não cabe na cabeça da LED, portanto deve ser inserido no final do arquivo
        entrada.seek(0, os.SEEK_END)
        entrada.write((len(registro)).to_bytes(2))
        registro_bytes = registro.encode()
        entrada.write(registro_bytes)
    entrada.seek(os.SEEK_SET)   # Reposiciona o ponteiro no início do arquivo após a operação

def imprimir_led(entrada: io.TextIOWrapper):
    entrada.seek(os.SEEK_SET) # Posiciona o ponteiro no início do arquivo
    cabeca_led = int.from_bytes(entrada.read(4)) # Lê e armazena a cabeça da led em *cabeca_led*
    buffer = 'LED' # Inicia o buffer que conterá a string de saída
    contagem_espacos = 0 # Inicia a contagem de espaços disponíveis em zero
    entrada.seek(cabeca_led, os.SEEK_SET) # Posiciona o ponteiro no registro removido com espaço equivalente à cabeça da LED
    while cabeca_led != CABECA_LED_PADRAO:
        contagem_espacos += 1 # Sempre que encontrar um ponteiro diferente do -1 (fim da LED), adiciona 1 ao número de espaços disponíveis
        entrada.seek(cabeca_led, os.SEEK_SET) # Posiciona o ponteiro no registro removido com espaço equivalente à cabeça da LED
        offset = entrada.tell() # Armazena em *offset* o byteoffset do espaço disponível
        tamanho = int.from_bytes(entrada.read(2)) # Armazena em *tamanho* o tamanho do espaço disponível
        buffer += (f' -> [offset: {offset}, tam: {tamanho}]') # Atualiza a string buffer com o espaço disponível encontrado que é menor que o anterior
        entrada.seek(1, os.SEEK_CUR) # Faz o "pular" o caracter '*' que indica ser um registro removido
        cabeca_led = int.from_bytes(entrada.read(4)) # Lê o próximo espaço removido menor que o atual e o atualiza para continuar a busca por espaços disponíveis
    buffer += ' -> [offset = -1]' # Após o fim do while, adiciona o último offset possível que a cabeça da LED assuma (-1) 
    print(buffer + '\nTotal:', contagem_espacos,'espacos disponiveis' )

def main() -> None:
    with open('dados copy.dat', 'rb+') as entrada:
        assert (len(argv) > 4)
        if len(argv) < 2:
            raise TypeError('Numero incorreto de argumentos!')
        elif len(argv) == 3:
            opera = input('')
            if opera[0] == 'r':
                opera = opera[2:]
                remover_registro(entrada, opera)
                print('Remoção do registro de chave ' + '"' + opera + '"')
        else: # len(argv) > 2 and len(argv) != 3, apenas resta a opção que o len(argv) = 2
            imprimir_led(entrada)

if __name__ == '__main__':
    main()

    
'''    
with open('dados copy.dat', 'rb+') as entrada:
    imprimir_led(entrada)
    #remover_registro(entrada,'1')
    imprimir_led(entrada)
    #remover_registro(entrada,'2')
    imprimir_led(entrada)
    #remover_registro(entrada,'4')
    imprimir_led(entrada)
    #remover_registro(entrada,'3')
    imprimir_led(entrada)
    inserir_registro(entrada,'450|Resident Evil 2|pqoweqopweoqwpeoqwepoqpwoeqwpoeqwpoeqowpeoqwpeiqowieqopwieqopwieoqpwiepoqwieqpowie')
    imprimir_led(entrada)
'''