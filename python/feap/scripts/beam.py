script = """\
FEAP ** Bending
  0,0,1,2,2,4

PARAMETER
  L = 5.
  h = 1.0
  E = 100.
  n = {v}
  I = {M}
  J = {N}

GLOBAL
    PLANE {plane}

MATERIAL 1
  SOLID
  ENHANCED
  elastic isotropic e n

MATERIAL 2
  user 13
  e     n 0.0 0 2

BLOCK
  CART I J 1 1 {elem}
  QUAD 4
  1   0.0   0.0
  2    L    0.0
  3    L     h
  4   0.0    h

EBOUNDARY
  1 0.0 1 0

CBOUNDARY
  NODE 0.0 h/2 1 1

CSURFACE
  LINEAR
  1  L  0.0  6/h/h
  2  L   h  -6/h/h

END mesh

BATCH
  tang, , 1

  plot post
  plot defo
! plot node -1
  plot defo
  plot mesh
  plot undefo,,1
  plot mesh
  plot post

  disp, all
END

"""

from feap import Feap
import numpy as np
import matplotlib.pyplot as plt
plt.style.use("steel")

X = np.linspace(0, 5, 100)

cfig, cax = plt.subplots(1,2, constrained_layout=True, sharey=True)
cax = iter(cax.flatten())
caxi = next(cax)
caxi.set_ylabel("Error")
elem = 2 # 2: user, 1: feap
for plane in "STRAIN","STRESS":
    fig, axa = plt.subplots(2,2,constrained_layout=True)
    fig.suptitle(f"Plane {plane.title()}")
    axi = iter(axa.flatten())
    caxi.set_title(f"Plane {plane.title()}")
    caxi.set_xlabel("$M$")

    for v in 0.3, 0.45, 0.499, 0.49999:
        E = 100.0
        if plane == "STRAIN":
            E /= (1-v**2)
        ax = next(axi)
        ax.set_xlabel(r"$x_1$")
        ax.set_ylabel(r"$u_2$")
        ax.plot(X, 1/E*12*0.5*X**2)
        h = []
        e = []
        for N,M in (2,2), (2,4), (4,8), (8,16): #(32,64):
            p = Feap(f"beam-{elem}-{plane.lower()}-{v}-{N}").exec(script.format(N=N,M=M,v=v,plane=plane,elem=elem)).output
            df = p.displ(t=0.0).df #, x=5.0)
            X = p.coord.df[p.coord.df["2 Coord"] == 0.5]["1 Coord"]
            Y = df[(p.coord.df["2 Coord"] == 0.5)[df.index]]["2 Displ"]
            ax.plot(X, Y)

            h.append(M)
            u_true = 1/E*12*0.5*5**2
            # print(Y.iloc[-1])
            e.append(abs(Y.iloc[-1] - u_true)/u_true)

        print(h,e)
        ax.set_title(rf"$\nu = {v}$")
        caxi.loglog(h, e, label=rf"$\nu={v}$")
    try:
        caxi = next(cax)
    except:
        caxi.legend()
        print("i")

    fig.savefig(f"_plots/beam-{plane.lower()}.png")

cfig.savefig("_plots/beam-conv.png")


plot_cmd = """
batch
  plot post
  plot mesh
  plot boun
  plot disp
  plot load
  plot post

  tang,,1
  plot post
  plot defo
  plot node -1
  plot defo
  plot mesh
  plot undefo,,1
  plot mesh
  plot post
end
"""
# p = Feap("beam").exec(script.format(N=N,M=M,v=v,plane=plane,elem=elem)+plot_cmd).output


