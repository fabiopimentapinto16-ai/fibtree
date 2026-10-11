from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from datetime import datetime

def gerar_pdf(analise, caminho="relatorio_olho_deus.pdf"):
    doc = SimpleDocTemplate(caminho, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle("T", parent=estilos["Title"], fontSize=22, textColor=HexColor("#0a4d68"), spaceAfter=6)
    subtitulo = ParagraphStyle("S", parent=estilos["Heading2"], fontSize=14, textColor=HexColor("#088395"), spaceAfter=10)
    corpo = ParagraphStyle("C", parent=estilos["Normal"], fontSize=11, leading=16)
    destaque = ParagraphStyle("D", parent=corpo, fontSize=13, textColor=HexColor("#0a4d68"))
    c = []
    c.append(Paragraph("OLHO DE DEUS", titulo))
    c.append(Paragraph("Relatorio de Analise Mineral Preliminar", subtitulo))
    c.append(Paragraph("Data: " + datetime.now().strftime("%d/%m/%Y %H:%M"), corpo))
    c.append(Spacer(1, 0.4*cm))
    coord = analise["coordenada"]
    c.append(Paragraph("<b>Coordenada Analisada</b>", destaque))
    c.append(Paragraph("Latitude: " + str(round(coord["lat"], 6)) + " | Longitude: " + str(round(coord["lng"], 6)), corpo))
    c.append(Paragraph("Sistema de referencia: SIRGAS 2000", corpo))
    c.append(Paragraph("Raio de analise: 15 km", corpo))
    c.append(Spacer(1, 0.5*cm))
    c.append(Paragraph("<b>Resultado da Analise</b>", destaque))
    c.append(Spacer(1, 0.3*cm))
    dados = [["Indicador", "Valor"], ["Score Final", str(analise["score_final"]) + "/100"], ["Classificacao", analise["classificacao"]], ["Tipo Principal", analise["tipo_principal"].upper()], ["Score OURO", str(analise["score_ouro"]) + "/100"], ["Score TERRAS RARAS", str(analise["score_etr"]) + "/100"]]
    t = Table(dados, colWidths=[8*cm, 8*cm])
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), HexColor("#0a4d68")), ("TEXTCOLOR", (0,0), (-1,0), HexColor("#ffffff")), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 10), ("GRID", (0,0), (-1,-1), 0.5, HexColor("#cccccc")), ("ROWBACKGROUNDS", (0,1), (-1,-1), [HexColor("#f5f5f5"), HexColor("#ffffff")]), ("BOTTOMPADDING", (0,0), (-1,-1), 8), ("TOPPADDING", (0,0), (-1,-1), 8)]))
    c.append(t)
    c.append(Spacer(1, 0.6*cm))
    if analise.get("pontos_proximos"):
        c.append(Paragraph("<b>Pontos num raio de 15 km</b>", destaque))
        c.append(Spacer(1, 0.3*cm))
        dp = [["Nome", "Tipo", "Distancia", "Acesso"]]
        for p in analise["pontos_proximos"][:10]:
            tp = "Ouro" if p["tipo"] == "ouro" else "ETR"
            ds = "DENTRO" if p["dentro"] else str(p["distancia_km"]) + " km"
            dp.append([p["nome"], tp, ds, p["facilidade"]])
        tbl = Table(dp, colWidths=[6*cm, 3*cm, 3.5*cm, 3.5*cm])
        tbl.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), HexColor("#088395")), ("TEXTCOLOR", (0,0), (-1,0), HexColor("#ffffff")), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 9), ("GRID", (0,0), (-1,-1), 0.5, HexColor("#cccccc")), ("ROWBACKGROUNDS", (0,1), (-1,-1), [HexColor("#f5f5f5"), HexColor("#ffffff")])]))
        c.append(tbl)
        c.append(Spacer(1, 0.5*cm))
    if analise.get("evidencias_ouro"):
        c.append(Paragraph("<b>Evidencias para OURO</b>", destaque))
        for e in analise["evidencias_ouro"]: c.append(Paragraph("- " + e, corpo))
        c.append(Spacer(1, 0.3*cm))
    if analise.get("evidencias_etr"):
        c.append(Paragraph("<b>Evidencias para TERRAS RARAS</b>", destaque))
        for e in analise["evidencias_etr"]: c.append(Paragraph("- " + e, corpo))
        c.append(Spacer(1, 0.3*cm))
    c.append(PageBreak())
    c.append(Paragraph("Proximos Passos Recomendados", subtitulo))
    passos = ["1. Verificar no SIGMINE se a area esta livre.", "2. Confirmar tipo de rocha no GeoSGB.", "3. Se aluviao: detector de metais nas margens de rios.", "4. Se rocha dura: amostragem sistematica.", "5. Enviar amostras para laboratorio (Au e ETR).", "6. Contratar engenheiro de minas para o REPEM.", "7. Emitir ART no CREA.", "8. Pagar emolumentos e protocolar no REPEM."]
    for p in passos:
        c.append(Paragraph(p, corpo)); c.append(Spacer(1, 0.15*cm))
    c.append(Spacer(1, 1.5*cm))
    c.append(Paragraph("Assinaturas", subtitulo))
    c.append(Spacer(1, 0.5*cm))
    ass = [["Tecnico Responsavel", "Solicitante"], ["_________________________", "_________________________"], ["Nome:", "Nome:"], ["CREA:", "CPF:"], ["ART:", "Data:"]]
    ta = Table(ass, colWidths=[8*cm, 8*cm])
    ta.setStyle(TableStyle([("ALIGN", (0,0), (-1,-1), "CENTER"), ("FONTSIZE", (0,0), (-1,-1), 10), ("VALIGN", (0,0), (-1,-1), "TOP")]))
    c.append(ta)
    doc.build(c)
    return caminho
