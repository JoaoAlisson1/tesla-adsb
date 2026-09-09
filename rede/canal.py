import random
import time

class CanalRadio:
    def __init__(self,
                 prob_perda: float = 0.1,
                 latencia_base: float = 0.1,
                 variacao_max: float = 0.005):

        self.prob_perda = prob_perda
        self.latencia_base = latencia_base
        self.variacao_max = variacao_max
        self.estatisticas = {
            "enviados": 0,
            "perdidos": 0,
            "intervalos_perdidos": []
        }

    def transmitir(self, pacote: dict) -> dict | None:
        self.estatisticas["enviados"] += 1

        if random.random() < self.prob_perda:
            self.estatisticas["perdidos"] += 1

            if pacote and "intervalo" in pacote:
                self.estatisticas["intervalos_perdidos"].append(pacote["intervalo"])

            return None

        variacao = random.uniform(-self.variacao_max, self.variacao_max)
        time.sleep(self.latencia_base + variacao)

        return pacote