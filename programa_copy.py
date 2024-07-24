# Alunos:
# Giovani Oliveira Santos RA:133166
# Lucas de Oliveira Fratus RA:134698
import io
import os
from sys import argv

# CONSTANTES
SIZEOF_HEADER = 4
CABECA_LED_PADRAO = 4294967295


def leia_reg(entrada: io.TextIOWrapper):
    '''
    Recebe o arquivo *entrada*, lê um registro e devolve uma tupla composta pelo registro decodificado
    e o byteoffset em que o mesmo se inicia (após sua marcação de tamanho). Caso chegue no fim do
    arquivo, devolve uma string vazia e o byteoffset da última posição do arquivo.
    '''
    if entrada.tell() < SIZEOF_HEADER:
        entrada.seek(4, os.SEEK_SET) # Coloca o ponteiro no primeiro registro, pulando o header.
    offset = entrada.read(2)
    offset = int.from_bytes(offset)    # O tamanho do registro é transformado de binário para inteiro
    posicao_ponteiro = entrada.tell() # É guardada a posição que o ponteiro fica após ser lido o offset (marcando a chave primária do registro)
    ler_possivel_asterisco = entrada.read(1).decode() # É lido o primeiro caractere do campo após o tamanho do registro (chave primária)
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
    '''
    Recebe um arquivo de *entrada* e uma *chave* de registro a ser buscada (seu ID).
    '''
    entrada.seek(os.SEEK_SET) # Coloca, por garantia, o ponteiro no começo do arquivo
    achou = False
    registro, posicao_ponteiro = leia_reg(entrada) # É lido o primeiro registro e são guardadas a string devolvida e a posição do ponteiro após ser lido o offset do registro
    '''
    Inicia-se um enquanto, para que seja atualizada a variável *achou*
    '''
    while registro != '' and not achou:
        if registro != '*': # Se o registro encontrado não for um registro removido
            identificador = registro.split(sep='|')[0] # Divide-se o registro em seus campos e, o primeiro campo (referente a chave primária) é armazenado em identificador
            if identificador == chave:
                achou = True
            else: # Caso o identificador encontrado não seja correspondente à chave primária buscada
                registro, posicao_ponteiro = leia_reg(entrada) # É feita a leitura do próximo registro
        else: # Caso se depare com um registro removido
            registro, posicao_ponteiro = leia_reg(entrada) # É lido o próximo registro
    '''
    Após a busca em arquivo, existem duas possibilidades: chave encontrada (achou é atualizado para True) ou
    a busca atingiu EOF. Caso aconteça a segunda possibilidade, acontece um raise de um erro.
    '''
    if achou == True: # Caso encontre o registro buscado
        registro = registro.split(sep='|') # registro é dividido em uma lista de strings (que representam seus campos)
        buffer = ''
        for campo in registro:
            if campo != '':
                buffer = buffer + campo + '|' # Recompõe-se o registro completo
        offset = len(buffer) # É medido o offset (tamanho) do registro
        entrada.seek(os.SEEK_SET)
        return buffer, posicao_ponteiro - 2, offset # Devolve o registro completo, byteoffset do registro e seu próprio offset (tamanho)
    else: # Caso não encontre o registro buscado, levante o erro na busca
        raise('Chave não encontrada.')


def remover_registro(entrada: io.TextIOWrapper, chave: str):
    '''
    Recebe o arquivo *entrada* e a *chave* do registro pertencente a ele que se deseja remover.
    Os registros removidos são logicamente marcados pelo caractere '*', que ocupa a terceira posição
    no registro, logo após seu tamanho.
    Mantém os registros removidos organizados em uma "Lista de Espaços Disponíveis" (LED) que
    usa a estratégia Worst-Fit, visando retardar necessidade de compactação do arquivo.
    '''
    entrada.seek(os.SEEK_SET)
    chave_removido, byteOffset_removido, tam_removido = busca_chave(entrada,chave) # Faz a busca pela chave do registro que deseja-se remover, guarda-se seu byteoffset e tamanho.
    entrada.seek(byteOffset_removido, os.SEEK_SET) # Posiciona o ponteiro no byteoffset do reg a ser removido
    entrada.seek(2, os.SEEK_CUR) # Posiciona o ponteiro após o offset do registro, em seu primeiro campo (chave primária)
    entrada.write('*'.encode()) # Sobrescreve a chave primária com '*'
    entrada.seek(os.SEEK_SET)
    headLed = int.from_bytes(entrada.read(4)) # Lê a cabeça da LED no cabeçalho do arquivo e armazena em headLed
    if headLed == CABECA_LED_PADRAO:
        entrada.seek(os.SEEK_SET)
        entrada.write(byteOffset_removido.to_bytes(4)) # É escrito na cabeça da LED o byte offset do último removido
        entrada.seek(byteOffset_removido+3, os.SEEK_SET) # Posiciona-se o ponteiro mais uma vez em 0 e o avança para a posição após o * do último registro removido
        entrada.write(headLed.to_bytes(4)) # Escreve a última cabeça da LED (byte offset do removido anterior) no último registro removido
    else: # headLed != CABECA_LED_PADRAO:
        entrada.seek(headLed, os.SEEK_SET)
        tam_headLed = int.from_bytes(entrada.read(2))
        if tam_headLed <= tam_removido:
            entrada.seek(os.SEEK_SET)
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
    return byteOffset_removido, tam_removido

