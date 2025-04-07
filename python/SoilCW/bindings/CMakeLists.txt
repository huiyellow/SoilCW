# Copyright 2020 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

########################################################################
# Check if there is C++ code at all
########################################################################
if(NOT SoilCW_sources)
    message(STATUS "No C++ sources... skipping python bindings")
    return()
endif(NOT SoilCW_sources)

########################################################################
# Check for pygccxml
########################################################################
gr_python_check_module_raw("pygccxml" "import pygccxml" PYGCCXML_FOUND)

include(GrPybind)

########################################################################
# Python Bindings
########################################################################

list(APPEND SoilCW_python_files
    soil_cw_radar_cc_python.cc python_bindings.cc)

gr_pybind_make_oot(SoilCW ../../.. gr::SoilCW "${SoilCW_python_files}")

# copy bindings extension for use in QA test module
add_custom_command(
    TARGET SoilCW_python
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:SoilCW_python>
            ${PROJECT_BINARY_DIR}/test_modules/gnuradio/SoilCW/)

install(
    TARGETS SoilCW_python
    DESTINATION ${GR_PYTHON_DIR}/gnuradio/SoilCW
    COMPONENT pythonapi)
