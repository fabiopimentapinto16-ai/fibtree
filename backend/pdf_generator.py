"""Gerador de PDF - Olho de Deus (com mapa estatico)"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from datetime import datetime
from PIL import Image
import requests
from io import BytesIO
import math

COR_AZUL_ESCURO = HexColor('#0a4d68')
COR_AZUL_MEDIO = HexColor('#088395')
COR_CINZA_CLARO = HexColor('#f5f5f5')
COR_BRANCO = HexColor('#ffffff')

def gerar_mapa_estatico(lat, lng, zoom=11):
    n = 2 ** zoom
    x_tile = int((lng + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    y_tile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y_tile}/{x_tile}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content))
        caminho = "/tmp/mapa_analise.jpg"
        img.save(caminho, "JPEG")
        return caminho
    except Exception as e:
        print(f"Erro ao baixar mapa: {e}")
        return None

def _tabela_dados(dados, colWidths=None):
    if colWidths is None: colWidths = [8*cm, 8*cm]
    t = Table(dados, colWidths=colWidths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COR_AZUL_ESCURO),
        ('TEXTCOLOR', (0,0), (-1,0), COR_BRANCO),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [COR_CINZA_CLARO, COR_BRANCO]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6)
    ]))
    return t

def gerar_pdf(analise, caminho="relatorio_olho_deus.pdf"):
    doc = SimpleDocTemplate(caminho, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    estilos = getSampleStyleSheet()
    corpo = ParagraphStyle('C', parent=estilos['Normal'], fontSize=11, leading=16)
    destaque = ParagraphStyle('D', parent=corpo, fontSize=13, textColor=COR_AZUL_ESCURO)
    subtitulo = ParagraphStyle('S', parent=estilos['Heading2'], fontSize=14, textColor=COR_AZUL_MEDIO, spaceAfter=10)
    c = []
    c.append(Paragraph("OLHO DE DEUS", ParagraphStyle('T', parent=estilos['Title'], fontSize=22, textColor=COR_AZUL_ESCURO)))
    c.append(Paragraph("Relatorio de Analise Mineral Preliminar", subtitulo))
    c.append(Paragraph(f"<b>Data:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", corpo))
    c.append(Spacer(1, 0.5*cm))
    coord = analise["coordenada"]
    c.append(Paragraph("<b>1. Identificacao da Area</b>", destaque))
    c.append(Paragraph(f"Latitude: {coord['lat']:.6f} | Longitude: {coord['lng']:.6f}", corpo))
    c.append(Paragraph("Sistema de referencia: SIRGAS 2000", corpo))
    c.append(Spacer(1, 0.5*cm))
    c.append(Paragraph("<b>2. Resultado da Analise</b>", destaque))
    icone = "OURO" if analise["tipo_principal"] == "ouro" else "TERRAS RARAS"
    dados = [["Indicador", "Valor"], ["Score Final", f"{analise['score_final']}/100"], ["Classificacao", analise["classificacao"]], ["Tipo Principal", icone], ["Score OURO", f"{analise['score_ouro']}/100"], ["Score TERRAS RARAS", f"{analise['score_etr']}/100"]]
    c.append(_tabela_dados(dados))
    c.append(Spacer(1, 0.5*cm))
    try:
        caminho_mapa = gerar_mapa_estatico(coord["lat"], coord["lng"])
        if caminho_mapa and os.path.exists(caminho_mapa):
            c.append(Paragraph("<b>Mapa da Regiao Analisada</b>", destaque))
            c.append(Spacer(1, 0.3*cm))
            img = RLImage(caminho_mapa, width=16*cm, height=10*cm)
            c.append(img)
            c.append(Spacer(1, 0.5*cm))
    except Exception as e:
        print(f"Erro ao inserir mapa: {e}")
    if analise.get("pontos_proximos"):
        c.append(Paragraph("<b>3. Ocorrencias Minerais no Raio de 15 km</b>", destaque))
        dp = [["Nome", "Tipo", "Distancia", "Acesso"]]
        for p in analise["pontos_proximos"][:10]:
            tipo_str = "Ouro" if p["tipo"] == "ouro" else "ETR"
            dist_str = "DENTRO" if p["dentro"] else f"{p['distancia_km']} km"
            dp.append([p["nome"], tipo_str, dist_str, p["facilidade"]])
        c.append(_tabela_dados(dp, colWidths=[6*cm, 3*cm, 3.5*cm, 3.5*cm]))
        c.append(Spacer(1, 0.5*cm))
    if analise.get("evidencias_ouro"):
        c.append(Paragraph("<b>4. Evidencias para OURO</b>", destaque))
        for e in analise["evidencias_ouro"]: c.append(Paragraph(f"- {e}", corpo))
        c.append(Spacer(1, 0.3*cm))
    if analise.get("evidencias_etr"):
        c.append(Paragraph("<b>5. Evidencias para TERRAS RARAS</b>", destaque))
        for e in analise["evidencias_etr"]: c.append(Paragraph(f"- {e}", corpo))
        c.append(Spacer(1, 0.3*cm))
    if analise.get("dados_satelite"):
        ds = analise["dados_satelite"]
        c.append(Paragraph("<b>6. Indices Espectrais (Satelite)</b>", destaque))
        dados_sat = [["Indice", "Valor"], ["Oxido de Ferro", str(ds.get("oxido_ferro", 0))], ["Carbonato/Argila", str(ds.get("carbonato_argila", 0))], ["Anomalia Radioativa", str(ds.get("anomalia_radioativa", 0))], ["Data da Imagem", ds.get("data_imagem", "-")], ["Resolucao", ds.get("resolucao", "-")]]
        c.append(_tabela_dados(dados_sat))
        c.append(Spacer(1, 0.5*cm))
    c.append(PageBreak())
    c.append(Paragraph("7. Proximos Passos Recomendados", subtitulo))
    passos = ["1. Verificar no SIGMINE se a area esta livre.", "2. Confirmar tipo de rocha no GeoSGB.", "3. Se aluviao: detector de metais nas margens de rios.", "4. Se rocha dura: amostragem sistematica.", "5. Enviar amostras para laboratorio (Au e ETR).", "6. Contratar engenheiro de minas para o REPEM.", "7. Emitir ART no CREA.", "8. Pagar emolumentos e protocolar no REPEM."]
    for p in passos: c.append(Paragraph(p, corpo)); c.append(Spacer(1, 0.15*cm))
    c.append(Spacer(1, 1*cm))
    c.append(Paragraph("8. Assinaturas", subtitulo))
    ass = [["Tecnico Responsavel", "Solicitante"], ["\n\n\n_________________________", "\n\n\n_________________________"], ["Nome: ____________________", "Nome: ____________________"], ["CREA: ____________________", "CPF: _____________________"], ["ART: _____________________", "Data: ____________________"]]
    ta = Table(ass, colWidths=[8*cm, 8*cm])
    ta.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTSIZE', (0,0), (-1,-1), 10), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    c.append(ta)
    c.append(Spacer(1, 0.8*cm))
    c.append(Paragraph("<i>Aviso: Este relatorio e um rascunho gerado por software. Nao substitui a analise de um engenheiro de minas registrado no CREA.</i>", corpo))
    doc.build(c)
    return caminho

def gerar_memorial(analise, caminho="memorial_descritivo.pdf", dados_solicitante=None):
    if dados_solicitante is None: dados_solicitante = {}
    doc = SimpleDocTemplate(caminho, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    estilos = getSampleStyleSheet()
    corpo = ParagraphStyle('C', parent=estilos['Normal'], fontSize=11, leading=16)
    destaque = ParagraphStyle('D', parent=corpo, fontSize=13, textColor=COR_AZUL_ESCURO)
    subtitulo = ParagraphStyle('S', parent=estilos['Heading2'], fontSize=14, textColor=COR_AZUL_MEDIO, spaceAfter=10)
    c = []
    coord = analise["coordenada"]
    lat = coord['lat']; lng = coord['lng']
    c.append(Paragraph("MEMORIAL DESCRITIVO", ParagraphStyle('T', parent=estilos['Title'], fontSize=24, textColor=COR_AZUL_ESCURO, spaceAfter=10)))
    c.append(Paragraph("Requerimento de Pesquisa Mineral", ParagraphStyle('S2', parent=estilos['Heading2'], fontSize=16, textColor=COR_AZUL_MEDIO, spaceAfter=20)))
    c.append(Spacer(1, 1*cm))
    c.append(Paragraph("<b>1. DADOS DO REQUERENTE</b>", destaque))
    dados_req = [["Campo", "Preenchimento"], ["Nome completo / Razao Social", "____________________________________________"], ["CPF / CNPJ", "____________________________________________"], ["Endereco completo", "____________________________________________"], ["Cidade / Estado / CEP", "____________________________________________"], ["Telefone / E-mail", "____________________________________________"], ["Nacionalidade / Profissao", "____________________________________________"], ["Estado civil", "____________________________________________"], ["Documento de identidade", "____________________________________________"]]
    c.append(_tabela_dados(dados_req, colWidths=[6*cm, 10*cm]))
    c.append(Spacer(1, 0.8*cm))
    c.append(Paragraph("<b>2. DADOS DO IMOVEL / AREA</b>", destaque))
    dados_imovel = [["Campo", "Preenchimento"], ["Denominacao da area", "____________________________________________"], ["Municipio", "____________________________________________"], ["Estado (UF)", "____________________________________________"], ["Area total (hectares)", "____________________________________________"], ["Coordenadas geodesicas", f"Lat: {lat:.6f} / Lng: {lng:.6f}"], ["Sistema de referencia", "SIRGAS 2000"], ["Proprietario do solo", "____________________________________________"], ["Tipo de posse", "____________________________________________"]]
    c.append(_tabela_dados(dados_imovel, colWidths=[6*cm, 10*cm]))
    c.append(PageBreak())
    c.append(Paragraph("<b>3. CARACTERIZACAO DA AREA</b>", destaque))
    c.append(Paragraph("A area requerida esta localizada na regiao de coordenadas acima, apresentando as seguintes caracteristicas:", corpo))
    fisio = [["Aspecto", "Descricao"], ["Relevo", "____________________________________________"], ["Vegetacao predominante", "____________________________________________"], ["Clima", "____________________________________________"], ["Hidrografia", "____________________________________________"], ["Acesso a area", "____________________________________________"]]
    c.append(_tabela_dados(fisio, colWidths=[5*cm, 11*cm]))
    c.append(Spacer(1, 0.5*cm))
    icone = "OURO" if analise["tipo_principal"] == "ouro" else "TERRAS RARAS"
    c.append(Paragraph("<b>4. GEOLOGIA REGIONAL</b>", destaque))
    geologia = [["Parametro", "Resultado"], ["Score de potencial", f"{analise['score_final']}/100"], ["Classificacao", analise["classificacao"]], ["Tipo principal", icone], ["Score Ouro", f"{analise['score_ouro']}/100"], ["Score Terras Raras", f"{analise['score_etr']}/100"]]
    c.append(_tabela_dados(geologia, colWidths=[6*cm, 10*cm]))
    c.append(Spacer(1, 0.5*cm))
    if analise.get("pontos_proximos"):
        c.append(Paragraph("<b>5. OCORRENCIAS MINERAIS PROXIMAS</b>", destaque))
        dp = [["Nome", "Tipo", "Distancia", "Acesso"]]
        for p in analise["pontos_proximos"][:15]:
            tipo_str = "Ouro" if p["tipo"] == "ouro" else "ETR"
            dist_str = "DENTRO" if p["dentro"] else f"{p['distancia_km']} km"
            dp.append([p["nome"], tipo_str, dist_str, p["facilidade"]])
        c.append(_tabela_dados(dp, colWidths=[5*cm, 3*cm, 4*cm, 4*cm]))
        c.append(Spacer(1, 0.5*cm))
    c.append(PageBreak())
    c.append(Paragraph("<b>6. METODOLOGIA APLICADA</b>", destaque))
    metodologia = ["1. Obtencao de imagens de satelite da NASA GIBS (MODIS Terra TrueColor, 250m).", "2. Processamento digital para extracao de indices espectrais.", "3. Calculo do indice de oxido de ferro (pista para ouro).", "4. Calculo do indice de carbonato/argila (pista para Terras Raras).", "5. Analise de anomalia radioativa.", "6. Cruzamento com banco de 24 regioes minerais conhecidas.", "7. Cruzamento com dados do SIGMINE/ANM.", "8. Classificacao final do potencial mineral."]
    for m in metodologia: c.append(Paragraph(m, corpo)); c.append(Spacer(1, 0.15*cm))
    c.append(Spacer(1, 0.5*cm))
    c.append(Paragraph("<b>7. CONCLUSAO</b>", destaque))
    conclusao = f"Com base na analise realizada, a area requerida apresenta <b>{analise['classificacao']}</b> para ocorrencia de <b>{icone}</b>, com score final de <b>{analise['score_final']}/100</b>.<br/><br/>Recomenda-se a realizacao de trabalhos de campo complementares."
    c.append(Paragraph(conclusao, corpo))
    c.append(Spacer(1, 1*cm))
    c.append(Paragraph("<b>8. ASSINATURAS</b>", destaque))
    c.append(Spacer(1, 1.5*cm))
    ass = [["_________________________________", "_________________________________"], ["Requerente", "Tecnico Responsavel"], ["Nome: _________________________", "Nome: _________________________"], ["CPF/CNPJ: _____________________", "CREA: _________________________"], ["", "ART: __________________________"]]
    ta = Table(ass, colWidths=[8*cm, 8*cm])
    ta.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTSIZE', (0,0), (-1,-1), 10), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    c.append(ta)
    c.append(Spacer(1, 1*cm))
    c.append(Paragraph("<i>Este memorial descritivo e um documento preliminar. Nao substitui a analise tecnica de um engenheiro de minas registrado no CREA.</i>", corpo))
    doc.build(c)
    return caminho
