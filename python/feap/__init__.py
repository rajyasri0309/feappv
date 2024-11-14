#!/usr/bin/env python

"""
                   ┌──┌─┐┌─┐ ┌─┐
                   ├─ └──└─└ ├─┘
   ────────────────┘─────────┘──────────────────────
                   © UC Regents
"""
import io
import os
import re
import sys
import textwrap
from pathlib import Path

import pandas


class FeapTable:
    end   = re.compile(r"\*Command ")
    begin = re.compile(r"\*Command *([0-9]*) *\*")
    def __init__(self, *args, **kwds):
        self.df = None

    def __repr__(self):
        try:
            return str(self.df)
        except:
            return "FeapTable"

class NodalCoordinates(FeapTable):
    #begin = re.compile("(N o d a l   C o o r d i n a t e s|     Nodal Coordinates)")
    #end   = re.compile("(E l e m e n t   C o n n e c t i o n s|[A-Z] [A-z] [A-z] [A-z])")
    begin = re.compile("^ *[Nn]ode *1 [Cc]oord")
    end = re.compile("^$")

    def __init__(self, file, begin, lines, tlines):
        rows = 1
        skip = []
        while begin+rows < tlines:
            if self.end.search(lines[begin+rows]):
                break
            elif "FEAP" in lines[begin+rows] \
                or "N o d a l   C o o r d i n a t e s" in lines[begin+rows]\
                or "Nodal Coordinates" in lines[begin+rows]:
                # or "1 coord" in lines[begin+rows] :
                skip.append(begin+rows)
                # print(lines[begin+rows], file=sys.stderr)
            rows += 1
        else:
            rows -= 1

        #self.columns = re.split(" {2,}", lines[begin+2].strip())
        self.columns = list(map(str.title, re.split(" {2,}", lines[begin].strip())))
        self.df = pandas.read_table(file,
            skiprows=lambda i: (i <= begin or (i in skip) or (i >= begin+rows)), nrows=rows, header=None,
            # usecols=lambda  i: ("Coord" not in i),
            skipinitialspace=True, index_col=0, sep='\s+',
            names=self.columns
        )
        self.offset = begin + rows

    def __repr__(self):
        return str(self.df)


class NodalDisplacements(FeapTable):
    begin = re.compile(r"\*Command *([0-9]*) *\* disp")

    def __init__(self, file, begin, lines, tlines, time=None):
        rows = 1
        skip = []
        while begin+rows < tlines:
            if self.end.search(lines[begin+rows]):
                break

            elif "Time" in lines[begin+rows]:
                match = re.search("Time *([0-9eE.+-]*)", lines[begin+rows])
                if match is not None:
                    time = float(match.groups(1)[0])
                skip.append(begin+rows)

            elif "FEAP" in lines[begin+rows] \
                or "N o d a l" in lines[begin+rows] \
                or "Prop. " in lines[begin+rows]\
                or "Node" in lines[begin+rows] \
                or "t=" in lines[begin+rows]:
                skip.append(begin+rows)
                pass
                #or "Command" in lines[begin+rows] \

            rows += 1

        else:
            rows -= 1

        self.columns = re.split(" {2,}", lines[begin+8].strip())
        self.df = pandas.read_table(file,
                #skiprows=lambda i: (i <= begin or (i in skip) or (i > begin+rows-9)), nrows=rows-9, header=None, 
            skiprows=lambda i: (i <= begin or (i in skip) or (i >= begin+rows)), nrows=rows-1, header=None,
            usecols=lambda  i: ("Coord" not in i),
            skipinitialspace=True, index_col=0, sep='\s+',
            names=self.columns
        )
        self.offset = begin + rows
        self.time = time


class NodalReactions(FeapTable):
    begin = re.compile(r"\*Command *([0-9]*) *\* reac")
    end = re.compile(r"Pr\.Sum")

    def __init__(self, file, begin, lines, tlines):
        rows = 1
        skip = []
        while begin+rows < tlines:
            if self.end.search(lines[begin+rows]):
                break
            elif "FEAP" in lines[begin+rows] \
                or "N o d a l" in lines[begin+rows] \
                or "Node" in lines[begin+rows] \
                or "Command" in lines[begin+rows] \
                or "t=" in lines[begin+rows]:
                skip.append(begin+rows)
                pass
            rows += 1
        else:
            rows -= 1

        self.columns = list(map(lambda i: i.replace(" dof",""), re.split(" {2,}", lines[begin+7].strip())))
        self.df = pandas.read_table(file,
                #skiprows=lambda i: (i <= begin or (i in skip) or (i > begin+rows-9)), nrows=rows-9, header=None, 
            skiprows=lambda i: (i <= begin or (i in skip) or (i >= begin+rows)), nrows=rows-1, header=None,
            usecols=lambda  i: ("Coord" not in i),
            skipinitialspace=True, index_col=0, sep='\s+',
            names=self.columns
        )
        self.offset = begin + rows

    def __repr__(self):
        return str(self.df)


