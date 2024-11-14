from . import Feap, FeapOutput


def parse_args(argv):
    opts = dict(
        interact=False,
        input=None,
        definitions = {},
        operation = "execute"
    )
    argi = iter(argv)
    for arg in argi:
        if arg == "-i":
            opts["interact"] = True
        elif arg == "--parse":
            opts["operation"] = "parse"
        elif "-D" in arg:
            if "=" in arg:
                arg = arg[2:]
            else:
                arg = next(argi)
            k,v = arg.split("=")
            opts["definitions"][k] = float(v)
        else:
            opts["input"] = arg
    return opts

if __name__=="__main__":
    opts = parse_args(sys.argv)
    file = opts.pop("input")
    script = open(file).read()
    name = file
    if opts["definitions"]:
        name = name + "-".join(f"{k}_{v}" for k,v in opts["definitions"].items())

    if file[0] == "I":
        opts.pop("operation")
        out  = Feap(name=name).exec(script.format(**opts.pop("definitions")), **opts)

    elif file[0] == "O" or opts["operation"] == "parse":
        FeapOutput(file).tables


