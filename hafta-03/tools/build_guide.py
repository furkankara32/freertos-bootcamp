from pathlib import Path
import re, html
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
for name, file in [('Regular','arial.ttf'),('Bold','arialbd.ttf'),('Mono','consola.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/'+file))
pdfmetrics.registerFontFamily('Regular', normal='Regular', bold='Bold', italic='Regular', boldItalic='Bold')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyTR',fontName='Regular',fontSize=10,leading=14.4,spaceAfter=7,textColor=colors.HexColor('#253247')))
styles.add(ParagraphStyle(name='TitleTR',fontName='Bold',fontSize=24,leading=29,spaceAfter=15,textColor=colors.HexColor('#102C4A')))
styles.add(ParagraphStyle(name='SubTR',fontName='Bold',fontSize=14,leading=19,spaceAfter=11,textColor=colors.HexColor('#147D83')))
styles.add(ParagraphStyle(name='HeadTR',fontName='Bold',fontSize=11.5,leading=16,spaceBefore=8,spaceAfter=6,textColor=colors.HexColor('#102C4A'),keepWithNext=True))
styles.add(ParagraphStyle(name='CellTR',fontName='Regular',fontSize=9,leading=12,spaceAfter=0))
styles.add(ParagraphStyle(name='CodeTR',fontName='Mono',fontSize=8.7,leading=12,spaceAfter=9,backColor=colors.HexColor('#EEF3F7'),borderPadding=9))

def inline(s):
    s=html.escape(s)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<link href="\2" color="#147D83"><u>\1</u></link>',s)
    s=re.sub(r'`([^`]+)`',r'<font name="Mono">\1</font>',s)
    return s

def footer(c,doc):
    w,h=doc.pagesize
    c.setStrokeColor(colors.HexColor('#D2DFE9'));c.line(44,43,w-44,43)
    c.setFont('Regular',8);c.setFillColor(colors.HexColor('#67798A'))
    c.drawString(44,29,'FREERTOS BOOTCAMP  /  HAFTA 03  /  ÇALIŞMA REHBERİ')
    c.drawRightString(w-44,29,str(doc.page))
    c.setFillColor(colors.HexColor('#147D83'));c.rect(0,h-9,w,9,fill=1,stroke=0)

text=(ROOT/'docs/konu_anlatimi.md').read_text(encoding='utf-8')
story=[]
for pi,page in enumerate(text.split('---PAGE---')):
    if pi: story.append(PageBreak())
    lines=page.strip().splitlines(); i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line: i+=1;continue
        if line.startswith('```'):
            block=[];i+=1
            while i<len(lines) and not lines[i].startswith('```'):
                block.append(lines[i]);i+=1
            story.append(Preformatted('\n'.join(block),styles['CodeTR']));i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[x.strip() for x in lines[i].strip('|').split('|')]
                if not all(re.fullmatch('[-: ]+',c) for c in cells): rows.append([Paragraph(inline(c),styles['CellTR']) for c in cells])
                i+=1
            n=len(rows[0]);widths=([150,357] if n==2 else [170,226,111])
            t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DAE9ED')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,-1),0.4,colors.HexColor('#D8E2E9'))]))
            story.extend([t,Spacer(1,12)]);continue
        if line.startswith('### '):style='HeadTR';line=line[4:]
        elif line.startswith('## '):style='SubTR';line=line[3:]
        elif line.startswith('# '):style='TitleTR';line=line[2:]
        else:style='BodyTR'
        if line.startswith('- '):line='• '+line[2:]
        if line.startswith('> '):line=line[2:]
        story.append(Paragraph(inline(line),styles[style]));i+=1

output=ROOT/'Hafta_03_Konu_Anlatimi.pdf'
doc=SimpleDocTemplate(str(output),pagesize=(595.28,841.89),rightMargin=44,leftMargin=44,topMargin=35,bottomMargin=55,title='FreeRTOS Hafta 03 - Queue Konu Anlatımı',author='Furkan için hazırlanmış çalışma rehberi')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
reader=PdfReader(output)
print('PDF:',output,'Pages:',len(reader.pages))
for i,p in enumerate(reader.pages,1):
    text=p.extract_text()
    print(i,len(text),text.splitlines()[2:4])

