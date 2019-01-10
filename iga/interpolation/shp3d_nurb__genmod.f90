        !COMPILER-GENERATED INTERFACE MODULE: Thu Jan 10 13:24:06 2019
        ! This source file is for reference only and may not completely
        ! represent the generated interface used by the compiler.
        MODULE SHP3D_NURB__genmod
          INTERFACE 
            SUBROUTINE SHP3D_NURB(SG,XL,WT,SHP,SHPL,XJAC,LKNOT,KTNUM,   &
     &KNOTS,NDM)
              COMMON/ELDATA/ DM,N_EL,MA,MCT,IEL,NEL,PSTYP,ELTYP,ELTY2,  &
     &ELTY3
                REAL(KIND=8) :: DM
                INTEGER(KIND=4) :: N_EL
                INTEGER(KIND=4) :: MA
                INTEGER(KIND=4) :: MCT
                INTEGER(KIND=4) :: IEL
                INTEGER(KIND=4) :: NEL
                INTEGER(KIND=4) :: PSTYP
                INTEGER(KIND=4) :: ELTYP
                INTEGER(KIND=4) :: ELTY2
                INTEGER(KIND=4) :: ELTY3
              COMMON/IGDATA/ DKNOTIG,LKNOTIG,NKNOTIG,DSIDEIG,NSIDEIG,   &
     &DBLOKIG,NBLOKIG,NSTRPIG
                INTEGER(KIND=4) :: DKNOTIG
                INTEGER(KIND=4) :: LKNOTIG
                INTEGER(KIND=4) :: NKNOTIG
                INTEGER(KIND=4) :: DSIDEIG
                INTEGER(KIND=4) :: NSIDEIG
                INTEGER(KIND=4) :: DBLOKIG
                INTEGER(KIND=4) :: NBLOKIG
                INTEGER(KIND=4) :: NSTRPIG
              INTEGER(KIND=4) :: NDM
              REAL(KIND=8) :: SG(3)
              REAL(KIND=8) :: XL(NDM,NEL)
              REAL(KIND=8) :: WT(NEL)
              REAL(KIND=8) :: SHP(4,NEL)
              REAL(KIND=8) :: SHPL(NEL)
              REAL(KIND=8) :: XJAC
              INTEGER(KIND=4) :: LKNOT(0:4,*)
              INTEGER(KIND=4) :: KTNUM(6,*)
              REAL(KIND=8) :: KNOTS(DKNOTIG,*)
            END SUBROUTINE SHP3D_NURB
          END INTERFACE 
        END MODULE SHP3D_NURB__genmod
