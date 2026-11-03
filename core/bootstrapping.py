import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding


class GestorCertificadoX509:

    def __init__(self, icao: str):
        self.icao = icao

        self.chave_privada = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.chave_publica = self.chave_privada.public_key()
        self.certificado = self._gerar_certificado()

    def _gerar_certificado(self) -> x509.Certificate:
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, f"Aeronave-{self.icao}"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Autoridade Aeronautica"),
        ])

        cert = x509.CertificateBuilder() \
            .subject_name(subject) \
            .issuer_name(issuer) \
            .public_key(self.chave_publica) \
            .serial_number(x509.random_serial_number()) \
            .not_valid_before(datetime.datetime.now(datetime.timezone.utc)) \
            .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)) \
            .sign(self.chave_privada, hashes.SHA256())

        return cert

    def assinar_bootstrapping(self, k0: bytes, t0: float, t_int: float, d: int) -> dict:

        payload = f"{k0.hex()},{t0:.3f},{t_int:.3f},{d}".encode("utf-8")

        assinatura = self.chave_privada.sign(
            payload,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return {
            "k0": k0,
            "t0": t0,
            "t_int": t_int,
            "d": d,
            "assinatura": assinatura,
            "certificado": self.certificado
        }


class VerificadorBootstrapping:

    @staticmethod
    def validar_pacote_bootstrapping(pacote_boot: dict) -> bytes | None:
        k0 = pacote_boot["k0"]
        t0 = pacote_boot["t0"]
        t_int = pacote_boot["t_int"]
        d = pacote_boot["d"]
        assinatura = pacote_boot["assinatura"]
        cert: x509.Certificate = pacote_boot["certificado"]

        payload = f"{k0.hex()},{t0:.3f},{t_int:.3f},{d}".encode("utf-8")
        chave_publica = cert.public_key()

        try:
            #Valida se a assinatura RSA bate com a chave pública contida no certificado
            chave_publica.verify(
                assinatura,
                payload,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            return k0
        except Exception:
            return None