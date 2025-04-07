/* -*- c++ -*- */
/*
 * Copyright 2025 SnT.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_SOILCW_SOIL_CW_RADAR_CC_H
#define INCLUDED_SOILCW_SOIL_CW_RADAR_CC_H

#include <gnuradio/SoilCW/api.h>
#include <gnuradio/sync_block.h>
#include <libbladeRF.h>

namespace gr {
namespace SoilCW {

/*!
 * \brief <+description of block+>
 * \ingroup SoilCW
 *
 */
class SOILCW_API soil_cw_radar_cc : virtual public gr::sync_block
{
public:
    typedef std::shared_ptr<soil_cw_radar_cc> sptr;

    /*!
     * \brief Return a shared_ptr to a new instance of SoilCW::soil_cw_radar_cc.
     *
     * To avoid accidental use of raw pointers, SoilCW::soil_cw_radar_cc's
     * constructor is in a private implementation
     * class. SoilCW::soil_cw_radar_cc::make is the public interface for
     * creating new instances.
     */
    static sptr make(bladerf_frequency main_freq,
                     bladerf_frequency delta_f,
                     int samp_rate,
                     bladerf_gain rx_gain,
                     bladerf_gain tx_gain,
                     bladerf_gain ref_gain,
                     bool enable_biastee,
                     float baseband_amp,
                     float baseband_freq);
};

} // namespace SoilCW
} // namespace gr

#endif /* INCLUDED_SOILCW_SOIL_CW_RADAR_CC_H */
