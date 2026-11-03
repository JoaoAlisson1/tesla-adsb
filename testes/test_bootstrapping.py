import time
from core.bootstrapping import GestorCertificadoX509, VerificadorBootstrapping


def test_bootstrapping_x509_valido():
    k0 = b"chave_k0_teste_32_bytes_1234567"
    gestor = GestorCertificadoX509("TESTE01")

    pacote_boot = gestor.assinar_bootstrapping(k0=k0, t0=time.time(), t_int=0.1, d=2)
    k0_extraida = VerificadorBootstrapping.validar_pacote_bootstrapping(pacote_boot)

    assert k0_extraida == k0


def test_bootstrapping_x509_adulterado():
    k0 = b"chave_k0_teste_32_bytes_1234567"
    gestor = GestorCertificadoX509("TESTE01")

    pacote_boot = gestor.assinar_bootstrapping(k0=k0, t0=time.time(), t_int=0.1, d=2)

    # Atacante altera a chave K0 enviada no pacote
    pacote_boot["k0"] = b"chave_falsa_32_bytes_1234567890"
    k0_extraida = VerificadorBootstrapping.validar_pacote_bootstrapping(pacote_boot)

    assert k0_extraida is None