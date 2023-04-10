!$Id:$
      subroutine fluid3d(d,ul,xl,ix,tl,s,p,ndf,ndm,nst,isw)

!      * * F E A P * * A Finite Element Analysis Program

!....  Copyright (c) 1984-2023: Regents of the University of California
!                               All rights reserved

!-----[--.----+----.----+----.-----------------------------------------]
!     Modification log                                Date (dd/mm/year)
!       Original version                                    02/04/2018
!-----[--.----+----.----+----.-----------------------------------------]
!      Purpose: Three Dimensional Fluid Element Driver

!      Inputs:
!         d(*)  - Element parameters
!         ul(ndf,*) - Current nodal solution parameters
!         xl(ndm,*) - Nodal coordinates
!         ix(*)     - Global nodal connections
!         ndf       - Degree of freedoms/node
!         ndm       - Mesh coordinate dimension
!         nst       - Element array dimension
!         isw       - Solution option switch

!      Outputs:
!         s(nst,*)  - Element array
!         p(ndf,*)  - Element vector
!-----[--.----+----.----+----.-----------------------------------------]
      implicit  none

      include  'cdata.h'
      include  'debugs.h'
      include  'eldata.h'
      include  'eltran.h'
      include  'eqsym.h'
      include  'hdata.h'
      include  'iofile.h'
      include  'pmod2d.h'
      include  'qudshp.h'
      include  'setups.h'
      include  'strnum.h'
      include  'comblk.h'

      logical       :: mech,ther,mther, errck
      integer       :: ndf,ndm,nst,isw, i,tdof,pdof, ix(*)
      real (kind=8) :: d(*),ul(ndf,*),xl(ndm,*),tl(*),s(nst,nst),p(nst)
      real (kind=8) :: th(125)
      real (kind=8) :: ctan1

      save

!     Extract type data
      stype = nint(d(16))
      etype = nint(d(17))
      dtype = nint(d(18))
      hflag = d(67).eq.1.d0

!     Set nodal temperatures: Can be specified or computed
      if(isw.gt.1) then
        tdof = nint(d(19))
        if(tdof.le.0) then
          do i = 1,nel ! {
            th(i) = tl(i)
          end do ! i     }
        else
          do i = 1,nel ! {
            th(i) = ul(tdof,i)
          end do ! i     }
        endif
      endif

!     Set zero state: Output element type
      if(isw.eq.0 .and. ior.lt.0) then
        write(*,'(5x,a)') '3-d Fluid Element Driver.'

!     Input material properties
      elseif(isw.eq.1) then

        write(iow,2000)
        if(ior.lt.0) write(*,2000)

        call influid(d,tdof,   0   ,1)

!       Set to check in each element
        mech  = .true.
        ther  = .false.
        stype = nint(d(16))
        etype = nint(d(17))
        dtype = nint(d(18))

!       Check for incompressibility
        if(nint(d(170)).eq.5) then
          if(etype.eq.1) nlm = 4
        endif

!       Set tdof to zero if 1, 2, 3, or larger than ndf
        if(tdof.gt.ndf) then
          write(iow,3000)
          if(ior.lt.0) write(*,3000)
          tdof = 0
        elseif(tdof.ge.1 .and. tdof.le.3) then
          write(iow,3001)
          if(ior.lt.0) write(*,3001)
          tdof = 0
        endif

!       Deactivate dof in element for dof > 3
        if(etype.eq.2) then
          pdof = 5
        else
          pdof = 4
        endif

        do i = pdof,ndf
          ix(i) = 0
        end do ! i

!       If temperature dof is specified activate dof
        if(tdof.gt.ndf) then
          if(rank.eq.0) then
            write(*,'(a,i4)') ' --> Thermal DOF > NDF: TDOF =',tdof
          endif
          write(iow,'(a,i4)') ' --> Thermal DOF > NDF: TDOF =',tdof
          call plstop(.true.)
        elseif(tdof.gt.0) then
          ix(tdof) = 1
        endif

!       Set plot sequence
        pstyp = 3

!       Set number of projected stress and strains
        istv = max(istv,15)

!       Check for errors in problem size
        errck = .false.
        if(ndf.lt.3 .or. nen.lt.4) then
          if(rank.eq.0) then
            write(*,4000) ndf,nen
          endif
          write(iow,4000) ndf,nen
          errck = .true.
        endif

        if(errck) then
          call plstop(.true.)
        endif

