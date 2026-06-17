import os
from datetime import datetime, timedelta
from typing import Any, Dict

def build_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """Constrói o payload JSON conforme o contrato da API DCLOGG/Velozter."""
    
    hoje = datetime.now()
    fim = hoje + timedelta(days=7)

    cnpj_empresa = os.getenv("EMPRESA_CNPJ")
    if not cnpj_empresa:
        raise ValueError("A variável de ambiente EMPRESA_CNPJ não foi configurada.")

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
                        "cnpj": cnpj_empresa,
                        "placa": data["placa"].upper(),
                        "neixos": str(data["eixos"]),
                        "fimVigencia": fim.strftime("%Y%m%d"),
                        "inicioVigencia": hoje.strftime("%Y%m%d"),
                        "observacao": f"Email: {data['email']}",
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