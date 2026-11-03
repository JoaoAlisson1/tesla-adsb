import time
from core.mensagem import MensagemADSB
from entidades.aeronave import Aeronave
from entidades.estacao_solo import EstacaoSolo


def test_autenticacao_fluxo_com_buffer():
    t_zero = time.time()
    n_msgs = 4
    d = 2

    aeronave = Aeronave(icao="TEST02", n_intervalos=n_msgs + d + 1, atraso_divulgacao=d)
    estacao = EstacaoSolo(
        chave_raiz=aeronave.chave_raiz,
        duracao_intervalo=0.1,
        atraso_divulgacao=d,
        max_drift_d_t=0.01,
        t_zero=t_zero
    )

    for i in range(n_msgs + d):
        msg = MensagemADSB("TEST02", 0.0, 0.0, 0.0, 0.0, time.time())
        pacote = aeronave.transmitir(msg)

        t_atual = time.time()
        estacao.receber(pacote, tempo_recepcao=t_atual)
        time.sleep(0.1)

    autenticados_idx = [item["intervalo"] for item in estacao.autenticados]

    assert 1 in autenticados_idx
    assert 2 in autenticados_idx
    assert len(estacao.rejeitados) == 0