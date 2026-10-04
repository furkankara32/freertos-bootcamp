"""Production C state-flow tests on a host fake HAL/RTOS, not timing evidence."""
import shutil,subprocess
from pathlib import Path
import pytest
from interface.src.protocol import Protocol,Decoder

ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('profile,variant',[(1,'Q'),(2,'QW'),(3,'QB'),(4,'QWB')])
def test_production_firmware_queues_and_protocol(tmp_path,profile,variant):
    gcc=shutil.which('gcc')
    if not gcc:pytest.skip('Native GCC required for production C harness')
    exe=tmp_path/'harness.exe';wire=tmp_path/'wire.bin'
    subprocess.run([gcc,'-std=c11','-Wall','-Wextra',f'-DAPP_PROFILE={profile}',
        '-I'+str(ROOT/'tests/native/stubs'),'-I'+str(ROOT/'firmware/Homework_001/Inc'),
        str(ROOT/'tests/native/firmware_harness.c'),'-o',str(exe)],check=True,capture_output=True,text=True)
    subprocess.run([str(exe),str(wire)],check=True,capture_output=True,text=True,timeout=10)
    decoder=Decoder();parser=Protocol();dump=None
    for raw in decoder.feed(wire.read_bytes()):
        kind,data=parser.accept(raw)
        if kind=='DUMP':dump=data
    assert not decoder.errors and dump is not None
    assert dump.metadata['variant']==variant and dump.protocol=='PROTO3'
    assert dump.counters['ok']==1 and dump.counters['late_10ms']==0
