indent = """
c***************************************************************************
c
c   INDENTATION PROBLEM:
c
c      Parameters that will change:
c
c         n = Poisson ratio
c         x = number of elements in the x direction
c         y = number of elements in the y direction
c
c***************************************************************************

param,POISSON RATIO
    n={n}

param,MESH
    x={x}
    y={y}

param
    e={E}

param
    l=1.
    h=1.
    b=h*1.05

feap ** Compression of a Block
0,0,2,2,2,{nen}

noprint

block
cart,1,x/2,1,1,2
1,0,b
2,0,h
3,l,h
4,l,b


block
cart,x,y,x+3,x/2+1,1
quad {nen}
1, 0.,0.
2,2*l,0.
3,2*l,h
4, 0.,h

eboun
1,0,1,0
1,2*l,1,0
2,0,0,1

forc
1,0,0,-50.

MATERIAL 1
  USER {elem}
  e n 0. 0


c
c NO NEED TO CHANGE THE PROPERTIES OF THE RIGID BLOCK
c
mate,2
solid
elastic isotropic e*1.d+08 0.3



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
  disp,,1

  plot post
  plot defo
  plot mesh
  plot undefo,,1
  plot mesh
  plot node -1
  plot post
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
    for n in 0,0.3,0.49999:
        for o in 1,2:
            displs = []
            meshes = []
            if elem == 12:
                nen = [0, 4, 9][o]
                o = 2
            else:
                nen = 4

            for x,y in (4,4),(8,8),(16,16),(32,32):
                i += 1
                params = dict(x=x, y=y, n=n, elem=elem, order=o, nen=nen, E=2.*50*(1+n))
                pname = f"indent-{elem}.1-{n}-{x}" + ("-r" if o==1 else "") + ("-Q2" if nen == 9 else "")
                out = feap.Feap(pname).exec(indent.format(**params)).output
                try:
                    displs.append(float(out.lines[-3].split()[-1]))
                    meshes.append(np.sqrt(x**2 + y**2))
                except:
                    pass

            if elem == 11:
                label = rf"$\nu={n}$" + (" (R)" if o==1 else "") + ("Q2" if nen == 9 else "Q1")
            else:
                label = None
            ax.plot(meshes, -np.array(displs), label=label)
    #ax.legend()
    ax.set_title(f"Element {elem}")
    ax.set_xlabel(r"$h$")

next(axi).axis("off")

# fig.suptitle("Locking in Low-Order Elements")
axs[0].set_ylabel("$u_1$")
fig.legend()
#fig.legend(loc=7)
#fig.tight_layout()
fig.subplots_adjust(right=0.75)
# plt.show()
# fig.savefig("indent.png")



