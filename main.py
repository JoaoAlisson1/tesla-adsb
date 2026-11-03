import time
from core.mensagem import MensagemADSB
from core.bootstrapping import VerificadorBootstrapping
from core.metricas import salvar_dataset_simulacao
from entidades.aeronave import Aeronave
from entidades.estacao_solo import EstacaoSolo
from rede.canal import CanalRadio


def simular(n_mensagens: int = 20, prob_perda: float = 0.1, atraso_divulgacao: int = 2):
    print("=" * 60)
    print("   SIMULAÇÃO — PROTOCOLO TESLA + ADS-B + X.509 (RFC 4082)")
    print("=" * 60)

    # Tempo t_0 sincronizado para o bootstrapping seguro
    t_zero = time.time()
    t_int = 0.1

    aeronave = Aeronave(
        icao="ABC123",
        n_intervalos=n_mensagens + atraso_divulgacao + 1,
        atraso_divulgacao=atraso_divulgacao
    )

    # A aeronave gera e assina digitalmente o pacote de inicialização contendo K_0
    pacote_boot = aeronave.gerar_pacote_bootstrapping(t0=t_zero, t_int=t_int)

    # A Estação de Solo valida a assinatura RSA e o Certificado X.509 da Aeronave antes de aceitar K_0
    k0_autenticada = VerificadorBootstrapping.validar_pacote_bootstrapping(pacote_boot)

    if k0_autenticada is None:
        print("\n  ! REJEITADO: Falha na validação do certificado X.509 ou assinatura do Bootstrapping!")
        print("    A sessão TESLA não será iniciada por risco de personificação (Spoofing).")
        return

    canal = CanalRadio(
        prob_perda=prob_perda,
        latencia_base=0.01,
        variacao_max=0.002
    )

    estacao = EstacaoSolo(
        chave_raiz=k0_autenticada,  # Recebe a K_0 validada no Bootstrapping X.509
        duracao_intervalo=t_int,
        atraso_divulgacao=atraso_divulgacao,
        max_drift_d_t=0.02,
        t_zero=t_zero
    )

    print(f"\n[CONFIG] Aeronave           : {aeronave.icao}")
    print(f"[CONFIG] Intervalos Totais  : {n_mensagens}")
    print(f"[CONFIG] Prob. perda canal  : {prob_perda * 100:.0f}%")
    print(f"[CONFIG] Atraso Divulgação  : d = {atraso_divulgacao}")
    print(f"[CONFIG] Bootstrapping X.509: Chave K_0 autenticada com sucesso via RSA/X.509\n")
    print("-" * 60)

    tot_rodadas = n_mensagens + atraso_divulgacao

    for idx in range(tot_rodadas):

        if idx < n_mensagens:
            mensagem = MensagemADSB(
                icao="ABC123",
                latitude=-23.5 + idx * 0.01,
                longitude=-46.6 + idx * 0.01,
                altitude=10000.0,
                velocidade=250.0,
                timestamp=time.time()
            )
        else:
            mensagem = MensagemADSB("ABC123", 0.0, 0.0, 0.0, 0.0, time.time())

        pacote = aeronave.transmitir(mensagem)

        pacote_recebido, tempo_recepcao = canal.transmitir(pacote)

        resultado = estacao.receber(pacote_recebido, tempo_recepcao)

        if resultado == "PERDIDO":
            icone = "✗"
        elif "AUTENTICADO" in resultado:
            icone = "✓"
        elif "RECEBIDO" in resultado:
            icone = "~"
        else:
            icone = "!"

        i_exibicao = idx + 1
        if idx < n_mensagens:
            print(f"  [{icone}] Intervalo {i_exibicao:02d}: {resultado}")
        else:
            print(f"  [{icone}] Intervalo {i_exibicao:02d} (Flush d={atraso_divulgacao}): {resultado}")

        time.sleep(t_int)

    print("-" * 60)

    print("\n" + "=" * 60)
    print("   RELATÓRIO FINAL E VALIDAÇÃO")
    print("=" * 60)

    autenticados = [p["intervalo"] for p in estacao.autenticados]
    rejeitados = [p["mensagem"] for p in estacao.rejeitados]
    perdidos = canal.estatisticas["intervalos_perdidos"]
    em_buffer = list(estacao.buffer_mensagens.keys())

    print(f"\n  Enviados pelo canal      : {canal.estatisticas['enviados']}")
    print(f"  Perdidos no canal        : {canal.estatisticas['perdidos']}")
    print(f"  Autenticados com sucesso : {len(autenticados)}")
    print(f"  Rejeitados/Inseguros     : {len(rejeitados)}")
    print(f"  Ainda no buffer          : {len(em_buffer)}")

    print(f"\n  Intervalos perdidos no canal : {perdidos if perdidos else '—'}")
    print(f"  Intervalos autenticados     : {autenticados if autenticados else '—'}")
    print(f"  Ainda em buffer (não final)  : {em_buffer if em_buffer else '—'}")

    print("\n" + "-" * 60)
    print("  VALIDAÇÃO CRUZADA DE SEGURANÇA (RFC 4082)")
    print("-" * 60)

    nao_autenticados = set(perdidos) | set(em_buffer)
    autenticados_set = set(autenticados)
    intersecao = nao_autenticados & autenticados_set

    if not intersecao:
        print("\n  ✓ Consistência Confirmada: Nenhum pacote perdido no canal")
        print("    ou corrompido foi indevidamente autenticado.")
    else:
        print(f"\n  ! ALERTA DE FALHA: Interseção detectada nos intervalos: {intersecao}")

    print("\n" + "=" * 60)

    salvar_dataset_simulacao(estacao.historico_eventos, filepath="dados_simulacao.csv")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    simular(n_mensagens=15, prob_perda=0.15, atraso_divulgacao=2)