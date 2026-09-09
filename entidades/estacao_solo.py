from core.cadeia import verificar_chave
from core.mac import verificar_mac

class EstacaoSolo:
    def __init__(self, chave_raiz: bytes):
        self.ultima_chave_confirmada = chave_raiz
        self.buffer_mensagens = {}  # intervalo -> (mensagem, mac)
        self.autenticados = []
        self.rejeitados = []

    def receber(self, pacote: dict | None) -> str:
        if pacote is None:
            return "PERDIDO"

        intervalo = pacote["intervalo"]
        chave_revelada = pacote["chave_revelada"]  #  K(i-1)
        mensagem = pacote["mensagem"]
        mac = pacote["mac"]  # calculado com K(i), ainda secreta

        # guarda a mensagem atual no buffer
        # só é verificada quando K(i) for revelada no proximo pacote
        self.buffer_mensagens[intervalo] = (mensagem, mac)

        #  verifica se K(i-1) revelada pertence à cadeia
        if chave_revelada != self.ultima_chave_confirmada:
            if not verificar_chave(chave_revelada, self.ultima_chave_confirmada):
                return "REJEITADO — chave inválida"

            self.ultima_chave_confirmada = chave_revelada

        # quando K(i-1) for confirmada, verifica a mensagem do intervalo ANTERIOR que estava no buffer
        intervalo_a_verificar = intervalo - 1 # autenticação atrasada

        if intervalo_a_verificar in self.buffer_mensagens: # procura a mensagem no buffer
            msg_anterior, mac_anterior = self.buffer_mensagens.pop(intervalo_a_verificar)

            if verificar_mac(msg_anterior.serializar(), chave_revelada, mac_anterior):
                self.autenticados.append({
                    "mensagem": msg_anterior,
                    "intervalo": intervalo_a_verificar
                })
                return "AUTENTICADO (intervalo anterior verificado)"
            else:
                self.rejeitados.append({
                    "mensagem": msg_anterior,
                    "intervalo": intervalo_a_verificar
                })
                return "REJEITADO — MAC inválido"

        return "RECEBIDO — aguardando verificação"