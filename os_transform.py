def gerar_dt(os_str: str) -> str:
    """
    Converte a Ordem de Serviço (OS) no Documento de Transporte (DT).
    Exemplo: 4SSA128276A -> 4000312876 (SSA vira 0003)
    """
    mapa_portos = {
        "FOR": "0001", "REC": "0002", "SSA": "0003",
        "SSZ": "0004", "ITJ": "0005", "RIO": "0006", "MAO": "0007"
    }

    if len(os_str) < 5:
        raise ValueError("Formato de OS inválido ou muito curto.")

    sigla = os_str[1:4].upper()
    miolo = os_str[4:-1] # Remove última letra e mantém números

    if not (codigo_porto := mapa_portos.get(sigla)):
        raise ValueError(f"Sigla de porto '{sigla}' não mapeada.")

    # Formato: Primeiro dígito + Código do Porto + Miolo numérico
    return f"{os_str[0]}{codigo_porto}{miolo}"