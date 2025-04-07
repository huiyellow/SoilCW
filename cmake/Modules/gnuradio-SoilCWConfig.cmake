find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_SOILCW gnuradio-SoilCW)

FIND_PATH(
    GR_SOILCW_INCLUDE_DIRS
    NAMES gnuradio/SoilCW/api.h
    HINTS $ENV{SOILCW_DIR}/include
        ${PC_SOILCW_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_SOILCW_LIBRARIES
    NAMES gnuradio-SoilCW
    HINTS $ENV{SOILCW_DIR}/lib
        ${PC_SOILCW_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-SoilCWTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_SOILCW DEFAULT_MSG GR_SOILCW_LIBRARIES GR_SOILCW_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_SOILCW_LIBRARIES GR_SOILCW_INCLUDE_DIRS)
