!$Id:$
      subroutine pmatin(tx,d,ul,xl,tl,s,p,idl,ie,iedof,lie,prt,prth)

!      * * F E A P * * A Finite Element Analysis Program

!....  Copyright (c) 1984-2023: Regents of the University of California
!                               All rights reserved

!-----[--.----+----.----+----.-----------------------------------------]
!      Purpose: Data input routine for material parameters

!      Inputs:
!         tx           - Option identifier
!         prt          - Flag, print input data if true
!         prth         - Flag, print title/header if true

!      Scratch:
!         ul(*)        - Local nodal solution vector
!         xl(*)        - Local nodal coordinate vector
!         tl(*)        - Local nodal temperature vector
!         s(*)         - Element array
!         p(*)         - Element vector
!         idl(*)       - Local degree of freedom integer data
!         lie(ndf,*)   - Local dof assignment array

!      Outputs:
!         ie(nie,*)    - Element assembly data
!         iedof(*,*,*) - Element nodal assembly data
!         d(ndd,*)     - Material parameters generated by elements
!-----[--.----+----.----+----.-----------------------------------------]
      implicit  none

      include  'cdata.h'
      include  'cdat1.h'
      include  'chdata.h'
      include  'contrl.h'
      include  'eldata.h'
      include  'elname.h'
      include  'erotas.h'
      include  'hdata.h'
      include  'iofile.h'
      include  'iosave.h'
      include  'pdata3.h'
      include  'strnum.h'
      include  'sdata.h'

      character (len=69) :: mtype
      character (len=26) :: etype
      character (len=15) :: tx(2)

      logical       :: pcomp,pinput,tinput,vinput,errck,prt,prth,doflg
      logical       :: nomtyp
      integer       :: i,j, ii,il,is, isw
      real (kind=8) :: td(50)
      integer       :: lie(ndf,*),ie(nie,*),iedof(ndf,nen,*),idl(*)
      real (kind=8) :: d(ndd,*),ul(*),xl(*),tl(*),s(*),p(*)
      real (kind=8) :: uelnum(1)

      save

!     Data input for material set ma

      errck = vinput(yyy(16:30),15,td,1)
      ma    = max(1,int(td(1)))

!     Warning trap
      if(ie(3,ma).ne.0) then
        write(  *,3002) ma
        write(iow,3002) ma
      else
        ie(3,ma) = ma
      endif
      if(ma.le.0 .or. ma.gt.nummat) then
        if(ior.gt.0) then
          write(iow,3000) ma
          write(iow,3001)
          write(  *,3000) ma
          write(  *,3001)
          call plstop(.true.)
        else
          write(*,3000) ma,' Reinput mate,ma'
        endif
        return
      endif

      if(prt) then
        call prtitl(prth)
        write(iow,2000)
      endif

!     Set material identifier

      do j = 3,80
        if(xxx(j:j).eq.' ' .or. xxx(j:j).eq.',') then
          do i = j+1,80
            if(xxx(i:i).eq.' ' .or. xxx(i:i).eq.',') go to 300
          end do ! i
        endif
      end do ! j
      i = 80
300   nomtyp = .true.
      do j = i+1,80
        if(xxx(j:j).ne.' ') go to 310
      end do ! j
      j = 80
      nomtyp = .false.
310   mtype = xxx(j:80)

!     Input record for element type selection

301   if(ior.lt.0) write(*,2004)
      il = min(ndf+2,14)
      errck = tinput(tx(1),2,td,il)
      if(errck) go to 301

!     Set material type for standard and user elements

      iel = 0
      if(pcomp(tx(1),'user',4)) then ! Get name as 'user ma'
        errck = vinput(tx(2),15,uelnum,1)
        iel   = nint(uelnum(1))
      else                  ! Extract name of user element
        do j = 1,15
          if(pcomp(tx(1),umatn(j),15)) then
            iel = j
            exit
          endif
        end do ! j
        if(iel.eq.0) then  ! Standard FEAPpv element types
          call pelnum(tx(1),iel,errck)
        endif
      endif

      if(ie(nie-1,ma).ne.0 .and. iel.eq.0) then
        iel = ie(nie-1,ma)
      else
        ie(nie-2,ma) = nint(td(1))               ! Element set number
        if(ie(nie-2,ma).le.0) ie(nie-2,ma) = ma
      endif

!     Set print head

      if(ma.eq.ie(nie-2,ma)) then
        etype = ' '
      else
        write(etype,'(a22,i4)') 'Element Material Set =',ie(nie-2,ma)
      endif

!     Set idl for first group of dof's

      do j = 1,min(ndf,12)
        idl(j) = nint(td(j+1))
      end do ! j

