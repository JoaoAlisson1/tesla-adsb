import hashlib
import os

def gerar_cadeia(n_intervalos: int) -> list[bytes]:

    # Semente secreta inicial (corresponde ao K_N no final da cadeia)
    semente = os.urandom(32)
    cadeia = [semente]

    for _ in range(n_intervalos):
        proxima = hashlib.sha256(cadeia[-1]).digest()
        cadeia.append(proxima)

    return list(reversed(cadeia))


def derivar_chave_mac(k_i: bytes) -> bytes:

    return hashlib.sha256(b"MAC_KEY_SALT" + k_i).digest()


def verificar_chave(chave_divulgada: bytes, idx_divulgada: int,
                    chave_confiavel: bytes, idx_confiavel: int) -> bool:

    if idx_divulgada <= idx_confiavel:
        return False

    saltos = idx_divulgada - idx_confiavel
    temp = chave_divulgada

    for _ in range(saltos):
        temp = hashlib.sha256(temp).digest()

    return temp == chave_confiavel