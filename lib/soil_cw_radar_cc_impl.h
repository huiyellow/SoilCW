/* -*- c++ -*- */
/*
 * Copyright 2025 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SOILCW_SOIL_CW_RADAR_CC_IMPL_H
#define INCLUDED_SOILCW_SOIL_CW_RADAR_CC_IMPL_H
/**
 * Use 2 TXs and 2 RXs
 * */
#define NUM_TX_CHANNELS 2
#define NUM_RX_CHANNELS 2

#define RADAR_TX BLADERF_CHANNEL_TX(0) /**< TX 0 will be used for transmitting radar pulse*/
#define RADAR_RX BLADERF_CHANNEL_RX(0) /**< RX 0 will be used for receiving radar echos*/
#define REF_TX BLADERF_CHANNEL_TX(1) /**< TX 1 will be used for transmitting referece signal*/
#define REF_RX BLADERF_CHANNEL_RX(1) /**< RX 1 will be used for receiving reference signal*/

#include <gnuradio/SoilCW/soil_cw_radar_cc.h>
#include <libbladeRF.h>
#include "bladerf_device.h"

namespace gr {
namespace SoilCW {

class soil_cw_radar_cc_impl : public soil_cw_radar_cc
{
private:
    /**
     * Pointer to the BladerfDevice instance
     * */
    BladerfDevice *bladeRF;
    const unsigned int timeout_ms = 2000;

    /**
     * Parameters of baseband pulses
     * */
    float d_pulse_amplitude;
    float d_cw_frequency;
    gr_complex d_phase = 0;
    size_t d_burst_len;
    size_t d_recv_len;

    /**
     * sampling rate in Hz
     * */
    int d_samp_rate;

    /**
     * number of frequencies
     * */
    const unsigned int d_num_steps = 3;

    /**
     * FPGA time steps to wait for transmission after frequency tunning finished (ms)
     * */
    uint64_t d_ts_inc_send;

    /**
     * Change these flags upon reception of messages
     * d_scan = true && d_continuous_scan_flag = true. scan continousely
     * d_scan = true && d_continuous_scan_flag = false. scan only once
     * otherwise standby
     * */
    bool d_scan = false;
    bool d_continuous_scan_flag = false;
    
    int16_t *_16icbuf_in;              /**< raw samples to bladeRF */
    gr_complex *_32fcbuf_in;           /**< buffer to store generated samples for transmission */ 
    
    int16_t *_16icbuf_out;              /**< raw samples from bladeRF */
    gr_complex *_32fcbuf_out;           /**< buffer to store raw samples in 32 float*/

    gr_complex *_32fc_samples;          /**< buffer to store pulse samples in 32 float, the size is equal to d_burst_len*sizeof(gr_complex)*/
    
    /* Scaling factor used when converting from int16_t to float */
    const float SCALING_FACTOR = 2048.0f; 
    
    /**
     * set d_scan to true when a "scan" message is received
     * */
    void handle_scan_msg(const pmt::pmt_t& msg);
    
    /**
     * Initialise _16icbuf_in, _32fcbuf_in, _16icbuf_out, _32fcbuf_out and _32fc_samples
     * The size of _16icbuf_in: 2 * NUM_TX_CHANNELS * d_burst_len * sizeof(int16_t)
     * The size of _16icbuf_out: 2 * NUM_TX_CHANNELS * d_burst_len * sizeof(int16_t)
     * The size of _32fcbuf_in: NUM_TX_CHANNELS * d_burst_len * sizeof(gr_complex)
     * The size of _32fcbuf_out: NUM_TX_CHANNELS * d_burst_len * sizeof(gr_complex)
     * The size of _32fc_samples: d_burst_len * sizeof(gr_complex)
     * Then pulse samples are generated and stored to _32fc_samples, based on the choice of waveform
     * @see fill_tx_buffer() is called after that
     *
     * */
    void init_sample_buffers();
    
    /**
     * Generate single tone samples, and store them to _32fc_samples
     * The samples to be transmitted via the two TX channels are interleaved
     * */
    void generate_pure_tone_samples();


public:
    /**
     * Class Constructor.
     * The jobs include:
     * 1. Initialise sample buffers @see init_sample_buffers()
     * 2. Create an instance of BladerfDevice, and set it to use two TX and two RXs, one pair for radar channel, one pair for reference channel
     * 3. Provide frequency plan to the device to enable quick tune functionality
     * @param main_freq         The main frequency of the radar in Hz
     * @param delta_f           The frequency difference in Hz
     * @param samp_rate         Sampling rate in Hz
     * @param rx_gain           The gain of the radar RX channel
     * @param tx_gain           The gain of the radar TX channel
     * @param ref_gain          The gain of the reference TX and RX channel
     * @param enable_biastee    Set the flag if BT-100 and BT-200 are connected with radar TX and radar RX channels
     * @param baseband_amp      The amplitude of the baseband pulse
     * @param baseband_freq     The frequency of the baseband pulse
     * @burst_len               Number of samples per pulse to Send
     * @recv_len                Number of samples to receive at each frequency step, better to be larger than burst_len
     * @t_inc_send_ms           Time to wait in ms for sending pulse and receiving echo at each frequency step
     * */
    soil_cw_radar_cc_impl(bladerf_frequency main_freq,
                          bladerf_frequency delta_f,
                          int samp_rate,
                          bladerf_gain rx_gain,
                          bladerf_gain tx_gain,
                          bladerf_gain ref_gain,
                          bool enable_biastee,
                          float baseband_amp,
                          float baseband_freq,
                          size_t burst_len,
                          size_t recv_len,
                          float t_inc_send_ms);
    ~soil_cw_radar_cc_impl();

    // Where all the action really happens
    int work(int noutput_items,
             gr_vector_const_void_star& input_items,
             gr_vector_void_star& output_items);
};

} // namespace SoilCW
} // namespace gr

#endif /* INCLUDED_SOILCW_SOIL_CW_RADAR_CC_IMPL_H */
