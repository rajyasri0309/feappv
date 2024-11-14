#!/usr/bin/env python

block = """
 ! *********************************************************
 !
 !   Upsetting of an elastic block
 !
 !      Parameters that will change:
 !
 !         n     Poisson ratio
 !         nen   Number of element nodes
 !
 ! *********************************************************

feap ** Block compression
    0,0,1,2,2,{nen}


param,POISSON RATIO
    n={n}

param
    a=1.
    b=1.5

param
    mu=50.
    e=2.0*mu*(1.0+n)

! print

block
  cart,{x},10,1
    1 0. 0.
    2 a  0.
    3 a  b
    4 0. b

eboun
    1 0. 1   0
    2 0. 1   1
    2 b  0   1

edisp
    2 b  0. -1.

MATERIAL 1
USER {elem}
e n 0. 0 2

! MATERIAL 1
! SOLID
! elastic isotropic e n
! ENHANCED

end

tie
optimize

! macro
! nopr
! tang,,1
! disp,,1
! end

batch
  tang,,1
  loop plot 5

      plot post
      plot defo
      plot mesh
      plot undefo,,1
      plot mesh
      plot post
      plot wipe

      augment

      loop soln 5
        tang,,1
      next soln

  next plot
end

! inter

stop

"""


import matplotlib.pyplot as plt
plt.style.use("steel")
import numpy as np
import feap
import sys
i = 0
fig, axs = plt.subplots(1,4, sharey=True, constrained_layout=True)
axi = iter(axs)
for elem in 13, : #10,11,12:
    ax = next(axi)
    for n in 0.3, 0.45, 0.499, 0.49999:
        for o in 1,:
            displs = []
            meshes = []
            nen = 9
            if elem == 12:
                #nen = [0, 4, 9][o]
                aug = [0, 0, 1][o]
                o = 2
            elif o == 2:
                continue
            else:
                nen = 4
                aug = False

            if nen == 4:
                x = 5
            else:
                x = 10

            i += 1

            params = dict(x=x, n=n, elem=elem, nen=nen)
            pname = f"block-{elem}-{n}-{x}" + ("-A" if aug else "")
            if aug:
                params["augment"] = "  " + "\n".join(["  augment\n  tang,,1"]*5)
            else:
                params["augment"] = ""
            script = block.format(**params)

            out = feap.Feap(pname).exec(script).output

            try:
                displs.append(float(out.lines[-3].split()[-1]))
                meshes.append(np.sqrt(x**2 + y**2))
            except:
                pass

            if elem == 11:
                label = rf"$\nu={n}$" + (" (R)" if o==1 else "") + ("Q2" if nen == 9 else "Q1")
            else:
                label = None
#           ax.plot(meshes, -np.array(displs), label=label)
    #ax.legend()
    ax.set_title(f"Element {elem}")
    ax.set_xlabel(r"$h$")

next(axi).axis("off")

# fig.suptitle("Locking in Low-Order Elements")
axs[0].set_ylabel("$u_1$")
fig.legend()
#fig.legend(loc=7)
#fig.tight_layout()
# fig.subplots_adjust(right=0.75)
# plt.show()
# fig.savefig("block.png")