!     Check element for errors
      elseif(isw.eq.2) then

        if(nel.eq.4 .or. nel.eq.10) then
          call cktets ( n_el, ix, xl, ndm, nel, shp3 )
        elseif(nel.eq.5) then
!         call ckpyr5 ( n_el, ix, xl, ndm, shp3 )
        elseif(nel.eq.6) then
!         call ckwed6 ( n_el, ix, xl, ndm, shp3 )
        elseif(nel.eq.8) then
          call ckbrk8 ( n_el, ix, xl, ndm, nel, shp3 )
        elseif(nel.eq.27) then
!         call ckbrkq ( n_el, ix, xl, ndm, nel, shp3 )
        else
          write(*,*) ' No check feature for',nel,' node elements'
        endif
        return

!     Compute mass matrix
      elseif(isw.eq.5) then
        call mass3d(d,xl,s,p,ndf,ndm,nst)
        return

!     Compute damping matrix
      elseif(isw.eq.9) then
!       call damp3d(d,xl,s,ndf,ndm,nst)
        return

!     History manipulation: None currently required
      elseif(isw.eq.12) then

        return

!     Critical time step computation
      elseif(isw.eq.21) then

        return

!     Body Force computation
      elseif(isw.eq.15 .or.isw.eq.23) then

!       call sbody3d(d,xl, p,ndm,ndf, isw)
        return

!     Compute boundary nodes
      elseif(isw.eq.26) then

!       call pcorner3d()
        return

!     Compute residuals and tangents for parts
      else

        mech =  isw.eq.4 .or.
     &          isw.eq.8 .or. isw.eq.14
        if(tdof.ne.0 .and. tdof.gt.ndm .and. hflag) then
          ther = isw.eq.4 .or.
     &          isw.eq.8 .or. isw.eq.14
        else
          ther = .false.
        endif

      endif

!     Check if symmetric or unsymmetric tangent
      if(neqs.eq.1) then
        mther = ther
      else
        mther = .false.
      endif

!     Compute stress-divergence vector (p) and stiffness matrix (s)
      if(mech) then

!       Explicit/Implicit element solutions
        if(isw.eq.3) then
          ctan1 = ctan(1)
          if(d(187).gt.0.0d0 .and.
     &       min(ctan(2),ctan(3)).gt.0.0d0) then
            ctan(1) = 0.0d0
          endif
        endif

!       Velocity Model
        if(etype.eq.1) then

          call flu3d1(d,ul,xl,th,s,p,ndf,ndm,nst,isw)

!       Dohrmann-Bochev Stabilized Model (B-Bar)
        elseif(etype.eq.3) then

          call flu3d3(d,ul,xl,th,s,p,ndf,ndm,nst,isw)

!       ALE Model
        elseif(etype.eq.9) then

          call flu3d9(d,ul,xl,th,s,p,ndf,ndm,nst,isw)

        endif

        if(isw.eq.3) then
          ctan(1) = ctan1
          if(debug) then
!           write(iow,'(a,i8)') 'ELEMENT',n_el
!           call mprint(p,  1,nst,  1,'FLUID Residual')
!           call mprint(s,nst,nst,nst,'FLUID Stiffness')
          endif
        endif

      endif

!     Compute thermal vector (p) and matrix (s)
      if(ther) then

!       Prevent multiple accumulation of projection weights
        if(isw.eq.8) then
          pdof = 1
          do i = 1,nen
            p(i) = 0.0d0
          end do ! i
        else
          pdof = tdof
        endif
        call therm3d(d,ul(tdof,1),xl,ix,s(pdof,pdof),p(pdof),
     &               ndf,ndm,nst,isw)
      endif

!     Formats for input-output

2000  format(
     & /5x,'T h r e e   D i m e n s i o n a l   F l u i d',
     &     '   E l e m e n t'/)

3000  format(' *WARNING* Thermal d.o.f. > active d.o.f.s : Set to 0')

3001  format(' *WARNING* Thermal d.o.f. can not be 1 to 3: Set to 0')

4000  format(' *ERROR* Problem control record incorrect:'/
     &       '         DOFs/Node (ndf) = ',i4,' - Should be 3 or more'/
     &       '         Nodes/Elm (nen) = ',i4,' - Should be 4 or more')

      end subroutine fluid3d
