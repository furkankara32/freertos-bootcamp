from pathlib import Path
import markdown,html
root=Path(__file__).resolve().parents[1]
for path in (root/'docs').glob('*.md'):
    body=markdown.markdown(path.read_text(encoding='utf-8'),extensions=['tables','fenced_code'])
    body=body.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    path.with_suffix('.html').write_text('<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(path.stem)+'</title><link rel="stylesheet" href="../assets/style.css"><style>main{max-width:1100px}h2{margin-top:40px}h1{font-size:42px}li{margin:8px 0}pre{margin:20px 0}table{margin:20px 0}img{max-width:100%}code{overflow-wrap:anywhere}</style></head><body><header><a href="../index.html">HAFTA 03 / İÇERİK MERKEZİ</a><span>KURULUM VE DOĞRULAMA</span></header><main>'+body+'</main></body></html>',encoding='utf-8')
