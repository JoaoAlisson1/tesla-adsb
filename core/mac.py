import hmac
import hashlib

TAMANHO_MAC = 8

def calcular_mac(mensagem: bytes, chave: bytes) -> bytes:
    return hmac.new(chave, mensagem, hashlib.sha256).digest()[:TAMANHO_MAC]

def verificar_mac(mensagem: bytes, chave: bytes, mac_recebido: bytes) -> bool:

    mac_calculado = calcular_mac(mensagem, chave)

    return mac_calculado == mac_recebido