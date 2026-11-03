from core.bootstrapping import GestorCertificadoX509
from core.cadeia import gerar_cadeia, derivar_chave_mac
from core.mac import calcular_mac
from core.mensagem import MensagemADSB, PacoteTESLA


class Aeronave:
    def __init__(self, icao: str, n_intervalos: int, atraso_divulgacao: int = 2):
        self.icao = icao
        self.cadeia = gerar_cadeia(n_intervalos)
        self.intervalo_atual = 1
        self.d = atraso_divulgacao
        self.gestor_x509 = GestorCertificadoX509(icao)

    @property
    def chave_raiz(self) -> bytes:

        return self.cadeia[0]

    def gerar_pacote_bootstrapping(self, t0: float, t_int: float) -> dict:

        return self.gestor_x509.assinar_bootstrapping(
            k0=self.chave_raiz,
            t0=t0,
            t_int=t_int,
            d=self.d
        )

    def transmitir(self, mensagem: MensagemADSB) -> PacoteTESLA | None:
        if self.intervalo_atual >= len(self.cadeia):
            return None

        i = self.intervalo_atual

        k_i = self.cadeia[i]
        k_linha_i = derivar_chave_mac(k_i)

        mac = calcular_mac(mensagem.serializar(), k_linha_i)

        idx_chave_revelada = i - self.d
        if idx_chave_revelada >= 0:
            chave_revelada = self.cadeia[idx_chave_revelada]
        else:
            chave_revelada = b""
            idx_chave_revelada = -1

        pacote = PacoteTESLA(
            mensagem=mensagem,
            intervalo_i=i,
            mac=mac,
            chave_revelada=chave_revelada,
            idx_chave_revelada=idx_chave_revelada
        )

        self.intervalo_atual += 1
        return pacote