TABLES = [
    NodalCoordinates,
    NodalDisplacements,
    NodalReactions
    #FeapTable
]

class FeapOutput:
    def __init__(self, file):
        if isinstance(file, (str,Path)):
            self.filename = file
            file = open(file, "r")
        else:
            self.filename = None
        self._coord = None
        self._disps = None

        self.text = file.read()
        self.file = file
        self.lines = self.text.split("\n")
        file.seek(0)
        self.parse()
        file.close()

    def react(self, **kwds):
        df = [t for t in self.tables if isinstance(t, NodalReactions)][0]
        if "x" in kwds:
            df = df[self.coords["1"] == kwds["x"]]
        return df

    @property
    def disps(self):
        if self._disps is None:
            self._disps = [t for t in self.tables if isinstance(t, NodalDisplacements)]
        return self._disps

    def displ(self, **kwds):
        df = self.disps

        if "time" in kwds:
            df = [i for i in df if i.time == time][0]
        else:
            df = df[0]

        if "x" in kwds:
            df = df[self.coords["1"] == kwds["x"]]

        return df

    @property
    def coord(self):
        if self._coord is None:
            table_iter = iter(t for t in self.tables if isinstance(t,NodalCoordinates))
            self._coord = next(table_iter)
            for t in table_iter:
                if isinstance(t,NodalCoordinates):
                    self._coord.df = t.df.combine_first(self._coord.df)

        return self._coord


    def parse(self):
        lines = self.lines
        ilines = iter(enumerate(lines))
        nlines = len(lines)
        self.tables = tables = []
        for i, line in ilines:
            for table in TABLES:
                if table.begin.search(line):
                    try:
                        tables.append(table(self.file, i, lines=lines, tlines=nlines))
                    except Exception as e:
                        raise
                    # print(tables[-1], file=sys.stderr)
                    while i < tables[-1].offset:
                        i, line = next(ilines)
                    self.file.seek(0)
                    break

    def __repr__(self):
        return "\n\n".join(map(str,self.tables))

class Feap:
    def __init__(self,
                 name=None,
                 input_file=None,
                 interact=False,
                 exec_dir=None,
                 plot_dir=None,
                 feap_bin=None
        ):
        if exec_dir is None:
            exec_dir = Path("./_feap/")

        if plot_dir is None:
            plot_dir = Path("./_plots/")

        if feap_bin is None:
            feap_bin = Path("/home/claudio/berkeley/ce-233/f84/feap84_2/bin/feap")


        self.set_run_directory(exec_dir)

        self.plot_dir = plot_dir

        self.name = name if name is not None else "xx"
        self.input_file = input_file
        self._output = None
        self._feap_exec = feap_bin


    def set_run_directory(self, directory):
        self.exec_dir = Path(directory)
        self.exec_dir.mkdir(parents=True, exist_ok=True)
        self.existing_plots = [
            f.name for f in self.exec_dir.glob("Feap*.eps")
        ]


    @property
    def output(self):
        if self._output is None:
            self._output = FeapOutput(self.exec_dir/self.input_file.replace("I","O"))
        return self._output

    def exec(self, script, interact=False, clean=True):
        if "stop" not in script:
            script = script + "\nstop\n"

        if interact:
            script.replace("stop", "inter")


        if self.name[0] != "I":
            self.input_file = f"I{self.name}"
        else:
            self.input_file = self.name

#       if Path(self.work_dir).is_dir():
#           self.set_run_directory(Path("_feap"))

        with open(self.exec_dir/self.input_file, "w+") as f:
            f.write(script)

        self.run()


        if clean:
            # Delete the input file
            (self.exec_dir/self.input_file).unlink()

        return self

    def run(self, organize=True):
        os.system(f"cd {self.exec_dir} && " + \
                  f"{self._feap_exec}   -i{self.input_file}"
        )
        if organize:
            self.organize()

        return self

    def organize(self):
        plot_counter = 0
        outdir = self.plot_dir
        for file in self.exec_dir.glob("Feap*.eps"):
            if file.name not in self.existing_plots:
                plot_counter += 1
                file.rename(outdir/f"{self.input_file[1:]}-{plot_counter}.eps")

    def __repr__(self):
        return str(self.output)


