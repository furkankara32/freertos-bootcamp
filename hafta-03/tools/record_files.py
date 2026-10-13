"""Excel-compatible CSV and rollback-safe replacement of one recording."""
import csv
import io
import tempfile
from pathlib import Path


def csv_bytes(columns, rows):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, delimiter=';')
    writer.writerow(columns)
    for row in rows:
        writer.writerow([str(v).replace('.', ',') if isinstance(v, float) else v for v in row])
    return stream.getvalue().encode('utf-8-sig')


def replace_files(folder, files):
    """Stage first; restore the previous bundle if a file is locked or writing fails."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.record-', dir=folder) as tmp:
        stage = Path(tmp)
        for name, data in files.items():
            if Path(name).name != name:
                raise ValueError('Recording filename must not contain a directory')
            (stage / name).write_bytes(data)
        saved, installed = [], []
        try:
            for name in files:
                target = folder / name
                if target.exists():
                    target.replace(stage / (name + '.previous'))
                    saved.append(name)
            for name in files:
                (stage / name).replace(folder / name)
                installed.append(name)
        except OSError as exc:
            for name in installed:
                (folder / name).unlink()
            for name in saved:
                (stage / (name + '.previous')).replace(folder / name)
            if isinstance(exc, PermissionError):
                raise PermissionError('Kayit dosyasi kullanimda. Excel/SystemView dosyasini kapatip tekrar deneyin; onceki kayit korundu.') from exc
            raise
