#!/usr/bin/env python
import textwrap

boun = """\
EBOUNDARY
   1 0.0 1 1
   1 1.0 1 1
   2 0.0 1 1
   2 1.0 1 1
"""

def patch(n=3, nen=4, disp="", order=2, dist="", boun=boun, material=None):
    if nen == 9:
        n *= 2
    if material is None:
        material = textwrap.dedent("""\
            MATERIAL 1
                SOLID
                Elastic Isotropic e n
                Enhanced
            """)


    return f"""\
FEAP ** Patch Test
  0,0,1,2,2,{nen}


PARAMETER
  e = 100.
  n = 0.3
  d = 0.0

{material}


BLOCK
  CART {n} {n} 1 1 1
    QUAD {nen}
      1 0.0 0.0
      2 1.0 0.0
      3 1.0 1.0
      4 0.0 1.0


{dist}

{boun}

{disp}

END mesh"""


