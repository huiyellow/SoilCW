#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2024 SnT.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
import pmt
import json

class ChannelResponseExtractor(gr.sync_block):
    """
    docstring for block ChannelResponseExtractor
    """
    def __init__(self, recv_len, num_drops, dir, f_c, delta_f, d_g, d_m, cable_length, cable_speed_factor):
        gr.sync_block.__init__(self,
            name="ChannelResponseExtractor",
            in_sig=[(np.complex64,recv_len),(np.complex64,recv_len)],
            out_sig=[(np.complex64,1)],
        )

        self.recv_len = recv_len
        self.num_drops = num_drops
        self.current_file = None
        self.fileIndex = 0
        self.dir = dir
        self.scan_param = {
            "main frequency":f_c,
            "delta_f":delta_f,
            "d_g":d_g,
            "d_m":d_m,
            "cable_length":cable_length,
            "cable_speed_factor":cable_speed_factor
        }

        filename = f"{self.dir}/scan_meta.json"
        with open(filename,"w") as f:
            json.dump(self.scan_param, f)
        print("scan parameters: ", self.scan_param)
        print("saved to ", filename)
    
    def fix_iq_imbalance(self, x):
        # remove DC and save input power
        z = x - np.mean(x)
        p_in = np.var(z)

        # scale Q to have unit amplitude (remember we're assuming a single input tone)
        Q_amp = np.sqrt(2*np.mean(x.imag**2))
        z /= Q_amp

        I, Q = z.real, z.imag

        alpha_est = np.sqrt(2*np.mean(I**2))
        sin_phi_est = (2/alpha_est)*np.mean(I*Q)
        cos_phi_est = np.sqrt(1 - sin_phi_est**2)

        I_new_p = (1/alpha_est)*I
        Q_new_p = (-sin_phi_est/alpha_est)*I + Q

        y = (I_new_p + 1j*Q_new_p)/cos_phi_est

        #print ('phase error:', arccos(cos_phi_est)*360/2/pi, 'degrees')
        #print ('amplitude error:', 20*log10(alpha_est), 'dB')

        return y#*np.sqrt(p_in/np.var(y))

    def work(self, input_items, output_items):
        rx_vec = input_items[0]
        ref_vec = input_items[1]
        out_vec = output_items[0]
        
#        print("shape of rx_vec: ", rx_vec.shape)
#        print("shape of ref_vec: ", ref_vec.shape)
        if rx_vec.shape[1] != self.recv_len:
            print(f"Warning: Input vector length ({len(in_vec)}) does not match recv_len")
            return 0  
        
        if self.num_drops >= self.recv_len-self.num_drops:
            print(f"Warning: invalid num_drops {num_drops}")
            return 0  
        
        for i in range(len(rx_vec)):
            tags = self.get_tags_in_window(0, i, i+1) 
            for tag in tags:
                if pmt.to_python(tag.key) == "newScan":
                    print("found newScan")
                    if self.current_file:
                        print("close the current file")
                        self.current_file.close()
                    # create a new file here
                    self.fileIndex = self.fileIndex + 1
                    filename = f"{self.dir}/scan_{self.fileIndex}.dat"
                    self.current_file = open(filename, "wb")
                    print(f"create new file: {filename}")
            rx_samples_fixed = self.fix_iq_imbalance(rx_vec[i])
            ref_samples_fixed = self.fix_iq_imbalance(ref_vec[i])
            channelResponse = rx_samples_fixed[self.num_drops:self.recv_len-self.num_drops]*np.conjugate(ref_samples_fixed[self.num_drops:self.recv_len-self.num_drops])
#channelResponse = rx_vec[i][self.num_drops:self.recv_len-self.num_drops]*np.conjugate(ref_vec[i][self.num_drops:self.recv_len-self.num_drops])
            print("calculated phases of channel response is: ", np.angle(np.mean(channelResponse)))
            out_vec[i] = np.mean(channelResponse)
            if self.current_file:
                # If a file is currently open, write the channelResponse to it
                print(f"write {np.mean(channelResponse)} to {self.current_file}")
                self.current_file.write(np.mean(channelResponse).tobytes())
        return len(output_items[0])
