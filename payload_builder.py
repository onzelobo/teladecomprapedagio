from datetime import datetime, timedelta

def build_payload(data: dict) -> dict:
    """Constrói o payload JSON conforme o contrato da API DCLOGG/Velozter."""
    
    hoje = datetime.now()
    fim = hoje + timedelta(days=7)

    return {
        "routes": [
            {
                "route": [
                    {
                        "idDocumentoTransporte": data["dt"],
                        "cnpj": "42278291000124",
                        "placa": data["placa"].upper(),
                        "neixos": str(data["eixos"]),
                        "inicioVigencia": hoje.strftime("%Y%m%d"),
                        "fimVigencia": fim.strftime("%Y%m%d"),
                        "positions": {
                            "position": [
                                {
                                    "country": "BR",
                                    "state": data["origem"]["uf"].upper(),
                                    "city": data["origem"]["cidade"].upper(),
                                    "eixoSuspenso": False
                                },
                                {
                                    "country": "BR",
                                    "state": data["destino"]["uf"].upper(),
                                    "city": data["destino"]["cidade"].upper(),
                                    "eixoSuspenso": False
                                }
                            ],
                            "waypoint_index": [] # Campo obrigatório em alguns gateways
                        }
                    }
                ]
            }
        ]
    }