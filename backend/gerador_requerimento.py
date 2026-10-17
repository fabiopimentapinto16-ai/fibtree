from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from datetime import datetime

def gerar_pdf_requerimento(dados, caminho):
    doc = SimpleDocTemplate(caminho, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle("T", parent=estilos["Title"], fontSize=18, textColor=HexColor("#0a4d68"), spaceAfter=10)
    corpo = ParagraphStyle("C", parent=estilos["Normal"], fontSize=11, leading=14, spaceAfter=6)

    c = []
    c.append(Paragraph("REQUERIMENTO DE PESQUISA MINERAL", titulo))
    c.append(Paragraph(f"Data de Emissão: {datetime.now().strftime('%d/%m/%Y')}", corpo))
    c.append(Spacer(1, 0.5*cm))

    c.append(Paragraph("<b>1. DADOS DO REQUERENTE</b>", corpo))
    c.append(Paragraph("Nome Completo / Razão Social: __________________________________________________", corpo))
    c.append(Paragraph("CPF / CNPJ: ________________________  Telefone: (__) _____________", corpo))
    c.append(Paragraph("Endereço: _____________________________________________________________________", corpo))
    c.append(Spacer(1, 0.5*cm))

    coord = dados.get("coordenada", {})
    pi = dados.get("ponto_interesse", {})

    c.append(Paragraph("<b>2. DADOS DA ÁREA REQUERIDA</b>", corpo))
    c.append(Paragraph(f"Coordenada Central (Analisada): Lat {coord.get('lat')} / Lng {coord.get('lng')}", corpo))
    if pi:
        c.append(Paragraph(f"Ponto de Interesse (Maior Potencial): Lat {pi.get('lat')} / Lng {pi.get('lng')}", corpo))
        c.append(Paragraph(f"Score de Potencial: {pi.get('score')}%", corpo))
    c.append(Paragraph("Área Estimada (Raio de 5km): Aproximadamente 7.850 hectares.", corpo))
    c.append(Paragraph("Substância Mineral Pretendida: " + dados.get("tipo_principal", "").upper(), corpo))
    c.append(Spacer(1, 0.5*cm))

    c.append(Paragraph("<b>3. JUSTIFICATIVA TÉCNICA</b>", corpo))
    c.append(Paragraph(f"O local apresenta um Score de {dados.get('score_final')}/100, sendo classificado como {dados.get('classificacao')}.", corpo))
    c.append(Paragraph("A análise de satélite identificou anomalias espectrais (óxido de ferro e argila) compatíveis com a presença do minério.", corpo))
    if dados.get("pontos_sigmine"):
        c.append(Paragraph(f"Foram identificados {len(dados['pontos_sigmine'])} processos minerários próximos, indicando uma província mineral ativa na região.", corpo))
    c.append(Spacer(1, 0.5*cm))

    c.append(Paragraph("<b>4. PRÓXIMOS PASSOS (ROTEIRO ANM)</b>", corpo))
    passos = [
        "1. Acesse o sistema SEI/ANM (Agência Nacional de Mineração).",
        "2. Selecione a opção 'Requerimento de Pesquisa'.",
        "3. Insira as coordenadas do Ponto de Interesse listadas acima.",
        "4. Anexe este documento e o Memorial Descritivo gerado pelo aplicativo.",
        "5. Pague a Taxa de Emolumentos (TR) e protocole o pedido.",
        "6. Após o deferimento, contrate um engenheiro de minas para emitir a ART no CREA."
    ]
    for p in passos:
        c.append(Paragraph(p, corpo))

    c.append(Spacer(1, 1*cm))
    c.append(Paragraph("_______________________________________________________", corpo))
    c.append(Paragraph("Assinatura do Requerente", corpo))

    doc.build(c)
    return caminho
