/* -*- c++ -*- */
/*
 * Copyright 2025 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "soil_cw_radar_cc_impl.h"
#include <gnuradio/io_signature.h>
#include <volk/volk.h>
#include <gnuradio/math.h>
#include "bladerf_device.h"

namespace gr {
namespace SoilCW {

using output_type = gr_complex;
soil_cw_radar_cc::sptr soil_cw_radar_cc::make(bladerf_frequency main_freq,
                                              bladerf_frequency delta_f,
                                              int samp_rate,
                                              bladerf_gain rx_gain,
                                              bladerf_gain tx_gain,
                                              bladerf_gain ref_gain,
                                              bool enable_biastee,
                                              float baseband_amp,
                                              float baseband_freq)
{
    return gnuradio::make_block_sptr<soil_cw_radar_cc_impl>(main_freq,
                                                            delta_f,
                                                            samp_rate,
                                                            rx_gain,
                                                            tx_gain,
                                                            ref_gain,
                                                            enable_biastee,
                                                            baseband_amp,
                                                            baseband_freq);
}


/*
 * The private constructor
 */
soil_cw_radar_cc_impl::soil_cw_radar_cc_impl(bladerf_frequency main_freq,
                                             bladerf_frequency delta_f,
                                             int samp_rate,
                                             bladerf_gain rx_gain,
                                             bladerf_gain tx_gain,
                                             bladerf_gain ref_gain,
                                             bool enable_biastee,
                                             float baseband_amp,
                                             float baseband_freq)
    : gr::sync_block("soil_cw_radar_cc",
                     gr::io_signature::make(0, 0, 0),
                     gr::io_signature::make(
                         NUM_RX_CHANNELS /* min outputs */, NUM_RX_CHANNELS /*max outputs */, sizeof(output_type)))
{
    /**
     * register the message port
     * the module starts sweep the frequencies upon reception of a "scan" message
     * */
    message_port_register_in(pmt::mp("scan"));

    d_samp_rate = samp_rate; 
    d_pulse_amplitude = baseband_amp;
    d_cw_frequency = baseband_freq;

    /**
     * wait 2 ms after frequency tunning
     * */
    d_ts_inc_send = (uint64_t)(d_samp_rate * 2)/1000;

    init_sample_buffers();
    
    /**
     * Initialize device
     */ 
    std::cout << "*************************Initialize device************************" <<std::endl;
    d_scan = false;
    d_continuous_scan_flag = false;

    bladeRF = new BladerfDevice();

    if(bladeRF->openDevice()){
        int status = 0;
        //device opened, configure tx and rx channels
        struct channel_config radar_tx_config;
        radar_tx_config.channel = RADAR_TX;
        radar_tx_config.frequency = main_freq-delta_f;
        radar_tx_config.bandwidth = d_samp_rate/2;
        radar_tx_config.samplerate = d_samp_rate;
        radar_tx_config.gain = tx_gain;

        //channel_config does not have pointer so this create a copy 
        struct channel_config ref_tx_config = radar_tx_config;
        ref_tx_config.channel = REF_TX;
        ref_tx_config.gain = ref_gain;
        
        struct channel_config radar_rx_config = radar_tx_config;
        radar_rx_config.channel = RADAR_RX;
        radar_rx_config.gain = rx_gain;
        //radar_rx_config.gain_mode = BLADERF_GAIN_AUTOMATIC;

        struct channel_config ref_rx_config = radar_tx_config;
        ref_rx_config.channel = REF_RX;
        ref_rx_config.gain = ref_gain;
        //ref_rx_config.gain_mode = BLADERF_GAIN_AUTOMATIC;
        
        /**usb buffer configuration*/
        usb_buffer_config buf_config;
        buf_config.num_buffers = 8;
        buf_config.buffer_size = 2048;
        buf_config.num_transfers = 4;
        status = bladeRF->enable_channels(&radar_tx_config, &radar_rx_config, &ref_tx_config, &ref_rx_config, &buf_config, enable_biastee);
        if(status!=0){
            std::cerr << "Failed to enable rx channels" << std::endl;
            bladeRF->closeDevice();
            return;
        }


        //tx and rx channels all enabled, set quick tune
        frequency_plan_config frequency_plan;
        frequency_plan.start_freq = main_freq - delta_f;
        frequency_plan.num_steps = d_num_steps;
        frequency_plan.step_size = delta_f;
        
        status = bladeRF->set_quick_tune(&frequency_plan);
        if(status!=0){
            std::cerr << "Set quick tune failed" << std::endl;
            bladeRF->closeDevice();
            return;
        }
        std::cout << "Device initialisation completed" << std::endl;
    }else{
        std::cerr << "Failed to open device" << std::endl;
    }
}