def inserir_registro(entrada: io.TextIOWrapper, registro: str):
    '''
    Recebe um arquivo de *entrada* e um *registro* a ser inserido nesse arquivo.
    Analisa o tamanho do espaço disponível que ocupa a cabeça da LED e, caso o registro
    a ser inserido tenha tamanho menor ou igual ao da cabeça, é inserido no byteoffset
    apontado pela cabeça da LED. Se o tamanho do inserido for menor que a cabeça da LED,
    é calculado o tamanho da sobra do espaço e, caso a sobra seja maior que 10 bytes,
    a sobra é reinserida na LED
    Se o registro inserido for maior que o espaço da cabeça da LED, o registro é inserido
    ao final do arquivo.
    A LED utiliza a estratégia de organização Worst-Fit, visando retardar a necessidade de
    compactação do arquivo.
    '''
    entrada.seek(os.SEEK_SET)
    headLed = int.from_bytes(entrada.read(4))
    entrada.seek(headLed, os.SEEK_SET) # Leva o ponteiro até o byteoffset do espaço disponível que ocupa a cabeça da LED
    tam_headLed = int.from_bytes(entrada.read(2)) # É lido e armazenado o tamanho da cabeça da LED
    reg = registro.encode() # Passa o *registro* a ser inserido para sua forma em bytes
    tam_reg = len(registro)
    tam_sobra = 0
    if tam_headLed >= tam_reg: # Se o tamanho da cabeça for maior ou igual ao tamanho do registro a ser inserido, faça:
        entrada.seek(headLed+3, os.SEEK_SET) # Posicione o ponteiro após o '*' do registro removido que ocupa a cabeça da LED
        headLed_ant = int.from_bytes(entrada.read(4)) # Leia o byteoffset da cabeça da LED anterior (espaço disponível que seja menor que o que ocupa a cabeça atualmente)
        novoOfsset_removido = (headLed + tam_reg + 2).to_bytes(4) # Calcula o byteoffset que a sobra ficará após a inserção do novo registro
        entrada.seek(headLed+2, os.SEEK_SET) # Posiciona o ponteiro no espaço disponível da cabeça da LED, após seu tamanho
        resto_removido = entrada.read(5) # Armazena 5 bytes do espaço disponível da cabeça da LED (após seu tamanho), para uso posterior(incluindo o '*')
        posicao_inserida = headLed # Guarda o byteoffset de onde é inserido o novo registro
        entrada.seek(headLed, os.SEEK_SET) # Posiciona o ponteiro no byteoffset do espaço disponível na cabeça da LED
        entrada.write(tam_reg.to_bytes(2))
        entrada.write(reg) # Escreve o registro inserido
        tam_sobra = tam_headLed - tam_reg - 2 # Calcula o tamanho que sobra após a inserção do novo registro
        entrada.seek(headLed_ant, os.SEEK_SET) # Posiciona o ponteiro no espaço disponível menor que a cabeça da LED considerada
        tam_headLed_ant = int.from_bytes(entrada.read(2)) # Mede-se o tamanho do espaço disponível menor que a cabeça da LED considerada
        if tam_sobra > tam_headLed_ant: # Caso o tamanho que sobra da inserção continue sendo maior que o espaço disponível menor que a cabeça da LED considerada
            entrada.seek(os.SEEK_SET) # Posiciona o ponteiro no cabeçalho
            entrada.write(novoOfsset_removido) # A nova cabeça da LED deverá ser o espaço que sobrou da inserção, portando, o novo byteoffset da sobra é escrito no cabeçalho
            entrada.seek(int.from_bytes(novoOfsset_removido), os.SEEK_SET) # Posiciona o ponteiro no novo byteoffset da sobra disponível
            entrada.write(tam_sobra.to_bytes(2)) # Escreve o novo tamanho da sobra disponível
            entrada.write(resto_removido) # Escreve o '*' (para indicar ser um espaço disponível) e o byteoffset do próximo espaço disponível na LED
        elif tam_sobra > 10: # Se o tamanho da sobra for somente maior que 10:
            entrada.seek(os.SEEK_SET) # Posiciona o ponteiro no início do arquivo
            entrada.write(headLed_ant.to_bytes(4)) # Escreve no cabeçalho o byteoffset da nova cabeça da LED (primeiro espaço disponível menor que o utilizado na inserção do registro)
            entrada.seek(int.from_bytes(novoOfsset_removido), os.SEEK_SET) # Posiciona o ponteiro no novo byteoffset da sobra
            entrada.write(tam_sobra.to_bytes(2)) # Escreve o tamanho da sobra após inserção
            entrada.write('*'.encode()) # Escreve o '*' (indicador de remoção)
            headLed = headLed_ant # Atualiza a cabeça da LED para o byteoffset da nova cabeça
            tam_headLed = tam_headLed_ant # Atualiza o tamanho da nova cabeça da LED
            entrada.seek(headLed +3, os.SEEK_SET) # Posiciona o ponteiro na nova cabeça da LED, após o '*'
            headLed_ant = int.from_bytes(entrada.read(4)) # É lido o byteoffset do próximo espaço disponível (menor que a cabeça atual)
            entrada.seek(headLed_ant, os.SEEK_SET) # Posiciona o ponteiro no próximo espaço disponível menor que a cabeça atual
            tam_headLed_ant = int.from_bytes(entrada.read(2)) # É lido o tamanho do próximo espaço menor que a cabeça
            cabeca = headLed # Armazena o byteoffset da cabeça atual em outra variável
            while tam_headLed > tam_sobra: # Enquanto o tamanho da cabeça atual for maior que o tamanho da sobra:
                cabeca = headLed # Armazena o byteoffset da cabeça atual em outra variável
                headLed = headLed_ant # Cabeça atual passa a ser o próximo espaço disponível
                entrada.seek(headLed, os.SEEK_SET) # Posiciona o ponteiro no byteoffset da nova cabeça considerada
                tam_headLed = int.from_bytes(entrada.read(2))
                entrada.seek(1, os.SEEK_CUR) # Posiciona o ponteiro após o '*'
                headLed_ant = int.from_bytes(entrada.read(4)) # Armazena o byteoffset do próximo espaço disponível menor que o da cabeça atualmente considerada
            entrada.seek(int.from_bytes(novoOfsset_removido)+3, os.SEEK_SET) # Posiciona o ponteiro após o '*' do espaço restante da inserção
            entrada.write(headLed.to_bytes(4)) # Faz com que o espaço restante da inserção aponte para o próximo espaço disponível na LED que seja menor que ele
            entrada.seek(cabeca + 3, os.SEEK_SET) # Posiciona o ponteiro no primeiro espaço da LED maior que o espaço restante da inserção do registro
            entrada.write(novoOfsset_removido) # Faz com que o primeiro espaço da LED maior que o espaço restante da inserção do registro aponte para o espaço restante
            entrada.seek(os.SEEK_SET)
        else: # tam_sobra < 10:
            entrada.seek(headLed, os.SEEK_SET) # Posiciona o ponteiro no byteoffset do espaço disponível na cabeça da LED
            entrada.write((tam_reg + tam_sobra).to_bytes(2)) # O tamanho do inserido leva em conta o tamanho da sobra junto dele, tornando a sobra fragmentação interna
            entrada.seek(os.SEEK_SET) # Posiciona de volta o ponteiro no cabeçalho
            entrada.write(headLed_ant.to_bytes(4)) # Escreve a nova cabeça da LED (que era apontada pela cabeça inicial)
    else: # O tamanho do novo registro não cabe na cabeça da LED, portanto deve ser inserido no final do arquivo
        posicao_inserida = 'fim do arquivo'
        entrada.seek(0, os.SEEK_END)
        entrada.write((len(registro)).to_bytes(2)) # Escreve o tamanho do registro a ser inserido
        registro_bytes = registro.encode() # Transforma o *registro* em bytes
        entrada.write(registro_bytes) # Escreve o *registro* em bytes
    entrada.seek(os.SEEK_SET)
    return posicao_inserida, tam_headLed, tam_sobra


