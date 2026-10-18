import io
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
bp_requerimentos = Blueprint("requerimentos", __name__)
@bp_requerimentos.route("/api/requerimento-completo", methods=["POST"])
def requerimento_completo():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    d=request.get_json(silent=True) or {}
    req=d.get("requerimento") or {}; coord=d.get("coordenada") or {}; pi=d.get("ponto_interesse") or {}
    st=getSampleStyleSheet()
    st.add(ParagraphStyle(name="Sub",parent=st["Normal"],textColor=colors.HexColor("#555"),fontSize=9))
    st.add(ParagraphStyle(name="Aviso",parent=st["Normal"],textColor=colors.HexColor("#C73E1D"),backColor=colors.HexColor("#FFF3E0"),borderPadding=6,fontSize=8,leading=11))
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=2*cm,rightMargin=2*cm,topMargin=2*cm,bottomMargin=2*cm)
    L=[]
    L.append(Paragraph("MINUTA DE REQUERIMENTO",st["Title"]))
    L.append(Paragraph(req.get("tipo_nome","Requerimento"),st["Heading2"]))
    L.append(Paragraph(f"Emitido em {datetime.now():%d/%m/%Y}",st["Sub"])); L.append(Spacer(1,14))
    dados=[["Requerente",req.get("nome","____________")],["CPF / CNPJ",req.get("cpf","____________")],["Substância",str(req.get("substancia","OURO")).upper()],["Área",f'{req.get("area_ha","____")} ha'],["Coordenada",f'{coord.get("lat","—")}, {coord.get("lng","—")}']]
    t=Table(dados,colWidths=[5*cm,10*cm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),colors.HexColor("#EFEFEF")),("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#999")),("FONTSIZE",(0,0),(-1,-1),10),("PADDING",(0,0),(-1,-1),6)]))
    L.append(t); L.append(Spacer(1,16))
    L.append(Paragraph("<b>1. Objeto</b>",st["Heading3"]))
    L.append(Paragraph(f'Requerimento de <b>{req.get("tipo_nome","")}</b> para <b>{str(req.get("substancia","OURO")).upper()}</b>.',st["Normal"]))
    L.append(Spacer(1,14))
    L.append(Paragraph("⚠️ Minuta automática. Protocolo oficial no ANM Digital.",st["Aviso"]))
    doc.build(L); buf.seek(0)
    return send_file(buf,as_attachment=True,download_name="requerimento_anm.pdf",mimetype="application/pdf")
