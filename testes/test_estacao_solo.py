from entidades.estacao_solo import EstacaoSolo

if __name__ == "__main__":
    import time
    from core.mensagem import MensagemADSB
    from entidades.aeronave import Aeronave

    aviao = Aeronave(icao="E48C12", n_intervalos=5)
    estacao = EstacaoSolo(chave_raiz=aviao.chave_raiz)

    msg = MensagemADSB(
        icao="E48C12",
        latitude=-29.7123,
        longitude=-53.7181,
        altitude=3000.0,
        velocidade=250.0,
        timestamp=time.time()
    )

    print("--- Teste de Recepção TESLA ---")

    pkt1 = aviao.transmitir(msg)
    res1 = estacao.receber(pkt1)
    print(f"Pacote 1: {res1}")

    pkt2 = aviao.transmitir(msg)
    res2 = estacao.receber(pkt2)
    print(f"Pacote 2: {res2}")

    print(f"\nMensagens autenticadas no receptor: {len(estacao.autenticados)}")