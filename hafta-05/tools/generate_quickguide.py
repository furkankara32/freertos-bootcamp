from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'output/pdf/Hafta5_Task_ve_SystemView_Kisa_Rehber.pdf'
out.parent.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('Guide','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('GuideBold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Guide',normal='Guide',bold='GuideBold')
navy=colors.HexColor('#17334A');teal=colors.HexColor('#087F83')
body=ParagraphStyle('Body',fontName='Guide',fontSize=10,leading=14,textColor=navy,spaceAfter=7)
small=ParagraphStyle('Small',parent=body,fontSize=9,leading=12,spaceAfter=0)
head=ParagraphStyle('Head',parent=body,fontName='GuideBold',fontSize=11,leading=15,textColor=teal,spaceBefore=9,spaceAfter=6)
title=ParagraphStyle('Title',parent=body,fontName='GuideBold',fontSize=21,leading=25,spaceAfter=6)
P=lambda s,style=body:Paragraph(s,style)
story=[P('Hafta 5 | Task ve SystemView',title),P('STM32F407G-DISC1 • Deney sırasında bakılacak noktalar',small),Spacer(1,12)]
story.append(P('1 / Oluşturulacak tasklar',head))
rows=[[P('<b>Task / öncelik</b>',small),P('<b>Görevi ve bekleme nedeni</b>',small)],
      [P('<b>ParserTask / 4</b>',small),P('RX StreamBuffer’dan veriyi alır ve parse eder. Komutu CommandQueue’ya koyar; Event Group ile ExecuteTask’ı uyandırır. Veri yokken bloklanır.',small)],
      [P('<b>ExecuteTask / 3</b>',small),P('Komutu yürütür; LED sırasını ve 1000 ms hedeflerini yönetir. Sonucu ResultQueue’ya koyar, ReportTask’a notify verir. Event veya LED zamanı için bekler.',small)],
      [P('<b>ReportTask / 2</b>',small),P('Notify ile uyanır; sonucu 100 baytlık rapora çevirir. TX StreamBuffer üzerinden USART2’ye verir. Normalde TX tamamlanmasını bloklanarak bekler.',small)]]
t=Table(rows,colWidths=[126,385]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E3F0F1')),('BACKGROUND',(0,1),(-1,-1),colors.HexColor('#F5F8FA')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.6,teal)]));story.append(t)
story.append(Spacer(1,7))
story.append(P('<b>Büyük sayı = yüksek öncelik.</b> S2’de ReportTask hata ve kesmeli düzeltmede <b>5</b>, düşük öncelikli polling düzeltmesinde <b>2</b> olur. IDLE task’ını FreeRTOS oluşturur; ayrıca RX/TX task’ı yoktur, UART kesmeleri kullanılır.',small))
story.append(P('2 / SystemView’da senaryo senaryo incele',head))
for label,text in [
 ('S1 - Doğru çalışan referans','10 KB giriş yükünde Parser kısa çalışıp beklemeli; Execute LED zamanında çalışabilmeli. <b>LED late_us</b> düşük, kayıp sayaçları sıfır artışlı olmalı.'),
 ('S2 - Report CPU’yu tutuyor mu?','<b>TX_BEGIN - TX_END</b> aralığına bak. Hatalı polling’de Report uzun Running, Execute ise zamanı geldiğinde Ready kalır. Düşük öncelik veya kesmeli TX ile Execute gecikmesi azalmalı.'),
 ('S3 - Parser diğer task’ı geciktiriyor mu?','<b>WORK_BEGIN - WORK_END</b> aralığını incele. Kesintisiz iş Execute’ı geciktirir. Parçalı işte Parser gerçekten Blocked olmalı ve aralarda Execute çalışmalı; yalnız yield yeterli değildir.'),
 ('S4 - Event ile Queue aynı şey değil','<b>EVENT ve EXECUTE</b> olaylarını karşılaştır. Event biti tekrarları saymaz. UART durumunda Queue doluyken Execute’ın beklemesi hatadır. Düzeltmede bekleyen tüm komutlar sırayla tüketilmeli.')]:
    story.append(P('<b>'+label+'</b><br/>'+text))
story.append(P('3 / Yanlış yorumlamamak için',head))
story.append(P('<b>Ready:</b> çalışmaya hazır, CPU bekliyor. <b>Blocked:</b> veri/event/notify/zaman bekliyor; tek başına hata değildir.<br/><b>LED süresi ≠ geçiş gecikmesi.</b> Açık kalma süresini arayüz/CSV’den, hedefe göre gecikmeyi <b>late_us</b> alanından karşılaştır.<br/><b>Trace yalnız 1,5 saniyedir.</b> Hata tetiklemesi bu pencereye sığmalı. Kaydı bitir, ST-LINK ile çıkar, aynı <b>run_id</b> ve <b>COMPLETE</b> durumunu doğrula. COMPLETE, deadline geçti demek değildir.',small))
story.append(Spacer(1,7))
story.append(P('Bu sürümde UART bayt başına ISR ve ayrıntılı FreeRTOS API izleri filtrelidir. Queue derinliği ve kayıp sayaçlarını arayüz/STATUS ile birlikte incele. Yeni başarılı kayıt, aynı senaryonun önceki kaydını değiştirir.',small))
def footer(c,doc):
    c.setStrokeColor(teal);c.line(42,36,553,36);c.setFont('Guide',8);c.setFillColor(navy)
    c.drawString(42,23,'Hafta 05 • Mevcut uygulama için kısa inceleme rehberi • 25.10.2026')
    c.drawRightString(553,23,str(doc.page))
doc=SimpleDocTemplate(str(out),pagesize=(595.28,841.89),rightMargin=42,leftMargin=42,topMargin=32,bottomMargin=48)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(out)