def imprimir_led(entrada: io.TextIOWrapper):
    '''
    Imprime na tela todos os espaços disponiveis que pertencem a LED(Lista de espaços disponíveis).
    A impressão da LED será acessada por meio de linha de comando, da seguinte forma:
    $ python programa.py -p
    sendo a flag -p a que sinaliza o modo de impressão.
    Apresentará na tela os offsets dos espaços disponiveis, iniciando pela cabeça da LED, além de mostrar o número de espaços disponíveis.
    '''
    entrada.seek(os.SEEK_SET)
    cabeca_led = int.from_bytes(entrada.read(4)) # Lê e armazena a cabeça da led em *cabeca_led*
    buffer = 'LED'
    contagem_espacos = 0 # Inicia a contagem de espaços disponíveis em zero
    entrada.seek(cabeca_led, os.SEEK_SET) # Posiciona o ponteiro no registro removido com espaço equivalente à cabeça da LED
    while cabeca_led != CABECA_LED_PADRAO:
        contagem_espacos += 1 # Sempre que encontrar um ponteiro diferente do -1 (fim da LED), adiciona 1 ao número de espaços disponíveis
        entrada.seek(cabeca_led, os.SEEK_SET) # Posiciona o ponteiro no registro removido com espaço equivalente à cabeça da LED
        offset = entrada.tell() # Armazena em *offset* o byteoffset do espaço disponível
        tamanho = int.from_bytes(entrada.read(2)) # Armazena em *tamanho* o tamanho do espaço disponível
        buffer += (f' -> [offset: {offset}, tam: {tamanho}]') # Atualiza a string buffer com o espaço disponível encontrado que é menor que o anterior
        entrada.seek(1, os.SEEK_CUR)
        cabeca_led = int.from_bytes(entrada.read(4)) # Lê o próximo espaço removido menor que o atual e o atualiza para continuar a busca por espaços disponíveis
    buffer += ' -> [offset = -1]' # Após o fim do while, adiciona o último offset possível que a cabeça da LED assuma (-1)
    print(buffer + '\nTotal:',contagem_espacos,'espacos disponiveis' )


