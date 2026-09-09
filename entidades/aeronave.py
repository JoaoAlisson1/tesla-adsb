from core.cadeia import gerar_cadeia
from core.mac import calcular_mac
from core.mensagem import MensagemADSB

class Aeronave:
    def __init__(self, icao: str, n_intervalos: int):
        self.icao = icao # guarda o identificador da aeronave dentro do objeto.
        self.cadeia = gerar_cadeia(n_intervalos)
        self.intervalo_atual = 1  # começa em 1, K0 já foi distribuída

    @property
    def chave_raiz(self) -> bytes:

        return self.cadeia[0]

    def transmitir(self, mensagem: MensagemADSB) -> dict | None:

        if self.intervalo_atual >= len(self.cadeia):
            return None

        chave_atual = self.cadeia[self.intervalo_atual]
        chave_revelada = self.cadeia[self.intervalo_atual - 1]
        mac = calcular_mac(mensagem.serializar(), chave_atual)

        pacote = {
            "mensagem": mensagem,
            "mac": mac,
            "chave_revelada": chave_revelada,
            "intervalo": self.intervalo_atual
        }

        self.intervalo_atual += 1
        return pacote