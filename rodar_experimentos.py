import time
from core.bootstrapping import VerificadorBootstrapping
from core.mensagem import MensagemADSB
from core.metricas import salvar_dataset_simulacao
from entidades.aeronave import Aeronave
from entidades.estacao_solo import EstacaoSolo
from rede.canal import CanalRadio


def executar_cenario(nome_cenario: str, n_mensagens: int, prob_perda: float, latencia_base: float) -> list[dict]:
    print(f"-> Executando {nome_cenario} (Perda: {prob_perda * 100:.0f}%, Latência: {latencia_base * 1000:.1f}ms)...")

    t_zero = time.time()
    t_int = 0.1
    d = 2

    aeronave = Aeronave(icao="ABC123", n_intervalos=n_mensagens + d + 1, atraso_divulgacao=d)
    pacote_boot = aeronave.gerar_pacote_bootstrapping(t0=t_zero, t_int=t_int)
    k0 = VerificadorBootstrapping.validar_pacote_bootstrapping(pacote_boot)

    if k0 is None:
        raise ValueError("Falha no bootstrapping do cenário.")

    estacao = EstacaoSolo(chave_raiz=k0, duracao_intervalo=t_int, atraso_divulgacao=d, max_drift_d_t=0.02, t_zero=t_zero)
    canal = CanalRadio(prob_perda=prob_perda, latencia_base=latencia_base, variacao_max=0.005)

    tot_rodadas = n_mensagens + d

    for idx in range(tot_rodadas):
        if idx < n_mensagens:
            msg = MensagemADSB("ABC123", -23.5 + idx * 0.01, -46.6 + idx * 0.01, 10000.0, 250.0, time.time())
        else:
            msg = MensagemADSB("ABC123", 0.0, 0.0, 0.0, 0.0, time.time())

        pacote = aeronave.transmitir(msg)
        pacote_rec, t_rec = canal.transmitir(pacote)
        estacao.receber(pacote_rec, t_rec)
        time.sleep(0.005)

    for evento in estacao.historico_eventos:
        evento["cenario"] = nome_cenario

    return estacao.historico_eventos


if __name__ == "__main__":
    todos_eventos = []

    print("=" * 60)
    print("   GERAÇÃO DE MASSA DE DADOS PARA O TCC (3 CENÁRIOS)")
    print("=" * 60 + "\n")

    todos_eventos.extend(executar_cenario("1_Ideal", n_mensagens=100, prob_perda=0.02, latencia_base=0.005))
    todos_eventos.extend(executar_cenario("2_Moderado", n_mensagens=100, prob_perda=0.15, latencia_base=0.015))
    todos_eventos.extend(executar_cenario("3_Severo", n_mensagens=100, prob_perda=0.35, latencia_base=0.030))

    salvar_dataset_simulacao(todos_eventos, filepath="dataset_experimentos_tesla.csv")
    print("\n✓ Concluído! Arquivo 'dataset_experimentos_tesla.csv' gerado com sucesso.")