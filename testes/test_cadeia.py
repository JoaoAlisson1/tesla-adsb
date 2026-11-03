import os

from core.cadeia import gerar_cadeia, verificar_chave

if __name__ == "__main__":
    N = 5
    cadeia = gerar_cadeia(N)

    print(f"Tamanho total da cadeia (N + Raiz K0): {len(cadeia)}")
    print(f"K0 (Raiz pública): {cadeia[0].hex()[:16]}...")
    print(f"K1 (Chave do Int 1): {cadeia[1].hex()[:16]}...")

    k1 = cadeia[1]
    k0 = cadeia[0]
    valido_legitimo = verificar_chave(k1, k0)
    print(f"\n[TESTE 1] Chave K1 é válida contra K0? -> {valido_legitimo}")

    #  Validação de uma chave falsa (Spoofing)
    # Simula um atacante tentando usar uma chave aleatória
    chave_falsa = os.urandom(32)
    valido_falso = verificar_chave(chave_falsa, k0)
    print(f"[TESTE 2] Chave FALSA é aceita contra K0? -> {valido_falso}")