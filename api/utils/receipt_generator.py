import os
import json
import tempfile
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from ..types.sales_types import SaleDict, ChangeDict


def generate_sale_receipt(sale_data: SaleDict, change: ChangeDict = None):
    """
    IDENTICO ao seu, apenas com altura dinâmica automática.
    """

    # ======================================================
    # 1️⃣ CALCULAR QUANTAS LINHAS SERÃO IMPRESSAS
    # ======================================================
    line_height_mm = 5
    total_lines = 0

    def count_line():
        nonlocal total_lines
        total_lines += 1

    # --- LOGO (ocupa espaço fixo) ---
    LOGO_BLOCK_MM = 35  # altura do logo + margem

    # --- Cabeçalho ---
    count_line()  # store name
    count_line()
    count_line()
    count_line()

    store = None
    PUBLIC_DIR = os.path.join(settings.BASE_DIR, "public")
    info_path = os.path.join(PUBLIC_DIR, "inf_store.json")
    logo_path = os.path.join(PUBLIC_DIR, "logo_store.png")

    try:
        with open(info_path, "r", encoding="utf-8") as f:
            store = json.load(f)
    except:
        store = {
            "store_name": "Stock Plus",
            "fantasy_name": "",
            "cnpj": "",
            "address": "",
            "phone": ""
        }

    # linhas opcionais do header
    if store.get("fantasy_name"):
        count_line()
    if store.get("cnpj"):
        count_line()
    if store.get("address"):
        count_line()
    if store.get("phone"):
        count_line()

    # --- Cliente ---
    customer = sale_data["customer"]

    if customer["id"] == 1:
        count_line()
    else:
        count_line()
        count_line()
        count_line()
        count_line()

    for item in sale_data["items"]:
        count_line()
        count_line()
        count_line()

    # --- Resumo ---
    count_line()
    count_line()
    count_line()

    if change:
        count_line()
        count_line()

    count_line()  # obrigado

    # ======================================================
    # 2️⃣ DEFINIR ALTURA FINAL DO PDF
    # ======================================================
    dynamic_height_mm = LOGO_BLOCK_MM + (total_lines * line_height_mm) + 30
    receipt_height = dynamic_height_mm * mm
    receipt_width = 80 * mm

    # ======================================================
    # 3️⃣ GERAR O PDF (seu código original)
    # ======================================================
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_pdf.name, pagesize=(receipt_width, receipt_height))

    y = receipt_height - 10 * mm

    def write(text, size=10):
        nonlocal y
        c.setFont("Courier", size)
        c.drawString(5 * mm, y, text)
        y -= line_height_mm * mm

    def write_centered(text, size=10):
        nonlocal y
        c.setFont("Courier", size)
        w = c.stringWidth(text, "Courier", size)
        c.drawString((receipt_width - w) / 2, y, text)
        y -= line_height_mm * mm

    # ================================
    # LOGO PNG (mesmo que antes)
    # ================================
    if os.path.exists(logo_path):
        logo_w = 50 * mm
        logo_h = 25 * mm
        c.drawImage(
            logo_path,
            (receipt_width - logo_w) / 2,
            y - logo_h,
            width=logo_w,
            height=logo_h,
            preserveAspectRatio=True,
            mask='auto'
        )
        y -= (logo_h + 5 * mm)

    # ================================
    # HEADERS (mesmo que antes)
    # ================================
    write_centered(store.get("store_name", "Stock Plus"), 18)
    write_centered("-=-=- Comprovante de Venda -=-=-")
    write_centered("NÃO É DOCUMENTO FISCAL")
    write_centered("------------------------------")

    if store.get("fantasy_name"):
        write_centered(store["fantasy_name"])
    if store.get("cnpj"):
        write_centered(f"CNPJ: {store['cnpj']}")
    if store.get("address"):
        write_centered(store["address"])
    if store.get("phone"):
        write_centered(f"Tel: {store['phone']}")

    write_centered("------------------------------")

    # ================================
    # CLIENTE
    # ================================
    if customer["id"] == 1:
        write("Cliente: Avulso")
    else:
        write(f"Razão: {customer['name']}")
        write(f"Fantasia: {customer['trade_name']}")
        write(f"CPF/CNPJ: {customer['cnpj_or_cpf']}")
        write(f"Endereço: {customer['address']}")

    write_centered("------------------------------")

    # ================================
    # PRODUTOS
    # ================================
    write_centered("Produtos", 12)

    for item in sale_data["items"]:
        write(f"{item['product']} - {item['quantity']} x R$ {item['unit_price']:.2f}")
        write(f"Subtotal: R$ {item['subtotal']:.2f}")
        write_centered("------------------------------")

    # ================================
    # RESUMO
    # ================================
    write(f"Desconto: R$ {sale_data['discount']:.2f}")
    write(f"TOTAL: R$ {sale_data['total_amount']:.2f}", 12)
    write(f"Pagamento: {sale_data['payment_method']['name']}")

    if change:
        write(f"Recebido: R$ {change['money_received']:.2f}")
        write(f"Troco: R$ {change['change']:.2f}")

    write_centered("------------------------------")
    write_centered("Obrigado pela preferência!", 10)

    # FINALIZA
    c.showPage()
    c.save()

    return temp_pdf.name
