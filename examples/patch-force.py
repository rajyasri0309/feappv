import sys
import feap
from feap.scripts import patch

if len(sys.argv) > 1:
    ext = "-" + sys.argv[1]
    if sys.argv[1] == "a":
        gamma = 0.5
        def displf(x):
            return gamma*x[0], 0.0

    elif sys.argv[1] == "b":
        gamma = 0.5
        def displf(x):
            return gamma*x[1], 0.0
else:
    ext = ""
    def displf(x):
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



out = feap.FeapOutput(f"_feap/Opatch-displ{ext}" + ("-dist" if distort else ""))
reactions = out.react().df
nodes = out.coord.df

def boundary(node):
    return ((node[0]==0.0 or node[0]==1.0)) or (node[1]==0.0 or node[1]==1.0)


boun = "FORCE"
dist = """\
COORDINATE""" if distort else ""

for idx,node in nodes.to_dict(orient="index").items():
    x = list(node.values())
    if boundary(x) : #and idx not in [43, 1]:
        f = reactions.loc[idx]
        boun = "\n".join((boun, f"  {idx:5}  0  {f['1']:>12.8f} {f['2']:>12.8f}"))
    elif distort:
        dist = "\n".join((dist, f"  {idx:5} 0 {x[0]:>5.5f} {x[1]:>5.5f}"))

u_corner = displf([0., 1.])
# i_corner = nodes.loc["1 Coord"]
boun = boun + f"""

CBOUNDARY
  NODE 0.0 0.0 1 0
  NODE 0.0 0.5 0 1
  NODE 0.0 1.0 1 0

DISPLACEMENT
   7  0  {u_corner[0]}  {u_corner[1]}

"""

batch = """\

BATCH
  loop,,10
    tang, , 1
  next

  plot post
  plot defo
  plot boun
  plot defo
  plot node
  plot defo
  plot load
  plot defo
  plot mesh
  plot undefo,,1
  plot mesh
  plot post

  stre, all
  disp, all
! reac, all

END

! inter

stop
"""
out = feap.Feap(f"patch-force{ext}" + ("-dist" if distort else "")).exec(
        patch(blk, dist=dist, nen=nen, boun=boun, material=material)+batch).output

print(
    out.displ().df.join(out.displ().df, rsuffix="(b)")\
        .to_markdown(numalign="right", floatfmt=".2e")
)

nodes = out.coord.df
displ = out.displ().df
displ.insert(1, "1 Error", None)
# displ.insert(1, "1 True", None)
exterior = []
for node in nodes.index:
    x = nodes.loc[node]
    if boundary(x):
        exterior.append(node)
        u = displf(x)
        displ.loc[node, "1 Error"] =  (displ.loc[node, "1 Displ"] - u[0]) /u[0]
        displ.loc[node, "2 Error"] =  (displ.loc[node, "2 Displ"] - u[1]) /u[1]
        # displ.loc[node, "1 True"] = u[0]
        # displ.loc[node, "2 True"] = u[1]

print(displ.loc[exterior].to_markdown(numalign="right", floatfmt=".2e"))


