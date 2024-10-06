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
  # to "enable all the warnings about constructions that some users consider
  # questionable, and that are easy to avoid (or modify to prevent the
  # warning), even in conjunction with macros."
  -Wall 

  # to "enable some extra warning flags that are not enabled by -Wall."
  -Wextra 

  # to generate warnings about language features that are supported by gfortran
  # but are not part of the official Fortran 95 standard. It possible to be
  # even more "pedantic" and use -std=f95 flag for warnings to become errors.
  #-pedantic 
  
  # to "specify that no implicit typing is allowed, unless overridden by
  # explicit IMPLICIT statements. This is the equivalent of adding implicit
  # none to the start of every procedure."
  #-fimplicit-none 
  
  # to "enable run-time tests", such as, for instance, array bounds checks.
# -fcheck=all 
  
  # when a runtime error is encountered or a deadly signal is emitted
  # (segmentation fault, illegal instruction, bus error or floating-point
  # exception), the Fortran runtime library should output a backtrace of the error."
  -fbacktrace
) 

include_directories(include)

add_subdirectory(elements)
add_subdirectory(program)
add_subdirectory(user)
add_subdirectory(plot)
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

