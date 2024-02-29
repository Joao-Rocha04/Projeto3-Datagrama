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
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM8"                  # Windows(variacao de)

comandos = {
    1: b"\x00\x00\x00\x00\n",
    2: b"\x00\x00\xFF\x00\n",
    3: b"\xFF\x00\x00\n",
    4: b"\x00\xFF\x00\n",
    5: b"\x00\x00\xFF\n",
    6: b"\x00\xFF\n",
    7: b"\xFF\x00\n",
    8: b"\x00\n",
    9: b"\xFF\n"
}
def contador_tempo():
    tempo_inicial = time.time()  
def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        com1.enable()
        
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        # com1.enable()
        time.sleep(.2)
        com1.sendData(b'00')
        time.sleep(.1)
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        
        
                  
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são um array bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.
        n = random.randint(10,30)
          #time.sleep(2)
        mandar = b''
        for i in range(n):
            x = random.randint(1,9)
            #if i==0:
            #    com1.sendData(comandos[10])
            #if i == n-1:
                #com1.sendData(comandos[10])
            mandar += comandos[x]
         #   print("estou enviando o comando {}".format(x))
        #print(len(mandar))
        #print((len(mandar)).to_bytes(1,byteorder='big'))
        com1.sendData(np.asarray(len(mandar).to_bytes(2,byteorder='big')))  #as array apenas como boa pratica para casos de ter uma outra forma de dados
        time.sleep(1)
        com1.sendData(mandar)
        print(f"enviei {n} comandos")

        #print("meu array de bytes tem tamanho {}" .format(len(txBuffer)))
        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.
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
        if sinal==False:   
            valor = int.from_bytes(rxBuffer, byteorder='big')
            print(f"Valor recebido: {valor}\nValor esperado: {n}")
            if valor==n:
                print("SUCESSO")
            else:
                print("Erro ao receber comando") 

        #faça aqui uma conferência do tamanho do seu rxBuffer, ou seja, quantos bytes foram recebidos.
          
        #finalmente vamos transmitir os todos. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #tente entender como o método send funciona!
        #Cuidado! Apenas trasmita arrays de bytes!
          
        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # O método não deve estar fincionando quando usado como abaixo. deve estar retornando zero. Tente entender como esse método funciona e faça-o funcionar.
        
        
        #txSize = com1.tx.getStatus()
        #print('enviou = {}' .format(txSize))
        
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
      
        #acesso aos bytes recebidos
        

            
    
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