def ler_arq_operacao(entrada: io.TextIOWrapper, arquivo_operacoes: io.TextIOWrapper):
    '''
    Será responsável por ler o arquivo de operações.(O arquivo de operações sempre deverá ter o )
    O arquivo de operações possui uma operação por linha, identificada com um dos seguintes identificadores:
    b = busca,
    i = inserção,
    r = remoção,
    e seguidas pelos seus argumentos.
    Além disso, imprimirá na tela o resultado das operações.
    '''
    entrada.seek(os.SEEK_SET)
    arq_operacao = open(arquivo_operacoes,'r')
    linha = arq_operacao.readline() # Lê a primeira linha do arquivo de operação
    while linha != '':
        operacao = linha[0] # Lê o primeiro caractere da linha(é resposável por indicar qual operação será feita)
        if operacao == 'b':
            '''
            Ambos "Ifs" abaixo são responsáveis por, no momento do split, realizarem ele da forma correta, já que na ultima linha do arquivo de operações
            não existe o "\n".
            '''
            if linha[-1] != '\n':
                chave_buscada = linha[2:]
            else:
                chave_buscada = linha[2:-1]
            try:
                reg_buscado, loc_ponteiro, tamanho = busca_chave(entrada, chave_buscada)
                print(f'Busca pelo registro de chave "{chave_buscada}" \n{reg_buscado} ({tamanho} bytes)\n')
            except:
                print('Registro não encontrado\n')
        if operacao == 'i':
            if linha[-1] == '|':
                chave_insercao = linha[2:]
            else:
                chave_insercao = linha[2:-1]
            chave_dividida =  chave_insercao.split('|')
            id = chave_dividida[0]
            tamanho = len(chave_insercao)
            local, tam_headLed, tam_sobra  = inserir_registro(entrada, chave_insercao)
            if local == 'fim do arquivo':
                print(f'Inserção do registro de chave "{id}" ({tamanho} bytes)\nLocal: {local}\n')
            elif tam_sobra < 10:
                print(f'Inserção do registro de chave "{id}" ({tamanho} bytes)\nTamanho do espaço reutilizado: {tam_headLed} bytes\nLocal: offset = {local} bytes ({hex(local)})\n')
            else:
                print(f'Inserção do registro de chave "{id}" ({tamanho} bytes)\nTamanho do espaço reutilizado: {tamanho + tam_sobra + 2} bytes (Sobra de: {tam_sobra} bytes)\nLocal: offset = {local} bytes ({hex(local)})\n')
        if operacao == 'r':
            try:
                if linha[-1] == '|':
                    chave_remocao = str(linha[2:])
                else:
                    chave_remocao = str(linha[2:-1])
                local_removido, tamanho = remover_registro(entrada, chave_remocao)
                print(f'Remoção do registro de chave "{chave_remocao}" \nRegistro removido!({tamanho} bytes)\nLocal: offset = {local_removido} bytes ({hex(local_removido)})\n')
            except:
                print(f'Remoção do registro de chave "{chave_remocao}" \nErro: registro não encontrado!\n')
        linha = arq_operacao.readline()
        entrada.seek(os.SEEK_SET)
    arq_operacao.close()


def main() -> None:
    try:
        with open('dados.dat', 'rb+') as entrada:
            if len(argv) == 3:
                ler_arq_operacao(entrada, argv[2])
            elif len(argv) == 2:
                if argv[1] == '-p':
                    imprimir_led(entrada)
            else:
                raise TypeError('Numero incorreto de argumentos!')
    except:
        raise FileNotFoundError('Não foi possível encontrar o arquivo "dados.dat"')


if __name__ == '__main__':
    main()

