        !COMPILER-GENERATED INTERFACE MODULE: Thu Jan 10 13:21:14 2019
        ! This source file is for reference only and may not completely
        ! represent the generated interface used by the compiler.
        MODULE SHELL3D__genmod
          INTERFACE 
            SUBROUTINE SHELL3D(D,UL,XL,IX,S,P,NDF,NDM,NST,ISW)
              INTEGER(KIND=4) :: NST
              INTEGER(KIND=4) :: NDM
              INTEGER(KIND=4) :: NDF
              REAL(KIND=8) :: D(*)
              REAL(KIND=8) :: UL(NDF,*)
              REAL(KIND=8) :: XL(NDM,*)
              INTEGER(KIND=4) :: IX(*)
              REAL(KIND=8) :: S(NST,*)
              REAL(KIND=8) :: P(NST)
              INTEGER(KIND=4) :: ISW
            END SUBROUTINE SHELL3D
          END INTERFACE 
        END MODULE SHELL3D__genmod
