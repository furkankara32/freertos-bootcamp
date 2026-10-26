"""One completed recording per scenario; promote only verified captures."""
import json
import shutil
import uuid
from pathlib import Path


def new_record(root, scenario):
    if scenario not in range(1, 5):
        raise ValueError('Geçersiz senaryo')
    folder = Path(root).resolve() / '.pending' / f'S{scenario}_{uuid.uuid4().hex}'
    folder.mkdir(parents=True)
    return folder


def publish(folder):
    folder = Path(folder).resolve()
    if folder.parent.name != '.pending':
        raise ValueError('Yalnız geçici koşu yayımlanabilir')
    root = folder.parent.parent
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    scenario = manifest['scenario']
    if scenario not in range(1, 5) or manifest['capture_status'] != 'COMPLETE':
        raise ValueError('Tam ve eşleşen trace olmadan önceki kayıt değiştirilmez')
    trace = manifest['trace']
    if (trace['run_id'], trace['scenario'], trace['variant']) != (manifest['run_id'], scenario, manifest['variant']):
        raise ValueError('Trace koşu kimliği eşleşmiyor')
    if not trace['complete_window'] or (folder / 'systemview/trace.SVDat').stat().st_size != trace['size']:
        raise ValueError('Trace eksik veya boyutu hatalı')
    target = root / f'S{scenario}'
    backup = root / f'.S{scenario}.previous'
    # All paths are fixed children of the validated records root. Roll back on
    # promotion failure; never remove the previous recording before this point.
    if backup.exists():
        raise RuntimeError(f'Önceki kesintili işlem incelenmeli: {backup}')
    if target.exists():
        target.rename(backup)
    try:
        folder.rename(target)
    except Exception:
        if backup.exists():
            backup.rename(target)
        raise
    if backup.exists():
        shutil.rmtree(backup)
    return target


def complete_capture(folder, metadata):
    folder = Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    matched = (metadata.get('run_id'), metadata.get('scenario'), metadata.get('variant')) == (
        manifest['run_id'], manifest['scenario'], manifest['variant'])
    status = ('COMPLETE' if metadata['complete_window'] else 'PARTIAL') if matched else 'MISMATCH'
    manifest.update(capture_status=status, trace=metadata)
    (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    summary_path = folder / 'summary.json'
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
    summary['trace_status'] = status
    summary_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    if status != 'COMPLETE':
        raise RuntimeError(f'{status}: önceki geçerli kayıt korundu; geçici kayıt: {folder}')
    return publish(folder)
