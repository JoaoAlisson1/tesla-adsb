import pytest
import hashlib
from core.cadeia import gerar_cadeia, derivar_chave_mac, verificar_chave
from core.mac import calcular_mac, verificar_mac


def test_geracao_e_verificacao_cadeia():

    cadeia = gerar_cadeia(5)
    assert len(cadeia) == 6

    k_0 = cadeia[0]
    k_3 = cadeia[3]

    assert verificar_chave(chave_divulgada=k_3, idx_divulgada=3, chave_confiavel=k_0, idx_confiavel=0) is True
    # Tentativa de validar chave inválida ou adulterada
    assert verificar_chave(chave_divulgada=b"chave_falsa_12345678901234567890", idx_divulgada=3, chave_confiavel=k_0,
                           idx_confiavel=0) is False


def test_derivacao_separada_chave_mac():
    k_i = b"chave_cadeia_exemplo_32bytes_123"
    k_linha_i = derivar_chave_mac(k_i)

    assert k_linha_i != k_i
    assert len(k_linha_i) == 32


def test_verificacao_hmac():
    msg = b"ICAO:ABC123,LAT:-23.5"
    chave = b"chave_secreta_para_mac_12345678"
    mac = calcular_mac(msg, chave)

    assert verificar_mac(msg, chave, mac) is True
    assert verificar_mac(b"msg_adulterada", chave, mac) is False