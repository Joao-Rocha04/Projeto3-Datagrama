#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import numpy as np
import random

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM8"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM8"                  # Windows(variacao de)
def temporizador(com1):
    tempo_inicial = time.time()
    while True:
        tempo_atual = time.time()
        tempo_passado = tempo_atual - tempo_inicial
        sinal = com1.rx.getIsEmpty()
        txLen = 1
        if sinal == False:
            rxBuffer, nRx = com1.getData(txLen) #u get all buffer
            break
        if tempo_passado > 5:
            print("Tempo limite excedido!!")
            com1.disable()  
            break
def constroi_head(tipo,num_pacotes,n_pacote_enviado,tamanho_payload):
    head = b""
    match tipo:
        case 1:
            head+=b"\x01"
            head+=b"\xa9"
            head+=num_pacotes.to_bytes(1,byteorder="big")
            head+=b"\x00\x00\x00\x00\x00\x00\x00"
        case 3:
            head+=b"\x03"
            head+=n_pacote_enviado.to_bytes(1,byteorder="big")
            head+=tamanho_payload.to_bytes(1,byteorder="big")
            head+=b"\x00\x00\x00\x00\x00\x00\x00"
        case 5:
            head+=b"\x05"
            head+=b"\xa9"
            head+=b"\x00\x00\x00\x00\x00\x00\x00\x00"
    return head

def pegar_payload(array_bytes):
    if len(array_bytes) >= 140:
        payload = array_bytes[0:140]
        array_bytes = array_bytes[140:]
        return payload, array_bytes
    else:
        payload = array_bytes
        array_bytes = b""
        return payload, array_bytes
    
def constroi_eop():
    return b"\xAA\xBB\xAA\xBB"

def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        com1.enable()
        ultimo_enviado = b""
        
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        # com1.enable()
        time.sleep(.2)
        com1.sendData(b'00')
        time.sleep(.1)
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        lista_imagens = ["rango.jpg","lactea.jpg",]
        for img in lista_imagens:
            tempo_inicial = time.time()
            with open('log.txt', 'a') as log:
                log.write(f"Começou o envio do arquivo {img}\n")
            acabou = False
            byteslactea = open(img, "rb").read()
            
            if len(byteslactea) % 140>0:
                num_pacotes = len(byteslactea)//140 + 1       
            else:
                num_pacotes = len(byteslactea)//140
            print(f"Numero de pacotes: {num_pacotes}")
            #envia o tipo 1
            enviar = constroi_head(1,num_pacotes,0,0)+constroi_eop()
            com1.sendData(enviar)
            print("enviei o primeiro comando")
            header,nr1 = com1.getData(10)
            tipo = header[0]
            if tipo == 2:
                print("Pode começar a enviar os pacotes")
            else:
                print("Erro! Tipo 2 não recebido")
                com1.disable()
            n_pacote = 1
            teve_problema = False
            acabou = False
            #Começa a enviar os pacotes	
            while acabou == False:
                if n_pacote == num_pacotes:
                    acabou = True
                    tempo_final = time.time()
                    print(f"Tempo total: {tempo_final - tempo_inicial}")
                    razao = len(byteslactea)/(tempo_final - tempo_inicial)
                    print(f"Taxa de transmissão: {razao} bytes/s")
                    with open('log.txt', 'a') as log:
                        log.write(f"Terminou o envio do arquivo {img}\n")
                        log.write(f"Tempo total: {tempo_final - tempo_inicial}\n")
                        log.write(f"Taxa de transmissão: {razao} bytes/s\n")
                payload, byteslactea = pegar_payload(byteslactea)
                mensagem = constroi_head(3,0,n_pacote,len(payload))+payload+constroi_eop()
                ultimo_enviado = mensagem
                com1.sendData(mensagem)
                #print(f"Enviando pacote {n_pacote}")

                tamanho = com1.rx.getBufferLen()
                tempo_inicial_time_out = time.time()
                tempo_decorrido_time_out = 0
                while tamanho == 0 and tempo_decorrido_time_out < 10:
                    tamanho = com1.rx.getBufferLen()
                    tempo_decorrido_time_out = time.time() - tempo_inicial_time_out
                    if tempo_decorrido_time_out > 10:
                        print("Tempo limite excedido!!")
                        com1.disable()
                header,nr1 = com1.getData(10)
                tipo = header[0]
                if tipo == 6:
                    #print("Erro! Tipo 6 recebido")
                    with open('log.txt', 'a') as log:
                        log.write(f"Erro! Tipo 6 recebido no pacote de numero {n_pacote}\n")
                    teve_problema = True
                eop,nr1 = com1.getData(4)
                if eop != constroi_eop():
                    #print("Erro no EOP")
                    with open('log.txt', 'a') as log:
                        log.write(f"Erro no EOP no pacote de numero {n_pacote}\n")
                    teve_problema = True
                if tipo == 4:
                    #print("Pacote recebido com sucesso")
                    n_pacote += 1
                while teve_problema == True:
                    print("Reenviando pacote")
                    com1.sendData(ultimo_enviado)
                    tamanho = com1.rx.getBufferLen()
                    tempo_inicial_time_out = time.time()
                    tempo_decorrido_time_out = 0
                    while tamanho == 0 and tempo_decorrido_time_out < 10:
                        tamanho = com1.rx.getBufferLen()
                        tempo_decorrido_time_out = time.time() - tempo_inicial_time_out
                        if tempo_decorrido_time_out > 10:
                            print("Tempo limite excedido!!")
                            com1.disable()
                    header,nr1 = com1.getData(10)
                    tipo = header[0]
                    eop,nr1 = com1.getData(4)
                    if eop != constroi_eop():
                        #print("Erro no EOP")
                        teve_problema = True
                        with open('log.txt', 'a') as log:
                            log.write(f"Erro no EOP no pacote de numero {n_pacote}\n")
                    elif tipo == 6:
                        #print("Erro! Tipo 6 recebido")
                        teve_problema = True
                        with open('log.txt', 'a') as log:
                            log.write(f"Erro! Tipo  recebido no pacote de numero {n_pacote}\n")
                    else:
                        teve_problema = False
         # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()