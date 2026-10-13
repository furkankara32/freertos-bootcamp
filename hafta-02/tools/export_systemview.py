"""GUI-only export helper: UART remains owned by SerialWorker."""
import argparse
import json
from pathlib import Path
from capture_v2 import export_trace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--elf', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    trace, info = export_trace(args.elf, args.output)
    print(json.dumps({'trace': str(trace), **info}), flush=True)
    return 0 if info['clean'] and info['capture_complete'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
