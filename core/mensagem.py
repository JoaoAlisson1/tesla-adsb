from dataclasses import dataclass

@dataclass
class MensagemADSB:
    icao: str
    latitude: float
    longitude: float
    altitude: float
    velocidade: float
    timestamp: float  # Tempo de geração da mensagem

    def serializar(self) -> bytes:
        conteudo = (
            f"{self.icao},{self.latitude:.4f},"
            f"{self.longitude:.4f},{self.altitude:.1f},"
            f"{self.velocidade:.1f},{self.timestamp:.3f}"
        )
        return conteudo.encode("utf-8")


@dataclass
class PacoteTESLA:

    mensagem: MensagemADSB
    intervalo_i: int
    mac: bytes
    chave_revelada: bytes
    idx_chave_revelada: int