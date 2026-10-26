"""Render the reviewed Markdown report; record hashes of its local evidence."""
from pathlib import Path
import hashlib,json,re
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
pdfmetrics.registerFont(TTFont('Report','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ReportBold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Report',normal='Report',bold='ReportBold')
navy=colors.HexColor('#18364B');teal=colors.HexColor('#087F83')
styles={
 'body':ParagraphStyle('body',fontName='Report',fontSize=9.5,leading=13,spaceAfter=7,textColor=navy),
 'title':ParagraphStyle('title',fontName='ReportBold',fontSize=21,leading=25,spaceAfter=10,textColor=navy),
 'head':ParagraphStyle('head',fontName='ReportBold',fontSize=12,leading=15,spaceBefore=9,spaceAfter=6,textColor=teal),
 'cell':ParagraphStyle('cell',fontName='Report',fontSize=9,leading=12,textColor=navy)}
def markup(text):
    return re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',escape(text)).replace('`','')
def p(text,kind='body'):return Paragraph(markup(text),styles[kind])
story=[]
for block in (ROOT/'reports/Hafta5_Rapor.md').read_text(encoding='utf-8').split('\n\n'):
    block=block.strip()
    if not block:continue
    if block=='<!-- pagebreak -->':story.append(PageBreak())
    elif block.startswith('# '):story.append(p(block[2:],'title'))
    elif block.startswith('## '):story.append(p(block[3:],'head'))
    elif block.startswith('|'):
        rows=[[c.strip() for c in line.strip('|').split('|')] for line in block.splitlines()]
        rows=[rows[0]]+rows[2:]
        n=len(rows[0]);widths={3:[80,75,356],4:[245,76,95,95],5:[105,140,75,105,86]}[n]
        table=Table([[p(('**'+c+'**') if i==0 else c,'cell') for c in row] for i,row in enumerate(rows)],colWidths=widths,repeatRows=1)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E3F0F1')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#F5F8FA'),colors.white]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        story.extend([table,Spacer(1,8)])
    else:story.append(p(block.replace('\n',' ')))
def footer(c,doc):
    c.setStrokeColor(teal);c.line(42,37,553,37);c.setFont('Report',8);c.setFillColor(navy)
    c.drawString(42,24,'Hafta 05 | Deney ve doğrulama raporu | 26.10.2026');c.drawRightString(553,24,str(doc.page))
out=ROOT/'reports/Hafta5_Rapor.pdf'
SimpleDocTemplate(str(out),pagesize=(595.28,841.89),leftMargin=42,rightMargin=42,topMargin=34,bottomMargin=49,title='Hafta 5 - FreeRTOS deney raporu',author='FreeRTOS Bootcamp').build(story,onFirstPage=footer,onLaterPages=footer)
files=[]
for scenario in range(1,5):files.extend(p for p in (ROOT/f'records/S{scenario}').rglob('*') if p.is_file())
files.extend(ROOT/'docs'/n for n in ['regression-results.json','protocol-stress.json','interface-smoke.json'])
manifest={'report_date':'2026-10-26','files':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}}
(ROOT/'reports/evidence-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(out)
