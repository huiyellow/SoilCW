#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: v3.10.9.2-39-gcf065ee5

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import SoilCW
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import sip



class SoilCW_gui(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "SoilCW_gui")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.burst_len = burst_len = 2**13
        self.tx_gain = tx_gain = 30
        self.samp_rate = samp_rate = 2e6
        self.rx_gain = rx_gain = 20
        self.ref_gain = ref_gain = 20
        self.recv_len = recv_len = burst_len+256
        self.pulse_amp = pulse_amp = 1
        self.num_drops = num_drops = 2**10
        self.main_freq = main_freq = 2.4e9
        self.delta_f = delta_f = 40e6
        self.cw_freq = cw_freq = 100e3

        ##################################################
        # Blocks
        ##################################################

        self.scan_once = _scan_once_toggle_button = qtgui.MsgPushButton('scan_once', '',1,"default","default")
        self.scan_once = _scan_once_toggle_button

        self.top_layout.addWidget(_scan_once_toggle_button)
        self.scan_cont = _scan_cont_toggle_button = qtgui.MsgPushButton('scan_cont', '',2,"default","default")
        self.scan_cont = _scan_cont_toggle_button

        self.top_layout.addWidget(_scan_cont_toggle_button)
        self.qtgui_time_sink_x_0_1 = qtgui.time_sink_c(
            (recv_len*3), #size
            samp_rate, #samp_rate
            "", #name
            2, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_1.set_update_time(0.10)
        self.qtgui_time_sink_x_0_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_1.enable_tags(True)
        self.qtgui_time_sink_x_0_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_1.enable_autoscale(False)
        self.qtgui_time_sink_x_0_1.enable_grid(True)
        self.qtgui_time_sink_x_0_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_1.enable_control_panel(False)
        self.qtgui_time_sink_x_0_1.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(4):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_1.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_1.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_1_win = sip.wrapinstance(self.qtgui_time_sink_x_0_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_1_win)
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_f(
            3, #size
            samp_rate, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0.set_y_axis(-4, 4)

        self.qtgui_time_sink_x_0_0.set_y_label('Amp', "")

        self.qtgui_time_sink_x_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            3, #size
            samp_rate, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-4, 4)

        self.qtgui_time_sink_x_0.set_y_label('Phase', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.filter_fft_low_pass_filter_0_0 = filter.fft_filter_ccc(1, firdes.low_pass(1, samp_rate, (cw_freq*1.5), (cw_freq/2), window.WIN_HAMMING, 6.76), 1)
        self.filter_fft_low_pass_filter_0 = filter.fft_filter_ccc(1, firdes.low_pass(1, samp_rate, (cw_freq*1.5), (cw_freq/2), window.WIN_HAMMING, 6.76), 1)
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, recv_len)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, recv_len)
        self.blocks_complex_to_magphase_0 = blocks.complex_to_magphase(1)
        self.SoilCW_soil_cw_radar_cc_0 = SoilCW.soil_cw_radar_cc(int(main_freq), int(delta_f), int(samp_rate), int(rx_gain), int(tx_gain), int(ref_gain), False, pulse_amp, cw_freq, burst_len, recv_len, 10)
        self.SoilCW_ChannelResponseExtractor_0 = SoilCW.ChannelResponseExtractor(recv_len,num_drops, '/home/hui/gr-SoilCW/data')


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.scan_cont, 'pressed'), (self.SoilCW_soil_cw_radar_cc_0, 'scan'))
        self.msg_connect((self.scan_once, 'pressed'), (self.SoilCW_soil_cw_radar_cc_0, 'scan'))
        self.connect((self.SoilCW_ChannelResponseExtractor_0, 0), (self.blocks_complex_to_magphase_0, 0))
        self.connect((self.SoilCW_soil_cw_radar_cc_0, 0), (self.filter_fft_low_pass_filter_0, 0))
        self.connect((self.SoilCW_soil_cw_radar_cc_0, 1), (self.filter_fft_low_pass_filter_0_0, 0))
        self.connect((self.blocks_complex_to_magphase_0, 1), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_complex_to_magphase_0, 0), (self.qtgui_time_sink_x_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.SoilCW_ChannelResponseExtractor_0, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.SoilCW_ChannelResponseExtractor_0, 1))
        self.connect((self.filter_fft_low_pass_filter_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.filter_fft_low_pass_filter_0, 0), (self.qtgui_time_sink_x_0_1, 0))
        self.connect((self.filter_fft_low_pass_filter_0_0, 0), (self.blocks_stream_to_vector_0_0, 0))
        self.connect((self.filter_fft_low_pass_filter_0_0, 0), (self.qtgui_time_sink_x_0_1, 1))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "SoilCW_gui")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_burst_len(self):
        return self.burst_len

    def set_burst_len(self, burst_len):
        self.burst_len = burst_len
        self.set_recv_len(self.burst_len+256)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.filter_fft_low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.cw_freq*1.5), (self.cw_freq/2), window.WIN_HAMMING, 6.76))
        self.filter_fft_low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.cw_freq*1.5), (self.cw_freq/2), window.WIN_HAMMING, 6.76))
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_1.set_samp_rate(self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain

    def get_ref_gain(self):
        return self.ref_gain

    def set_ref_gain(self, ref_gain):
        self.ref_gain = ref_gain

    def get_recv_len(self):
        return self.recv_len

    def set_recv_len(self, recv_len):
        self.recv_len = recv_len

    def get_pulse_amp(self):
        return self.pulse_amp

    def set_pulse_amp(self, pulse_amp):
        self.pulse_amp = pulse_amp

    def get_num_drops(self):
        return self.num_drops

    def set_num_drops(self, num_drops):
        self.num_drops = num_drops

    def get_main_freq(self):
        return self.main_freq

    def set_main_freq(self, main_freq):
        self.main_freq = main_freq

    def get_delta_f(self):
        return self.delta_f

    def set_delta_f(self, delta_f):
        self.delta_f = delta_f

    def get_cw_freq(self):
        return self.cw_freq

    def set_cw_freq(self, cw_freq):
        self.cw_freq = cw_freq
        self.filter_fft_low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.cw_freq*1.5), (self.cw_freq/2), window.WIN_HAMMING, 6.76))
        self.filter_fft_low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, (self.cw_freq*1.5), (self.cw_freq/2), window.WIN_HAMMING, 6.76))




def main(top_block_cls=SoilCW_gui, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
