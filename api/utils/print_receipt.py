import os
import platform
import cups
import win32print
import win32api


def print_pdf(
    path: str,
    printer_name: str = None,
    interface: str = "system"
) -> bool:
    """
    Imprime um PDF usando:
    - interface="system": impressão padrão do SO (Windows/macOS/Linux)
    - interface="escpos": reservado para impressoras térmicas direto na porta

    path: caminho do PDF
    printer_name: nome da impressora
    Retorna True/False.
    """

    if not os.path.exists(path):
        print(f"❌ Arquivo não encontrado: {path}")
        return False

    system = platform.system()

    # ============================================================
    # ESC/POS (para futuro)
    # ============================================================
    if interface == "escpos":
        print("⚠ interface ESC/POS ainda não implementada.")
        return False

    # ============================================================
    # WINDOWS
    # ============================================================
    if system == "Windows":
        try:
            printers = win32print.EnumPrinters(2)
            real_printer_name = ""

            for printer in printers:
                if printer[2] == printer_name:
                    real_printer_name = printer[2]

            if real_printer_name == "":
                raise Exception(
                    f"A impressora '{printer_name}' não existe no sistema."
                )

            win32print.SetDefaultPrinter(real_printer_name)
            win32api.ShellExecute(
                0,
                "print",
                path,
                None,
                ".",
                0
            )

            print(f"🖨 Enviado para impressão: {printer_name or '[DEFAULT]'}")
            return True

        except Exception as e:
            print(f"❌ Erro ao imprimir no Windows: {e}")
            return False

    # ============================================================
    # LINUX / MACOS
    # ============================================================
    if system in ["Linux", "Darwin"]:
        try:
            conn = cups.Connection()
            printers = conn.getPrinters()

            if printer_name not in printers:
                raise Exception(
                    f"A impressora '{printer_name}' não existe no sistema."
                )

            # Envia o arquivo PDF para a impressora
            print_id = conn.printFile(
                printer_name, path, "Impressão Stock Plus", {}
            )
            print(
                f"🖨 Enviado para impressão: {printer_name} "
                f"(job id: {print_id})"
            )
            return True
        except Exception as e:
            print(f"❌ Erro ao imprimir no Linux/Mac: {e}")
            return False

    print("⚠ Sistema operacional não suportado.")
    return False
