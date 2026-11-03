import time
from core.mensagem import MensagemADSB
from entidades.aeronave import Aeronave
from entidades.estacao_solo import EstacaoSolo


def test_bloqueio_pacote_atrasado_spoofing():
    t_zero = time.time()
    atraso_d = 2

    aeronave = Aeronave(icao="TEST01", n_intervalos=5, atraso_divulgacao=atraso_d)
    estacao = EstacaoSolo(
        chave_raiz=aeronave.chave_raiz,
        duracao_intervalo=0.1,
        atraso_divulgacao=atraso_d,
        max_drift_d_t=0.01,
        t_zero=t_zero
    )

    msg = MensagemADSB("TEST01", -23.5, -46.6, 1000.0, 250.0, time.time())
    pacote = aeronave.transmitir(msg)

    tempo_muito_atrasado = t_zero + ((1 + atraso_d) * 0.1) + 0.5

    resultado = estacao.receber(pacote, tempo_recepcao=tempo_muito_atrasado)

    assert "REJEITADO" in resultado
    assert len(estacao.rejeitados) == 1
    assert estacao.rejeitados[0]["motivo"] == "Inseguro - Chegou muito tarde"