"""Gerador de PDF - Olho de Deus (Relatorio + Memorial Descritivo)"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from datetime import datetime

COR_AZUL_ESCURO = HexColor('#0a4d68')
COR_AZUL_MEDIO = HexColor('#088395')
COR_CINZA_CLARO = HexColor('#f5f5f5')
COR_BRANCO = HexColor('#ffffff')
COR_VERDE = HexColor('#00ff88')
COR_AMARELO = HexColor('#ffcc00')
COR_VERMELHO = HexColor('#ff3355')

def _cabecalho(estilos):
    """Retorna os elementos do cabecalho padrao"""
    titulo = ParagraphStyle('T', parent=estilos['Title'], fontSize=22, textColor=COR_AZUL_ESCURO, spaceAfter=6)
    subtitulo = ParagraphStyle('S', parent=estilos['Heading2'], fontSize=14, textColor=COR_AZUL_MEDIO, spaceAfter=10)
    return [
        Paragraph("OLHO DE DEUS", titulo),
        Paragraph("Sistema de Analise Mineral Preliminar", subtitulo),
        Paragraph(f"<b>Data de emissao:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilos['Normal']),
        Spacer(1, 0.5*cm)
    ]

def _tabela_dados(dados, colWidths=None):
    """Cria uma tabela formatada com estilo padrao"""
    if colWidths is None:
        colWidths = [8*cm, 8*cm]
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
    
    # === CABECALHO ===
    c.extend(_cabecalho(estilos))
    
    # === COORDENADA ===
    coord = analise["coordenada"]
    c.append(Paragraph("<b>1. Identificacao da Area</b>", destaque))
    c.append(Paragraph(f"Latitude: {coord['lat']:.6f} | Longitude: {coord['lng']:.6f}", corpo))
    c.append(Paragraph("Sistema de referencia: SIRGAS 2000", corpo))
    c.append(Paragraph(f"Raio de analise: {analise.get('raio_analisado_km', 15)} km", corpo))
    c.append(Spacer(1, 0.5*cm))
    
    # === RESULTADO ===
    c.append(Paragraph("<b>2. Resultado da Analise</b>", destaque))
    c.append(Spacer(1, 0.3*cm))
    icone = "OURO" if analise["tipo_principal"] == "ouro" else "TERRAS RARAS"
    dados = [
        ["Indicador", "Valor"],
        ["Score Final", f"{analise['score_final']}/100"],
        ["Classificacao", analise["classificacao"]],
        ["Tipo Principal", icone],
        ["Score OURO", f"{analise['score_ouro']}/100"],
        ["Score TERRAS RARAS", f"{analise['score_etr']}/100"]
    ]
    c.append(_tabela_dados(dados))
    c.append(Spacer(1, 0.5*cm))
    
    # === PONTOS PROXIMOS ===
    if analise.get("pontos_proximos"):
        c.append(Paragraph("<b>3. Ocorrencias Minerais no Raio de 15 km</b>", destaque))
        c.append(Spacer(1, 0.3*cm))
        dp = [["Nome", "Tipo", "Distancia", "Acesso"]]
        for p in analise["pontos_proximos"][:10]:
            tipo_str = "Ouro" if p["tipo"] == "ouro" else "ETR"
            dist_str = "DENTRO" if p["dentro"] else f"{p['distancia_km']} km"
            dp.append([p["nome"], tipo_str, dist_str, p["facilidade"]])
        c.append(_tabela_dados(dp, colWidths=[6*cm, 3*cm, 3.5*cm, 3.5*cm]))
        c.append(Spacer(1, 0.5*cm))
    
    # === EVIDENCIAS ===
    if analise.get("evidencias_ouro"):
        c.append(Paragraph("<b>4. Evidencias para OURO</b>", destaque))
        for e in analise["evidencias_ouro"]:
            c.append(Paragraph(f"- {e}", corpo))
        c.append(Spacer(1, 0.3*cm))
    
    if analise.get("evidencias_etr"):
        c.append(Paragraph("<b>5. Evidencias para TERRAS RARAS</b>", destaque))
        for e in analise["evidencias_etr"]:
            c.append(Paragraph(f"- {e}", corpo))
        c.append(Spacer(1, 0.3*cm))
    
    # === DADOS DE SATELITE ===
    if analise.get("dados_satelite"):
        ds = analise["dados_satelite"]
        c.append(Paragraph("<b>6. Indices Espectrais (Satelite)</b>", destaque))
        c.append(Spacer(1, 0.2*cm))
        dados_sat = [
            ["Indice", "Valor"],
            ["Oxido de Ferro", str(ds.get("oxido_ferro", 0))],
            ["Carbonato/Argila", str(ds.get("carbonato_argila", 0))],
            ["Anomalia Radioativa", str(ds.get("anomalia_radioativa", 0))],
            ["Data da Imagem", ds.get("data_imagem", "-")],
            ["Resolucao", ds.get("resolucao", "-")]
        ]
        c.append(_tabela_dados(dados_sat))
        c.append(Spacer(1, 0.5*cm))
    
    # === PROXIMOS PASSOS ===
    c.append(PageBreak())
    c.append(Paragraph("7. Proximos Passos Recomendados", subtitulo))
    passos = [
        "1. Verificar no SIGMINE se a area esta livre.",
        "2. Confirmar tipo de rocha no GeoSGB.",
        "3. Se aluviao: detector de metais nas margens de rios.",
        "4. Se rocha dura: amostragem sistematica.",
        "5. Enviar amostras para laboratorio (Au e ETR).",
        "6. Contratar engenheiro de minas para o REPEM.",
        "7. Emitir ART no CREA.",
        "8. Pagar emolumentos e protocolar no REPEM."
    ]
    for p in passos:
        c.append(Paragraph(p, corpo))
        c.append(Spacer(1, 0.15*cm))
    
    c.append(Spacer(1, 1*cm))
    c.append(Paragraph("8. Assinaturas", subtitulo))
    c.append(Spacer(1, 0.5*cm))
    ass = [
        ["Tecnico Responsavel", "Solicitante"],
        ["\n\n\n_________________________", "\n\n\n_________________________"],
        ["Nome: ____________________", "Nome: ____________________"],
        ["CREA: ____________________", "CPF: _____________________"],
        ["ART: _____________________", "Data: ____________________"]
    ]
    ta = Table(ass, colWidths=[8*cm, 8*cm])
    ta.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    c.append(ta)
    c.append(Spacer(1, 0.8*cm))
    c.append(Paragraph("<i>Aviso: Este relatorio e um rascunho gerado por software. Nao substitui a analise de um engenheiro de minas registrado no CREA. Nao protocola automaticamente no REPEM/ANM.</i>", corpo))
    
    doc.build(c)
    return caminho


def gerar_memorial(analise, caminho="memorial_descritivo.pdf", dados_solicitante=None):
    """
    Gera um Memorial Descritivo completo conforme exigencias da ANM/REPEM.
    O solicitante precisa preencher manualmente os dados pessoais.
    """
    if dados_solicitante is None:
        dados_solicitante = {}
    
    doc = SimpleDocTemplate(caminho, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    estilos = getSampleStyleSheet()
    corpo = ParagraphStyle('C', parent=estilos['Normal'], fontSize=11, leading=16)
    destaque = ParagraphStyle('D', parent=corpo, fontSize=13, textColor=COR_AZUL_ESCURO)
    subtitulo = ParagraphStyle('S', parent=estilos['Heading2'], fontSize=14, textColor=COR_AZUL_MEDIO, spaceAfter=10)
    c = []
    
    coord = analise["coordenada"]
    lat = coord['lat']
    lng = coord['lng']
    
    # === CAPA ===
    c.append(Paragraph("MEMORIAL DESCRITIVO", ParagraphStyle('T', parent=estilos['Title'], fontSize=24, textColor=COR_AZUL_ESCURO, spaceAfter=10)))
    c.append(Paragraph("Requerimento de Pesquisa Mineral", ParagraphStyle('S2', parent=estilos['Heading2'], fontSize=16, textColor=COR_AZUL_MEDIO, spaceAfter=20)))
    c.append(Spacer(1, 2*cm))
    
    # === DADOS DO REQUERENTE (para preencher) ===
    c.append(Paragraph("<b>1. DADOS DO REQUERENTE</b>", destaque))
    c.append(Spacer(1, 0.3*cm))
    dados_req = [
        ["Campo", "Preenchimento"],
        ["Nome completo / Razão Social", "____________________________________________"],
        ["CPF / CNPJ", "____________________________________________"],
        ["Endereço completo", "____________________________________________"],
        ["Cidade / Estado / CEP", "____________________________________________"],
        ["Telefone / E-mail", "____________________________________________"],
        ["Nacionalidade", "____________________________________________"],
        ["Profissão", "____________________________________________"],
        ["Estado civil", "____________________________________________"],
        ["Documento de identidade", "____________________________________________"]
    ]
    c.append(_tabela_dados(dados_req, colWidths=[6*cm, 10*cm]))
    c.append(Spacer(1, 0.8*cm))
    
    # === DADOS DO IMÓVEL ===
    c.append(Paragraph("<b>2. DADOS DO IMOVEL / AREA</b>", destaque))
    c.append(Spacer(1, 0.3*cm))
    dados_imovel = [
        ["Campo", "Preenchimento"],
        ["Denominação da área", "____________________________________________"],
        ["Município", "____________________________________________"],
        ["Estado (UF)", "____________________________________________"],
        ["Área total (hectares)", "____________________________________________"],
        ["Coordenadas geodésicas", f"Lat: {lat:.6f} / Lng: {lng:.6f}"],
        ["Sistema de referência", "SIRGAS 2000"],
        ["Proprietário do solo", "____________________________________________"],
        ["Tipo de posse", "____________________________________________"]
    ]
    c.append(_tabela_dados(dados_imovel, colWidths=[6*cm, 10*cm]))
    c.append(Spacer(1, 0.8*cm))
    
    # === CARACTERIZACAO DA AREA ===
    c.append(PageBreak())
    c.append(Paragraph("<b>3. CARACTERIZACAO DA AREA</b>", destaque))
    c.append(Spacer(1, 0.3*cm))
    c.append(Paragraph("<b>3.1. Aspectos fisiograficos</b>", subtitulo))
    c.append(Paragraph("A área requerida está localizada na região de coordenadas acima especificadas, apresentando as seguintes características fisiográficas:", corpo))
    c.append(Spacer(1, 0.3*cm))
    fisio = [
        ["Aspecto", "Descrição"],
        ["Relevo", "____________________________________________"],
        ["Vegetação predominante", "____________________________________________"],
        ["Clima", "____________________________________________"],
        ["Hidrografia", "____________________________________________"],
        ["Acesso à área", "____________________________________________"]
    ]
    c.append(_tabela_dados(fisio, colWidths=[5*cm, 11*cm]))
    c.append(Spacer(1, 0.8*cm))
    
    # === GEOLOGIA ===
    c.append(Paragraph("<b>3.2. Geologia regional e local</b>", subtitulo))
    c.append(Paragraph("Com base na análise de imagens de satélite (NASA GIBS/MODIS) e no cruzamento com o banco de ocorrências minerais conhecidas, a área apresenta:", corpo))
    c.append(Spacer(1, 0.3*cm))
    
    icone = "OURO" if analise["tipo_principal"] == "ouro" else "TERRAS RARAS"
    geologia = [
        ["Parâmetro", "Resultado"],
        ["Score de potencial", f"{analise['score_final']}/100"],
        ["Classificação", analise["classificacao"]],
        ["Tipo principal", icone],
        ["Score Ouro", f"{analise['score_ouro']}/100"],
        ["Score Terras Raras", f"{analise['score_etr']}/100"],
        ["Óxido de Ferro (satélite)", str(analise.get('dados_satelite', {}).get('oxido_ferro', 'Não disponível'))],
        ["Carbonato/Argila (satélite)", str(analise.get('dados_satelite', {}).get('carbonato_argila', 'Não disponível'))],
        ["Anomalia Radioativa", str(analise.get('dados_satelite', {}).get('anomalia_radioativa', 'Não disponível'))]
    ]
    c.append(_tabela_dados(geologia, colWidths=[6*cm, 10*cm]))
    c.append(Spacer(1, 0.5*cm))
    
    # === OCORRENCIAS PROXIMAS ===
    if analise.get("pontos_proximos"):
        c.append(Paragraph("<b>3.3. Ocorrências minerais no raio de 15 km</b>", subtitulo))
        c.append(Paragraph("Foram identificadas as seguintes ocorrências minerais conhecidas próximas à área requerida:", corpo))
        c.append(Spacer(1, 0.3*cm))
        dp = [["Nome", "Tipo", "Distância", "Acesso"]]
        for p in analise["pontos_proximos"][:15]:
            tipo_str = "Ouro" if p["tipo"] == "ouro" else "ETR"
            dist_str = "DENTRO" if p["dentro"] else f"{p['distancia_km']} km"
            dp.append([p["nome"], tipo_str, dist_str, p["facilidade"]])
        c.append(_tabela_dados(dp, colWidths=[5*cm, 3*cm, 4*cm, 4*cm]))
        c.append(Spacer(1, 0.5*cm))
    
    # === METODOLOGIA ===
    c.append(PageBreak())
    c.append(Paragraph("<b>4. METODOLOGIA APLICADA</b>", destaque))
    c.append(Spacer(1, 0.3*cm))
    c.append(Paragraph("A análise foi realizada através do sistema OLHO DE DEUS, que utiliza as seguintes etapas:", corpo))
    c.append(Spacer(1, 0.2*cm))
    metodologia = [
        "1. Obtenção de imagens de satélite da NASA GIBS (MODIS Terra TrueColor, resolução 250m).",
        "2. Processamento digital das imagens para extração de índices espectrais.",
        "3. Cálculo do índice de óxido de ferro (pista para depósitos auríferos).",
        "4. Cálculo do índice de carbonato/argila (pista para depósitos de Terras Raras).",
        "5. Análise de anomalia radioativa (indicador complementar).",
        "6. Cruzamento com banco de 24 regiões minerais conhecidas do Brasil.",
        "7. Cálculo de score de potencial com base na distância e tipo de ocorrência.",
        "8. Classificação final do potencial mineral."
    ]
    for m in metodologia:
        c.append(Paragraph(m, corpo))
        c.append(Spacer(1, 0.15*cm))
    c.append(Spacer(1, 0.5*cm))
    
    # === CONCLUSÃO ===
    c.append(Paragraph("<b>5. CONCLUSÃO</b>", destaque))
    c.append(Spacer(1, 0.3*cm))
    conclusao = f"""
    Com base na análise realizada, a área requerida apresenta <b>{analise['classificacao']}</b> 
    para ocorrência de <b>{icone}</b>, com score final de <b>{analise['score_final']}/100</b>.
    <br/><br/>
    Recomenda-se a realização de trabalhos de campo complementares, incluindo:
    <br/>- Levantamento geológico de detalhe;
    <br/>- Amostragem sistemática de solo e rocha;
    <br/>- Análise laboratorial para Au, ETR e elementos associados;
    <br/>- Levantamento geofísico (se aplicável).
    """
    c.append(Paragraph(conclusao, corpo))
    c.append(Spacer(1, 1*cm))
    
    # === ASSINATURAS ===
    c.append(Paragraph("<b>6. ASSINATURAS</b>", destaque))
    c.append(Spacer(1, 1.5*cm))
    ass = [
        ["_________________________________", "_________________________________"],
        ["Requerente", "Técnico Responsável"],
        ["Nome: _________________________", "Nome: _________________________"],
        ["CPF/CNPJ: _____________________", "CREA: _________________________"],
        ["", "ART: __________________________"]
    ]
    ta = Table(ass, colWidths=[8*cm, 8*cm])
    ta.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    c.append(ta)
    c.append(Spacer(1, 1*cm))
    
    # === RODAPE LEGAL ===
    c.append(Paragraph("<i>Este memorial descritivo é um documento preliminar gerado automaticamente pelo sistema OLHO DE DEUS. Não substitui a análise técnica de um engenheiro de minas registrado no CREA. O preenchimento dos dados pessoais e a conferência das informações são de responsabilidade do requerente. Este documento não protocola automaticamente no REPEM/ANM.</i>", corpo))
    
    doc.build(c)
    return caminho
