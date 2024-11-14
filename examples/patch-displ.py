import sys
import random
from feap import Feap, FeapOutput
from patch import patch

if len(sys.argv) > 1:
    ext = "-" + sys.argv[1]
    if sys.argv[1] == "a":
        gamma = 0.5
        def displ(x):
            return gamma*x[0], 0.0

    elif sys.argv[1] == "b":
        gamma = 0.5
        def displ(x):
            return gamma*x[1], 0.0
else:
    ext = ""
    def displ(x):
        return 5*x[0] + x[1], -x[0]

nen = 4
blk = 2
distort = ("--dist" in sys.argv)
stdlib  = ("--stdlib" in sys.argv)
material = """\
GLOBAL
    PLANE STRAIN

""" + ("""
mate,1
  solid
  finite volume 3
  elastic neohookean 237.6 0.32

""" if stdlib else """
mate,1
  user,14
  90.0 160.0 0
""")

if stdlib:
    ext += "-std"


def boundary(node):
    return ((node[0]==0.0 or node[0]==1.0)) or (node[1]==0.0 or node[1]==1.0)


nodes = Feap("patch-nodes").exec(patch(blk,nen=nen)).output.coord.df


#
# Read, re-run
#
DISP = "DISPLACEMENT"

dist = """\
COORDINATE""" if distort else ""
#  10 0 0.25 0.75"""

for idx,node in nodes.to_dict(orient="index").items():
    x = list(node.values())
    if boundary(x):
        u = displ(x)
        DISP = "\n".join((DISP, f"  {idx:5}  0  {u[0]:>12.12f}  {u[1]:>12.12f}"))
    elif distort:
        x[0] *= random.uniform(0.80, 1.2)
        x[1] *= random.uniform(0.80, 1.2)
        dist = "\n".join((dist, f"  {idx:5} 0 {x[0]:>5.5f} {x[1]:>5.5f}"))

script = patch(blk,nen=nen, disp=DISP, dist=dist, material=material) + """

BATCH
  loop,,10
    tang, , 1
  next
  disp, all
  stre, all
  reac, all

  plot post
  plot defo
  plot node
  plot defo
  plot mesh
  plot undefo,,1
  plot mesh
  plot post
END

stop

! inter

"""

out = Feap(f"patch-displ{ext}" + ("-dist" if distort else "")).exec(script) #.output

# nodes = out.coord.df
# displ = out.displ().df
# displ.insert(1, "1 Error", None)
# # displ.insert(1, "1 True", None)
# interior = []
# for node in nodes.index:
#     x = nodes.loc[node]
#     if not boundary(x):
#         interior.append(node)
#         u = 5*x[0] + x[1], -x[0]
#         displ.loc[node, "1 Error"] =  (displ.loc[node, "1 Displ"] - u[0])# /u[0]
#         displ.loc[node, "2 Error"] =  (displ.loc[node, "2 Displ"] - u[1])# /u[1]
#         # displ.loc[node, "1 True"] = u[0]
#         # displ.loc[node, "2 True"] = u[1]
#
# print(displ.loc[interior].to_markdown(numalign="right", floatfmt=".2e"))