!     For large number of dof's input additional records and set idl

      if(ndf.gt.12) then
        il = 12
        do ii = 1,(ndf+2)/16
          is = il+1
          il = min(is+15,ndf)
302       errck = pinput(td,16)
          if(errck) go to 302
          do j = is,il
            idl(j) = nint(td(j-is+1))
          end do ! j
        end do ! ii
      endif

!     Check to see if degree of freedoms to be reassigned

      do i = 1,ndf
        if(idl(i).ne.0) go to 303
      end do ! i

!     Reset all zero inputs
      do i = 1,ndf
        idl(i) = i
      end do ! i

303   ie(nie-1,ma) = iel

!     Set flags for number of history and stress terms
      mct  = 0
      nh1  = 0            ! History pointers
      nh2  = 0
      nh3  = 0
      nlm  = 0            ! Element equations
      istv = 0            ! Number element projections

!     Output information
      if(prt) then
        if(iel.gt.0) then
          write(iow,2001) ma,tx(1),iel,etype,(j,idl(j),j=1,ndf)
        else
          write(iow,2002) ma,tx(1)(1:5),etype,(j,idl(j),j=1,ndf)
        endif
        if(nomtyp) write(iow,2003) mtype
      else
        if(iel.gt.0) then
          write(iow,2001) ma,tx(1),iel,etype
        else
          write(iow,2002) ma,tx(1)(1:5),etype
        endif
        if(nomtyp) write(iow,2003) mtype
      endif

!     Obtain inputs from element routine
      do j = 1,nen+1
        do i = 1,ndf
          lie(i,j) = i
        end do ! i
      end do ! j
      rotyp = 0

!     Set default plot type
      pstyp = ndm
      isw   = 1
      call elmlib(d(1,ma),ul,xl,lie,tl,s,p,ndf,ndm,nst,iel,isw)

      doflg = .false.    ! Check if mixed conditions exist
      do i = 1,ndf
        do j = 1,nen
          if(lie(i,j+1).eq.0) then
            doflg = .true.
          endif
        end do ! j
      end do ! i

!     Set assembly information
      if(doflg) then
        do i = 1,ndf
          do j = 1,nen
            if(lie(i,j+1).gt.0) then
              iedof(i,j,ma) = idl(i)
            else
              iedof(i,j,ma) = 0
            endif
          end do ! j
        end do ! i
      else
        do i = 1,ndf
          if(lie(i,1).gt.0) then
            do j = 1,nen
              iedof(i,j,ma) = idl(i)
            end do ! j
          else
            do j = 1,nen
              iedof(i,j,ma) = 0
            end do ! j
          endif
        end do ! i
      endif

!     Set plot information
      ie(1,ma) = pstyp

!     Set number of history terms
      if(nh1.ne.0) then
        ie(nie,ma) = int(nh1)
      else
        ie(nie,ma) = mct
      endif
      ie(nie-5,ma) = int(nh3)

!     Element Lagrange multiplier number
      if(nlm.gt.0) then
        ie(nie-8,ma) = nlm
        nad          = max(nad,nlm)
      endif

!     Set rotational update type
      if(rotyp.ne.0) then
        ie(nie-6,ma) = rotyp
      endif

!     Set maximum number of element plot variables
      npstr = max(npstr,istv)

!     Formats

2000  format('   M a t e r i a l    P r o p e r t i e s')

2001  format(/5x,'Material Number',i4,': Element Type: ',a,
     &        ': ELMT =',i3/5x,a,:/
     &        5x,'Degree of Freedom Assignments    Local    Global'/
     &       37x,'Number',4x,'Number'/(31x,2i10))

2002  format(/5x,'Material Number',i4,': Element Type: ',a,': ',a,:/,
     &        5x,'Degree of Freedom Assignments    Local    Global'/
     &       37x,'Number',4x,'Number'/(31x,2i10:))

!2001  format(/5x,'Material Set',i3,' for User Element Type',i3,5x,/:/
!     &   5x,'Degree of Freedom Assignments    Local    Global'/
!     &   37x,'Number',4x,'Number'/(31x,2i10))

!!2002  format(/5x,'Material Set',i3,' for Element Type: ',a,5x,/:/
!     &   5x,'Degree of Freedom Assignments    Local    Global'/
!     &   37x,'Number',4x,'Number'/(31x,2i10))

2003  format(5x,a)

2004  format(' Input: Elmt type, Id No., dof set'/3x,'>',$)

3000  format(' *ERROR* PMATIN: Illegal material number: ma=',i5:,a)
3001  format('                 Check value of NUMMAT on control record')

3002  format(' --> WARNING: Duplicate material number',i5,' specified')

      end subroutine pmatin
