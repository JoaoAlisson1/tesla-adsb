from core.mac import calcular_mac, verificar_mac

if __name__ == "__main__":
    chave_secreta = b"chave_temporaria_k1"
    dados_voo = b"LAT:-29.7123|LON:-53.7181|ALT:3000"

    mac_gerado = calcular_mac(dados_voo, chave_secreta)
    print(f"MAC Gerado (hex): {mac_gerado.hex()}")

    valido = verificar_mac(dados_voo, chave_secreta, mac_gerado)
    print(f"[TESTE 1] Mensagem íntegra: {valido}")

    dados_alterados = b"LAT:-29.7123|LON:-53.7181|ALT:9000"
    valido_spoofing = verificar_mac(dados_alterados, chave_secreta, mac_gerado)
    print(f"[TESTE 2] Mensagem alterada aceita? {valido_spoofing}")