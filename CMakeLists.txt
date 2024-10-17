# ==================================================================
#   F I N I T E   E L E M E N T   A N A L Y S I S   P R O G R A M
#             FEAPpv (P e r s o n a l   V e r s i o n)
#
#          FEAPpv(C) Regents of the University of California
#                        All Rights Reserved.
# ==================================================================

cmake_minimum_required(VERSION 3.16)

project(FEAPPV 
  VERSION 0.0.0
  LANGUAGES Fortran C
  DESCRIPTION 
  "FEAPpv -- free personal version of the FEAP (A Finite Element Analysis Program)"
)

add_compile_options(
  -ggdb
  -Og
  -g
  -Wall             # enable a large number of warnings
  -Wextra           # enable additional warnings (good practice)
# -pedantic   
# -fimplicit-none   # turn off default implicit typing
 
# -fcheck=all  
  -fbacktrace
) 

include_directories(include)

add_subdirectory(elements)
add_subdirectory(program)
add_subdirectory(user)
add_subdirectory(plot)
add_subdirectory(fe2)
# add_subdirectory(iga)

if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
  add_subdirectory(windows)
else()
  add_subdirectory(unix)
endif()



add_executable(feappv main/feappv.f)
install(TARGETS feappv DESTINATION ${CMAKE_INSTALL_PREFIX})

#
find_package(BLAS REQUIRED)
find_package(LAPACK REQUIRED)

target_link_libraries(feappv
  PRIVATE
    FEAP_Program
    FEAP_Elements
    FEAP_Plot
    FEAP_OperatingSystem
    FEAP_User
    LAPACK::LAPACK
    BLAS::BLAS
)

