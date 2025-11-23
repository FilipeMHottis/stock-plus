import os
import json
from django.conf import settings

PRINTER_FILE = "printer.json"


def load_printer_for_user(user_id: int):
    """
    Carrega impressora do usuário a partir de:
    public/printer.json

    Formato esperado:
    {
        "DEFAULT": {
            "user": { "id": 0, "name": "DEFAULT" },
            "print_name": "EPSON3F7A62",
            "paper_width_mm": 80,"interface": "system"
        },
        "2": {
            "user": { "id": 2, "name": "José" },
            "print_name": "MINHA_EPSON",
            "paper_width_mm": 80,
            "interface": "system"
        }
    }
    """

    public_dir = os.path.join(settings.BASE_DIR, "public")
    file_path = os.path.join(public_dir, PRINTER_FILE)

    # -------------------------------
    # Carrega JSON
    # -------------------------------
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        print("⚠ printer.json não encontrado ou inválido!")
        return _default_config()

    # -------------------------------
    # Se existir config por usuário
    # -------------------------------
    str_id = str(user_id)
    if str_id in data:
        return data[str_id]

    # -------------------------------
    # Senão retorna o DEFAULT
    # -------------------------------
    if "DEFAULT" in data:
        return data["DEFAULT"]

    # Fallback final
    return _default_config()


def _default_config():
    """
    Configuração de impressora padrão caso
    o arquivo JSON não exista ou esteja inválido.
    """

    return {
        "user": {"id": 0, "name": "DEFAULT"},
        "print_name": None,
        "paper_width_mm": 80,
        "interface": "system"
    }
