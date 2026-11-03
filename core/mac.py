import hmac
import hashlib

TAMANHO_MAC = 8


def calcular_mac(mensagem: bytes, chave_mac: bytes) -> bytes:

    return hmac.new(chave_mac, mensagem, hashlib.sha256).digest()[:TAMANHO_MAC]


def verificar_mac(mensagem: bytes, chave_mac: bytes, mac_recebido: bytes) -> bool:

    mac_calculado = calcular_mac(mensagem, chave_mac)

    return hmac.compare_digest(mac_calculado, mac_recebido)