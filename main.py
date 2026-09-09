import time
from core.mensagem import MensagemADSB
from entidades.aeronave import Aeronave
from entidades.estacao_solo import EstacaoSolo
from rede.canal import CanalRadio


def simular(n_mensagens: int = 20, prob_perda: float = 0.1):
    print("=" * 55)
    print("   SIMULAÇÃO — PROTOCOLO TESLA + ADS-B")
    print("=" * 55)

    aeronave = Aeronave(icao="ABC123", n_intervalos=n_mensagens)
    canal = CanalRadio(prob_perda=prob_perda)
    estacao = EstacaoSolo(chave_raiz=aeronave.chave_raiz)

    print(f"\n[CONFIG] Aeronave      : {aeronave.icao}")
    print(f"[CONFIG] Intervalos    : {n_mensagens}")
    print(f"[CONFIG] Prob. perda   : {prob_perda * 100:.0f}%")
    print(f"[CONFIG] K0 distribuída à estação via X.509\n")
    print("-" * 55)

    #Simula intervalo a intervalo
    for i in range(n_mensagens):
        mensagem = MensagemADSB(
            icao="ABC123",
            latitude=-23.5 + i * 0.01,
            longitude=-46.6 + i * 0.01,
            altitude=10000.0,
            velocidade=250.0,
            timestamp=time.time()
        )

        pacote = aeronave.transmitir(mensagem)
        pacote_recebido = canal.transmitir(pacote)
        resultado = estacao.receber(pacote_recebido)

        if resultado == "PERDIDO":
            icone = "✗"
        elif "AUTENTICADO" in resultado:
            icone = "✓"
        elif "aguardando" in resultado:
            icone = "~"
        else:
            icone = "!"

        print(f"  [{icone}] Intervalo {i + 1:02d}: {resultado}")

    print("-" * 55)

    print("\n" + "=" * 55)
    print("   RELATÓRIO FINAL")
    print("=" * 55)

    autenticados = [p["intervalo"] for p in estacao.autenticados]
    rejeitados   = [p["intervalo"] for p in estacao.rejeitados]
    perdidos     = canal.estatisticas["intervalos_perdidos"]
    em_buffer    = list(estacao.buffer_mensagens.keys())

    print(f"\n  Enviados pelo canal      : {canal.estatisticas['enviados']}")
    print(f"  Perdidos no canal        : {canal.estatisticas['perdidos']}")
    print(f"  Autenticados             : {len(autenticados)}")
    print(f"  Rejeitados               : {len(rejeitados)}")
    print(f"  Aguardando no buffer     : {len(em_buffer)}")

    print(f"\n  Intervalos perdidos      : {perdidos if perdidos else '—'}")
    print(f"  Intervalos autenticados  : {autenticados if autenticados else '—'}")
    print(f"  Intervalos rejeitados    : {rejeitados if rejeitados else '—'}")
    print(f"  Ainda no buffer          : {em_buffer if em_buffer else '—'}")

    print("\n" + "-" * 55)
    print("  VALIDAÇÃO CRUZADA")
    print("-" * 55)

    # Verifica se os intervalos perdidos no canal
    # correspondem a mensagens que não foram autenticadas
    nao_autenticados = set(perdidos) | set(rejeitados) | set(em_buffer)
    autenticados_set = set(autenticados)
    intersecao = nao_autenticados & autenticados_set

    if not intersecao:
        print("\n  ✓ Consistente: nenhum intervalo perdido ou rejeitado")
        print("    foi indevidamente autenticado.")
    else:
        print(f"\n  ! INCONSISTÊNCIA detectada nos intervalos: {intersecao}")
        print("    Verificar lógica de verificação da cadeia.")

    # Resumo de tolerância de perdas
    if perdidos:
        recuperados = [
            i for i in perdidos
            if i not in em_buffer and i not in rejeitados
        ]
        print(f"\n  Intervalos perdidos no canal  : {len(perdidos)}")
        print(f"  Impacto na autenticação       : "
              f"{len(perdidos) - len(recuperados)} mensagens não verificadas")
        print(f"\n  ✓ O protocolo continuou operando normalmente")
        print(f"    para os demais {len(autenticados)} intervalos.")

    print("\n" + "=" * 55 + "\n")


if __name__ == "__main__":
    simular(n_mensagens=20, prob_perda=0.1)