"""Gerador de PDF - Grãos de Ouro"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from datetime import datetime
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import math

try:
    import qrcode
    QR_CODE_DISPONIVEL = True
except ImportError:
    QR_CODE_DISPONIVEL = False

COR_AZUL_ESCURO = HexColor('#0a4d68')
COR_AZUL_MEDIO = HexColor('#088395')
COR_CINZA_CLARO = HexColor('#f5f5f5')
COR_BRANCO = HexColor('#ffffff')



def gerar_mapa_com_ponto_interesse(lat, lng, ponto_interesse, pontos_sigmine=None, caminho="/tmp/mapa_pi.jpg", zoom=12):
    """Gera mapa com o Ponto de Interesse destacado em dourado."""
    try:
        n = 2 ** zoom
        x_tile = int((lng + 180.0) / 360.0 * n)
        lat_rad = math.radians(lat)
        y_tile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y_tile}/{x_tile}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert("RGB")
        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        # Função auxiliar para converter lat/lng em pixel
        fator = 256 * (2 ** zoom) / 360.0
        def latlng_para_pixel(p_lat, p_lng):
            px = (p_lng - lng) * fator + w/2
            py = -(p_lat - lat) * fator + h/2
            return (px, py)
        
        # Marcador do ponto analisado (azul)
        px, py = latlng_para_pixel(lat, lng)
        draw.ellipse([px-8, py-8, px+8, py+8], fill="blue", outline="white", width=2)
        draw.text((px+12, py-10), "Ponto analisado", fill="white")
        
        # Marcador do Ponto de Interesse (dourado)
        if ponto_interesse:
            pi_lat = ponto_interesse.get("lat")
            pi_lng = ponto_interesse.get("lng")
            if pi_lat and pi_lng:
                px_pi, py_pi = latlng_para_pixel(pi_lat, pi_lng)
                cor_pi = "gold" if ponto_interesse.get("tipo") == "ouro" else "cyan"
                draw.ellipse([px_pi-12, py_pi-12, px_pi+12, py_pi+12], fill=cor_pi, outline="white", width=3)
                draw.text((px_pi+15, py_pi-10), "PONTO DE INTERESSE", fill="white")
        
        # Marcadores dos processos SIGMINE (verde)
        if pontos_sigmine:
            for p in pontos_sigmine[:20]:
                try:
                    px_s, py_s = latlng_para_pixel(p["lat"], p["lng"])
                    if 0 <= px_s <= w and 0 <= py_s <= h:
                        draw.ellipse([px_s-3, py_s-3, px_s+3, py_s+3], fill="green", outline="white", width=1)
                except Exception:
                    pass
        
        img.save(caminho, "JPEG", quality=85)
        return caminho
    except Exception as e:
        print(f"Erro ao gerar mapa PI: {e}")
        return None

def gerar_mapa_com_marcadores(lat, lng, pontos_proximos=None, pontos_sigmine=None, caminho="/tmp/mapa_marcadores.jpg", zoom=11):
    """Baixa o tile do Esri e desenha circulos nos pontos de interesse."""
    try:
        n = 2 ** zoom
        x_tile = int((lng + 180.0) / 360.0 * n)
        lat_rad = math.radians(lat)
        y_tile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y_tile}/{x_tile}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert("RGB")
        draw = ImageDraw.Draw(img)
        w, h = img.size

        # Marcador central (azul)
        draw.ellipse([w/2-8, h/2-8, w/2+8, h/2+8], fill="blue", outline="white", width=2)

        # Converte lat/lng para pixel no tile (aproximacao)
        def latlng_para_pixel(p_lat, p_lng):
            # Fator de escala: quanto cada grau ocupa em pixels nesse zoom
            fator = 256 * (2 ** zoom) / 360.0
            px = (p_lng - lng) * fator + w/2
            py = -(p_lat - lat) * fator + h/2
            return (px, py)

        if pontos_proximos:
            for p in pontos_proximos[:15]:
                try:
                    cor = "orange" if p.get("tipo") == "ouro" else "cyan"
                    px, py = latlng_para_pixel(p["lat"], p["lng"])
                    if 0 <= px <= w and 0 <= py <= h:
                        draw.ellipse([px-5, py-5, px+5, py+5], fill=cor, outline="white", width=1)
                except Exception:
                    pass

        if pontos_sigmine:
            for p in pontos_sigmine[:20]:
                try:
                    px, py = latlng_para_pixel(p["lat"], p["lng"])
                    if 0 <= px <= w and 0 <= py <= h:
                        draw.ellipse([px-3, py-3, px+3, py+3], fill="green", outline="white", width=1)
                except Exception:
                    pass

        img.save(caminho, "JPEG", quality=85)
        return caminho
    except Exception as e:
        print(f"Erro ao gerar mapa com marcadores: {e}")
        return None

def gerar_qr_code(lat, lng, caminho="/tmp/qrcode.png"):
    if not QR_CODE_DISPONIVEL:
        return None
    try:
        url = f"https://earth.google.com/web/@{lat},{lng},1000a,1000d,35y,0h,0t,0r"
        img = qrcode.make(url)
        img.save(caminho)
        return caminho
    except Exception as e:
        print(f"Erro QR: {e}")
        return None



def gerar_mapa_area_provavel(lat, lng, ponto_interesse=None, raio_km=5, caminho="/tmp/mapa_area_provavel.jpg", zoom=12):
    """Gera mapa com a area provavel destacada (circulo + poligono) e porcentagem."""
    try:
        n = 2 ** zoom
        x_tile = int((lng + 180.0) / 360.0 * n)
        lat_rad = math.radians(lat)
        y_tile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        url = f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y_tile}/{x_tile}"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert("RGB")
        draw = ImageDraw.Draw(img)
        w, h = img.size

        # Fator de escala
        fator = 256 * (2 ** zoom) / 360.0
        def latlng_para_pixel(p_lat, p_lng):
            px = (p_lng - lng) * fator + w/2
            py = -(p_lat - lat) * fator + h/2
            return (px, py)

        # Se tem ponto de interesse, calcular distancia
        if ponto_interesse:
            pi_lat = ponto_interesse.get("lat", lat)
            pi_lng = ponto_interesse.get("lng", lng)
            px_pi, py_pi = latlng_para_pixel(pi_lat, pi_lng)
            
            # Desenhar circulo de area provavel ao redor do PI
            raio_pixels = int(raio_km * 1000 / 111.32 * fator / (2 ** zoom) * (2 ** zoom))
            raio_pixels = int(raio_km * fator / 111.32)
            
            # Circulo externo (area provavel)
            draw.ellipse([px_pi - raio_pixels, py_pi - raio_pixels, 
                         px_pi + raio_pixels, py_pi + raio_pixels], 
                         outline="gold", width=4)
            
            # Circulo interno (nucleo)
            raio_nucleo = max(10, raio_pixels // 3)
            draw.ellipse([px_pi - raio_nucleo, py_pi - raio_nucleo,
                         px_pi + raio_nucleo, py_pi + raio_nucleo],
                         fill="gold", outline="white", width=3)
            
            # Marcador do PI (estrela/asterisco)
            draw.ellipse([px_pi - 6, py_pi - 6, px_pi + 6, py_pi + 6], 
                        fill="red", outline="white", width=2)
            
            # Score em texto
            score = ponto_interesse.get("score", 0)
            draw.text((px_pi + 15, py_pi - 15), f"{score}%", fill="gold")

        # Marcador do ponto analisado
        px, py = latlng_para_pixel(lat, lng)
        draw.ellipse([px - 10, py - 10, px + 10, py + 10], 
                    outline="blue", width=3)
        draw.ellipse([px - 5, py - 5, px + 5, py + 5], 
                    fill="blue", outline="white", width=2)

        # Bussola
        draw.text((w - 30, 15), "N", fill="white")
        draw.line([(w - 25, 35), (w - 25, 55)], fill="white", width=2)
        draw.polygon([(w - 25, 30), (w - 30, 40), (w - 20, 40)], fill="white")

        img.save(caminho, "JPEG", quality=90)
        return caminho
    except Exception as e:
        print(f"Erro ao gerar mapa area provavel: {e}")
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

def gerar_pdf(analise, caminho="relatorio_graos_de_ouro.pdf"):
    doc = SimpleDocTemplate(caminho, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    estilos = getSampleStyleSheet()
    corpo = ParagraphStyle('C', parent=estilos['Normal'], fontSize=11, leading=16)
    destaque = ParagraphStyle('D', parent=corpo, fontSize=13, textColor=COR_AZUL_ESCURO)
    subtitulo = ParagraphStyle('S', parent=estilos['Heading2'], fontSize=14, textColor=COR_AZUL_MEDIO, spaceAfter=10)
    c = []
    c.append(Paragraph("GRAOS DE OURO", ParagraphStyle('T', parent=estilos['Title'], fontSize=22, textColor=COR_AZUL_ESCURO)))
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

    # MAPA COM MARCADORES
    try:
        caminho_mapa = gerar_mapa_com_marcadores(
            coord["lat"], coord["lng"],
            analise.get("pontos_proximos"),
            analise.get("pontos_sigmine")
        )
        if caminho_mapa and os.path.exists(caminho_mapa):
            c.append(Paragraph("<b>Mapa com Pontos de Interesse</b>", destaque))
            c.append(Paragraph("<i>Azul: ponto analisado | Laranja: ouro | Ciano: ETR | Verde: SIGMINE</i>", corpo))
            c.append(Spacer(1, 0.3*cm))
            c.append(RLImage(caminho_mapa, width=16*cm, height=10*cm))
            c.append(Spacer(1, 0.5*cm))
    except Exception as e:
        print(f"Erro mapa: {e}")

    if analise.get("pontos_proximos"):
        c.append(Paragraph("<b>3. Ocorrencias Minerais no Raio de 15 km</b>", destaque))
        dp = [["Nome", "Tipo", "Distancia", "Acesso"]]
        for p in analise["pontos_proximos"][:10]:
            tipo_str = "Ouro" if p["tipo"] == "ouro" else "ETR"
            dist_str = "DENTRO" if p["dentro"] else f"{p['distancia_km']} km"
            dp.append([p["nome"], tipo_str, dist_str, p["facilidade"]])
        c.append(_tabela_dados(dp, colWidths=[6*cm, 3*cm, 3.5*cm, 3.5*cm]))
        c.append(Spacer(1, 0.5*cm))

    # LISTA SIGMINE
    if analise.get("pontos_sigmine"):
        c.append(Paragraph("<b>4. Processos Minerarios (SIGMINE) no Raio de 15 km</b>", destaque))
        c.append(Spacer(1, 0.2*cm))
        dados_sig = [["Processo", "Substancia", "Fase", "Distancia (km)"]]
        for p in analise["pontos_sigmine"][:15]:
            dados_sig.append([
                str(p.get("processo", "-"))[:20],
                str(p.get("subs", "-"))[:20],
                str(p.get("fase", "-"))[:25],
                str(p.get("distancia_km", "-"))
            ])
        c.append(_tabela_dados(dados_sig, colWidths=[4*cm, 4*cm, 5*cm, 3*cm]))
        c.append(Spacer(1, 0.5*cm))

    if analise.get("evidencias_ouro"):
        c.append(Paragraph("<b>5. Evidencias para OURO</b>", destaque))
        for e in analise["evidencias_ouro"]: c.append(Paragraph(f"- {e}", corpo))
        c.append(Spacer(1, 0.3*cm))
    if analise.get("evidencias_etr"):
        c.append(Paragraph("<b>6. Evidencias para TERRAS RARAS</b>", destaque))
        for e in analise["evidencias_etr"]: c.append(Paragraph(f"- {e}", corpo))
        c.append(Spacer(1, 0.3*cm))
    if analise.get("dados_satelite"):
        ds = analise["dados_satelite"]
        c.append(Paragraph("<b>7. Indices Espectrais (Satelite)</b>", destaque))
        dados_sat = [["Indice", "Valor"], ["Oxido de Ferro", str(ds.get("oxido_ferro", 0))], ["Carbonato/Argila", str(ds.get("carbonato_argila", 0))], ["Anomalia Radioativa", str(ds.get("anomalia_radioativa", 0))], ["Data da Imagem", ds.get("data_imagem", "-")], ["Resolucao", ds.get("resolucao", "-")]]
        c.append(_tabela_dados(dados_sat))
        c.append(Spacer(1, 0.5*cm))

    # QR CODE
    try:
        caminho_qr = gerar_qr_code(coord["lat"], coord["lng"])
        if caminho_qr and os.path.exists(caminho_qr):
            c.append(Paragraph("<b>8. Escaneie para abrir no Google Earth:</b>", destaque))
            c.append(Spacer(1, 0.2*cm))
            c.append(RLImage(caminho_qr, width=4*cm, height=4*cm))
            c.append(Spacer(1, 0.5*cm))
    except Exception as e:
        print(f"Erro QR: {e}")


    # === PONTO DE INTERESSE ===
    if analise.get("ponto_interesse"):
        pi = analise["ponto_interesse"]
        c.append(PageBreak())
        c.append(Paragraph("PONTO DE INTERESSE CALCULADO", ParagraphStyle('T2', parent=estilos['Title'], fontSize=18, textColor=HexColor('#b8860b'))))
        c.append(Paragraph("Local de maior potencial identificado pela analise", subtitulo))
        c.append(Spacer(1, 0.5*cm))
        
        # Mapa com o Ponto de Interesse
        try:
            caminho_mapa_pi = gerar_mapa_com_ponto_interesse(
                coord["lat"], coord["lng"],
                pi,
                analise.get("pontos_sigmine")
            )
            if caminho_mapa_pi and os.path.exists(caminho_mapa_pi):
                c.append(Paragraph("<b>Mapa com Ponto de Interesse Destacado</b>", destaque))
                c.append(Paragraph("<i>Azul: ponto analisado | Dourado: ponto de interesse | Verde: SIGMINE</i>", corpo))
                c.append(Spacer(1, 0.3*cm))
                c.append(RLImage(caminho_mapa_pi, width=16*cm, height=10*cm))
                c.append(Spacer(1, 0.5*cm))
        except Exception as e:
            print(f"Erro mapa PI: {e}")
        
        # Tabela com as informações do Ponto de Interesse
        dados_pi = [
            ["Parametro", "Valor"],
            ["Coordenada", f"Lat: {pi['lat']:.6f} | Lng: {pi['lng']:.6f}"],
            ["Score no Ponto", f"{pi.get('score', 0)}/100"],
            ["Tipo Principal", pi.get('tipo', 'ouro').upper()],
            ["Motivo", pi.get('motivo', 'Nao informado')],
            ["Distancia do ponto analisado", f"{pi.get('distancia_km', 0)} km"],
        ]
        c.append(_tabela_dados(dados_pi, colWidths=[6*cm, 10*cm]))
        c.append(Spacer(1, 0.5*cm))
        
        # Aviso e instruções
        c.append(Paragraph("<b>Como usar este ponto:</b>", destaque))
        instrucoes = [
            "1. Este e o local de MAIOR POTENCIAL identificado pela analise.",
            "2. Use as coordenadas acima para navegar ate o local (GPS).",
            "3. Verifique no SIGMINE se a area esta livre para requerimento.",
            "4. Confirme o tipo de rocha no GeoSGB.",
            "5. Faca amostragem no local para confirmar a existencia de minerio.",
            "6. Se confirmado, protocole o requerimento no REPEM/ANM.",
        ]
        for inst in instrucoes:
            c.append(Paragraph(inst, corpo))
            c.append(Spacer(1, 0.15*cm))
        c.append(Spacer(1, 0.5*cm))

    c.append(PageBreak())
    c.append(Paragraph("9. Proximos Passos Recomendados", subtitulo))
    passos = ["1. Verificar no SIGMINE se a area esta livre.", "2. Confirmar tipo de rocha no GeoSGB.", "3. Se aluviao: detector de metais nas margens de rios.", "4. Se rocha dura: amostragem sistematica.", "5. Enviar amostras para laboratorio (Au e ETR).", "6. Contratar engenheiro de minas para o REPEM.", "7. Emitir ART no CREA.", "8. Pagar emolumentos e protocolar no REPEM."]
    for p in passos: c.append(Paragraph(p, corpo)); c.append(Spacer(1, 0.15*cm))
    c.append(Spacer(1, 1*cm))
    c.append(Paragraph("10. Assinaturas", subtitulo))
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
    fisio = [["Aspecto", "Descricao"], ["Relevo", "____________________________________________"], ["Vegetacao predominante", "____________________________________________"], ["Clima", "____________________________________________"], ["Hidrografia", "____________________________________________"], ["Acesso a area", "____________________________________________"]]
    c.append(_tabela_dados(fisio, colWidths=[5*cm, 11*cm]))
    c.append(Spacer(1, 0.5*cm))
    icone = "OURO" if analise["tipo_principal"] == "ouro" else "TERRAS RARAS"
    c.append(Paragraph("<b>4. GEOLOGIA REGIONAL</b>", destaque))
    geologia = [["Parametro", "Resultado"], ["Score de potencial", f"{analise['score_final']}/100"], ["Classificacao", analise["classificacao"]], ["Tipo principal", icone], ["Score Ouro", f"{analise['score_ouro']}/100"], ["Score Terras Raras", f"{analise['score_etr']}/100"]]
    c.append(_tabela_dados(geologia, colWidths=[6*cm, 10*cm]))
    c.append(PageBreak())
    c.append(Paragraph("<b>5. CONCLUSAO</b>", destaque))
    conclusao = f"Com base na analise realizada, a area requerida apresenta <b>{analise['classificacao']}</b> para ocorrencia de <b>{icone}</b>, com score final de <b>{analise['score_final']}/100</b>."
    c.append(Paragraph(conclusao, corpo))
    c.append(Spacer(1, 1*cm))
    c.append(Paragraph("<b>6. ASSINATURAS</b>", destaque))
    c.append(Spacer(1, 1.5*cm))
    ass = [["_________________________________", "_________________________________"], ["Requerente", "Tecnico Responsavel"], ["Nome: _________________________", "Nome: _________________________"], ["CPF/CNPJ: _____________________", "CREA: _________________________"], ["", "ART: __________________________"]]
    ta = Table(ass, colWidths=[8*cm, 8*cm])
    ta.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTSIZE', (0,0), (-1,-1), 10), ('VALIGN', (0,0), (-1,-1), 'TOP')]))
    c.append(ta)
    c.append(Spacer(1, 1*cm))
    c.append(Paragraph("<i>Este memorial descritivo e um documento preliminar.</i>", corpo))
    doc.build(c)
    return caminho
