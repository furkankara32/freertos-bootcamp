import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import hardware


class ExtractTests(unittest.TestCase):
    def test_swd_failure_attempts_resume(self):
        keys=['app_trace_data','app_trace_bytes','app_trace_dropped','app_trace_complete','app_trace_reason','run_id','scenario','variant']
        with tempfile.TemporaryDirectory() as folder,patch.object(hardware,'symbols',return_value=dict.fromkeys(keys,0x20000000)),patch.object(hardware,'openocd',side_effect=[RuntimeError('probe lost'),'resumed']) as oc:
            with self.assertRaisesRegex(RuntimeError,'probe lost'):hardware.extract_trace(Path(folder))
            self.assertEqual(oc.call_args_list[-1].args[0],'init; halt; resume; shutdown')
