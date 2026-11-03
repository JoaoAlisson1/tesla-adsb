import random
import time
from typing import Any


class CanalRadio:
    def __init__(self,
                 prob_perda: float = 0.1,
                 latencia_base: float = 0.05,
                 variacao_max: float = 0.005):

        self.prob_perda = prob_perda
        self.latencia_base = latencia_base
        self.variacao_max = variacao_max
        self.estatisticas = {
            "enviados": 0,
            "perdidos": 0,
            "intervalos_perdidos": []
        }

    def transmitir(self, pacote: Any) -> tuple[Any | None, float]:

        self.estatisticas["enviados"] += 1
        tempo_envio = time.time()

        if random.random() < self.prob_perda:
            self.estatisticas["perdidos"] += 1

            idx_intervalo = None
            if hasattr(pacote, "intervalo_i"):
                idx_intervalo = pacote.intervalo_i
            elif isinstance(pacote, dict) and "intervalo" in pacote:
                idx_intervalo = pacote["intervalo"]

            if idx_intervalo is not None:
                self.estatisticas["intervalos_perdidos"].append(idx_intervalo)

            return None, tempo_envio

        # Simulação de Latência
        variacao = random.uniform(-self.variacao_max, self.variacao_max)
        atraso_total = max(0.0, self.latencia_base + variacao)

        time.sleep(atraso_total)
        tempo_recepcao = time.time()

        return pacote, tempo_recepcao