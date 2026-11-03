from core.mensagem import MensagemADSB

if __name__ == "__main__":
    import time

    msg = MensagemADSB(
        icao="E48C12",
        latitude=-29.7123,
        longitude=-53.7181,
        altitude=3000.0,
        velocidade=250.0,
        timestamp=time.time()
    )

    dados_bytes = msg.serializar()
    print(f"Mensagem em bytes: {dados_bytes}")
    print(f"Tamanho em bytes: {len(dados_bytes)} bytes")