void soil_cw_radar_cc_impl::init_sample_buffers(){
    /* Set up constraints */
    int const alignment_multiple = volk_get_alignment() / sizeof(gr_complex);
    set_alignment(std::max(1,alignment_multiple)); 
    
    /* Allocate memory for conversions in work() */
    size_t alignment = volk_get_alignment();
    /**
     * Bladerf accept int16_t as input and output samples in int16_t while gnuradio use 2x float to store one sample 
     * */
    _32fcbuf_in = reinterpret_cast<gr_complex *>(volk_malloc(NUM_TX_CHANNELS*d_burst_len*sizeof(gr_complex), alignment));
    _16icbuf_in = reinterpret_cast<int16_t *>(volk_malloc(2*NUM_TX_CHANNELS*d_burst_len*sizeof(int16_t), alignment));

    _32fcbuf_out = reinterpret_cast<gr_complex *>(volk_malloc(NUM_RX_CHANNELS*d_burst_len*sizeof(gr_complex), alignment));
    _16icbuf_out = reinterpret_cast<int16_t *>(volk_malloc(2*NUM_RX_CHANNELS*d_burst_len*sizeof(int16_t), alignment));
    
    _32fc_samples  = reinterpret_cast<gr_complex *>(volk_malloc(d_burst_len*sizeof(gr_complex), alignment));

    generate_pure_tone_samples();
}

void soil_cw_radar_cc_impl::generate_pure_tone_samples(){
    for (size_t i=0; i<d_burst_len; i++){
        _32fc_samples[i] += d_pulse_amplitude*exp(d_phase);
        d_phase = gr_complex(0,std::fmod(imag(d_phase) + 2 * GR_M_PI * d_cw_frequency / (float)d_samp_rate,2*GR_M_PI));
    }
    for (size_t i=0; i<d_burst_len; i++){
        _32fcbuf_in[2*i] = _32fc_samples[i];
        _32fcbuf_in[2*i + 1] = _32fc_samples[i];
    }
    volk_32f_s32f_convert_16i(_16icbuf_in, reinterpret_cast<float const *>(_32fcbuf_in),
                            SCALING_FACTOR, 2*NUM_TX_CHANNELS*d_burst_len);
}

/*
 * Our virtual destructor.
 */
soil_cw_radar_cc_impl::~soil_cw_radar_cc_impl() {
    volk_free(_16icbuf_in);
    volk_free(_16icbuf_out);
    volk_free(_32fcbuf_in);
    volk_free(_32fcbuf_out);
    _16icbuf_in = NULL;
    _16icbuf_out = NULL;
    _32fcbuf_in = NULL;
    _32fcbuf_out = NULL;
}

int soil_cw_radar_cc_impl::work(int noutput_items,
                                gr_vector_const_void_star& input_items,
                                gr_vector_void_star& output_items)
{
    /**
     * Pointer to output
     * */
    gr_complex **out = reinterpret_cast<gr_complex **>(&output_items[0]);

    if(d_scan == true){
        std::cout << "scanning..." << std::endl;
        //add a new scan tag
        pmt::pmt_t new_scan_tag_key = pmt::string_to_symbol("newScan");
        pmt::pmt_t new_scan_tag_value = pmt::PMT_T;
        add_item_tag(0,nitems_written(0),new_scan_tag_key,new_scan_tag_value);

        //create step tag
        pmt::pmt_t new_freq_tag_key = pmt::string_to_symbol("step");
        // scan cmd received, start sweeping the bandwidth
        for (int i = 0; i < d_num_steps; i++){
            //add a step tag
            pmt::pmt_t new_freq_tag_value = pmt::from_uint64(i);
            add_item_tag(0,nitems_written(0)+i*d_burst_len,new_freq_tag_key,new_freq_tag_value);
            
            /**
             * Tune frequency to the next step
             * */
            bladeRF->tune_tx(i);
            bladeRF->tune_rx(i);
            
            /**
             * Generate pulse samples, the generated samples for two TXs are stored in _32fcbuf_in
             * */
            /*if (d_isChirp){
                //Chirp pulse
                generate_chirp_samples();
            }else{
                //Single tone pulse
                generate_cw_samples();
            }*/
            /** 
             * convert floating point to fixed point and scale
             * input_items is gr_complex (2x float), for 2 TXs, so num_points is 2*2*d_burst_len
             * */
            //volk_32f_s32f_convert_16i(_16icbuf_in, reinterpret_cast<float const *>(_32fcbuf_in),
            //                SCALING_FACTOR, 2*NUM_TX_CHANNELS*d_burst_len);
            
            /**
             * Send a pulse and receive the echo
             * */
            bladeRF->pulse(d_ts_inc_send, d_ts_inc_send, _16icbuf_in, d_burst_len*NUM_TX_CHANNELS, _16icbuf_out, d_burst_len*NUM_RX_CHANNELS);

            /**
            * process received samples
            * */
            volk_16i_s32f_convert_32f(reinterpret_cast<float *>(_32fcbuf_out), _16icbuf_out,
                            SCALING_FACTOR, 2*NUM_RX_CHANNELS*d_burst_len);

            // we need to deinterleave the multiplex as we copy
            gr_complex const *deint_in = _32fcbuf_out;
            //gr_complex const *deint_in = _32fcbuf_in;

            //std::cout << "deinterleave" << std::endl;
            for (size_t i = 0; i < (d_burst_len); ++i) {
                for (size_t n = 0; n < NUM_RX_CHANNELS; ++n) {
                    memcpy(out[n]++, deint_in++, sizeof(gr_complex));
                }
            }
        }
        if(d_continuous_scan_flag == false){
            d_scan = false;
        }
    }else{
        return 0;
    }
    return d_num_steps*d_burst_len;
}

} /* namespace SoilCW */
} /* namespace gr */
