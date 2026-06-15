from datetime import datetime, timedelta
from typing import Any, Dict

def build_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """Constrói o payload JSON conforme o contrato da API DCLOGG/Velozter."""
    
    hoje = datetime.now()
    fim = hoje + timedelta(days=7)

    origem: Dict[str, Any] = {
        "country": "BR",
        "state": data["origem"]["uf"].upper(),
        "city": data["origem"]["cidade"].upper(),
        "eixoSuspenso": False
    }

    destino: Dict[str, Any] = {
        "country": "BR",
        "state": data["destino"]["uf"].upper(),
        "city": data["destino"]["cidade"].upper(),
        "eixoSuspenso": False
    }

    return {
        "routes": [
            {
                "route": [
                    {
                        "idDocumentoTransporte": int(data["dt"]),
                        "cnpj": "42278291000124",
                        "placa": data["placa"].upper(),
                        "neixos": str(data["eixos"]),
                        "fimVigencia": fim.strftime("%Y%m%d"),
                        "inicioVigencia": hoje.strftime("%Y%m%d"),
                        "positions": {
                            "position": [
                                origem,
                                destino,
                                origem
                            ],
                            "waypoint_index": ["0"]
                        }
                    }
                ]
            }
        ]
    }