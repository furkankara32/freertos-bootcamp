import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import unittest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QCloseEvent
from interface.main import Window


class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def setUp(self):
        self.w=Window();self.w.timer.stop()
    def tearDown(self):
        self.w.recording=False;self.w.trace_busy=False;self.w.close();self.w.deleteLater()
    def test_close_during_record_or_capture_is_refused(self):
        for state in ('recording','trace_busy'):
            setattr(self.w,state,True);event=QCloseEvent();self.w.closeEvent(event)
            self.assertFalse(event.isAccepted());setattr(self.w,state,False)
    def test_controls_expose_exactly_four_scenarios(self):
        self.assertEqual(self.w.scenario.count(),4)
        for i,n in enumerate((1,3,2,2)):
            self.w.scenario.setCurrentIndex(i);self.assertEqual(self.w.variant.count(),n)
    def test_trigger_outside_record_does_not_transmit(self):
        with patch.object(self.w.session,'send') as send:
            for i in range(4):self.w.scenario.setCurrentIndex(i);self.w.trigger()
            send.assert_not_called()
    def test_saved_record_cannot_be_overwritten_by_manual_capture(self):
        from pathlib import Path
        self.w.last_folder=Path('records/S1');self.w.capture()
        self.assertFalse(self.w.trace_busy)
