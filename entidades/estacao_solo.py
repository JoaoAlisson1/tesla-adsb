import time
from core.cadeia import verificar_chave, derivar_chave_mac
from core.mac import verificar_mac
from core.mensagem import PacoteTESLA


class EstacaoSolo:
    def __init__(self, chave_raiz: bytes, duracao_intervalo: float = 1.0,
                 atraso_divulgacao: int = 2, max_drift_d_t: float = 0.1,
                 t_zero: float = None):

        self.ultima_chave_confirmada = chave_raiz
        self.idx_ultima_chave = 0

        self.t_int = duracao_intervalo
        self.d = atraso_divulgacao
        self.d_t = max_drift_d_t
        self.t_0 = t_zero if t_zero is not None else time.time()

        self.buffer_mensagens = {}
        self.autenticados = []
        self.rejeitados = []
        self.historico_eventos = []

    def registrar_evento(self, pacote: PacoteTESLA | None, tempo_recepcao: float, status: str,
                         motivo_rejeicao: str = "N/A"):

        if pacote is None or pacote.mensagem is None:

            self.historico_eventos.append({
                "intervalo": -1,
                "icao": "N/A",
                "latitude": 0.0,
                "longitude": 0.0,
                "altitude": 0.0,
                "velocidade": 0.0,
                "timestamp_emissao": 0.0,
                "timestamp_recepcao": tempo_recepcao,
                "latencia_canal": 0.0,
                "status_tesla": status,
                "motivo_rejeicao": motivo_rejeicao
            })
            return

        msg = pacote.mensagem
        latencia = tempo_recepcao - msg.timestamp if msg.timestamp else 0.0

        self.historico_eventos.append({
            "intervalo": pacote.intervalo_i,
            "icao": msg.icao,
            "latitude": msg.latitude,
            "longitude": msg.longitude,
            "altitude": msg.altitude,
            "velocidade": msg.velocidade,
            "timestamp_emissao": msg.timestamp,
            "timestamp_recepcao": tempo_recepcao,
            "latencia_canal": round(latencia, 4),
            "status_tesla": status,
            "motivo_rejeicao": motivo_rejeicao
        })

    def _obter_tempo_emissor_estimado(self, tempo_local: float) -> float:

        return (tempo_local - self.t_0) + self.d_t

    def receber(self, pacote: PacoteTESLA | None, tempo_recepcao: float = None) -> str:
        if tempo_recepcao is None:
            tempo_recepcao = time.time()

        if pacote is None:
            self.registrar_evento(None, tempo_recepcao, "PERDIDO", "Perda no canal de rádio")
            return "PERDIDO"

        i = pacote.intervalo_i

        tempo_limite_divulgacao = (i + self.d) * self.t_int
        tempo_estimado_emissor = self._obter_tempo_emissor_estimado(tempo_recepcao)

        if tempo_estimado_emissor >= tempo_limite_divulgacao:

            motivo = "Inseguro - Chegou muito tarde"
            self.rejeitados.append({"pacote": pacote, "motivo": motivo})
            self.registrar_evento(pacote, tempo_recepcao, "REJEITADO_TEMPO", motivo)
            return "REJEITADO — Pacote chegou após a janela de segurança"

        self.buffer_mensagens[i] = pacote

        status_retorno = None

        if pacote.idx_chave_revelada >= 0 and pacote.chave_revelada:
            k_v = pacote.chave_revelada
            v = pacote.idx_chave_revelada

            if v > self.idx_ultima_chave:
                if not verificar_chave(k_v, v, self.ultima_chave_confirmada, self.idx_ultima_chave):
                    motivo = "Chave divulgada não pertence à cadeia"
                    self.registrar_evento(pacote, tempo_recepcao, "REJEITADO_CADEIA", motivo)
                    return f"REJEITADO — {motivo}"

                # Atualiza a chave confiável da cadeia
                self.ultima_chave_confirmada = k_v
                self.idx_ultima_chave = v

                if v in self.buffer_mensagens:
                    pacote_pendente = self.buffer_mensagens.pop(v)
                    k_linha_v = derivar_chave_mac(k_v)
                    msg_bytes = pacote_pendente.mensagem.serializar()

                    if verificar_mac(msg_bytes, k_linha_v, pacote_pendente.mac):
                        self.autenticados.append({
                            "mensagem": pacote_pendente.mensagem,
                            "intervalo": v
                        })
                        self.registrar_evento(pacote_pendente, tempo_recepcao, "AUTENTICADO")
                        status_retorno = f"AUTENTICADO — Mensagem do intervalo {v} verificada com sucesso"
                    else:
                        motivo = "MAC inválido"
                        self.rejeitados.append({
                            "mensagem": pacote_pendente.mensagem,
                            "intervalo": v,
                            "motivo": motivo
                        })
                        self.registrar_evento(pacote_pendente, tempo_recepcao, "REJEITADO_MAC", motivo)
                        status_retorno = "REJEITADO — MAC não confere"

        # Se a mensagem apenas entrou no buffer aguardando a chave futura
        if status_retorno is None:
            self.registrar_evento(pacote, tempo_recepcao, "EM_BUFFER")
            status_retorno = "RECEBIDO — Armazenado no buffer aguardando chave divulgada"

        return status_retorno