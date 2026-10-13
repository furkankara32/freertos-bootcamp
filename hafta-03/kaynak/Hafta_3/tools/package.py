"""Build a shareable package without local flash backups or IDE caches."""
from pathlib import Path
import zipfile,json,hashlib
root=Path(__file__).resolve().parents[1]
skip_dirs={'.cube-workspace','.cube-workspace-native','.metadata','build','Debug','Release','__pycache__','superseded'}
dest=root/'Hafta_3_Ders_Paketi.zip'
manifest={}
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(root.rglob('*')):
        if not p.is_file() or p==dest:continue
        rel=p.relative_to(root)
        if any(x in skip_dirs for x in rel.parts) or p.name.startswith('flash_before_'):continue
        if p.suffix in {'.pyc','.zip'}:continue
        z.write(p,str(Path('Hafta_3')/rel))
        if rel.parts[0] in {'assets','docs','interface'} or rel.as_posix().startswith('firmware/src/'):
            manifest[rel.as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    z.writestr('Hafta_3/package-manifest.json',json.dumps(manifest,indent=2))
print(dest, dest.stat().st_size, 'bytes')
