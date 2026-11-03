from core.mensagem import MensagemADSB
from entidades.aeronave import Aeronave

if __name__ == "__main__":
    import time

    aviao = Aeronave(icao="E48C12", n_intervalos=5)
    print(f"Chave Raiz K0 (hex): {aviao.chave_raiz.hex()[:16]}...")

    msg = MensagemADSB(
        icao="E48C12",
        latitude=-29.7123,
        longitude=-53.7181,
        altitude=3000.0,
        velocidade=250.0,
        timestamp=time.time()
    )

    pacote = aviao.transmitir(msg)
    print("\n--- Pacote Transmitido (Intervalo 1) ---")
    print(f"MAC (hex): {pacote['mac'].hex()}")
    print(f"Chave Revelada (K0 hex): {pacote['chave_revelada'].hex()[:16]}...")
    print(f"Próximo Intervalo: {aviao.intervalo_atual}")