import hashlib
import os

def gerar_cadeia(n_intervalos: int) -> list[bytes]:

    semente = os.urandom(32)
    cadeia = [semente]

    for _ in range(n_intervalos):
        proxima = hashlib.sha256(cadeia[-1]).digest()
        cadeia.append(proxima)

    return list(reversed(cadeia))

def verificar_chave(chave_recebida: bytes, chave_anterior: bytes, max_saltos: int = 10) -> bool:
    # aplica o hash repetidamente para validar  as chaves mesmo após perdas no canal.
    temp = chave_recebida

    for _ in range(max_saltos):
        temp = hashlib.sha256(temp).digest()
        if temp == chave_anterior:
            return True

    return False