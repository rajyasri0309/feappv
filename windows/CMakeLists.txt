add_library(FEAP_OperatingSystem OBJECT)

target_compile_options(FEAP_OperatingSystem /libs:qwin)

target_sources(FEAP_OperatingSystem
    PRIVATE
        cinput.f
        clpan.f
        dplot.f
        etime.f
        pflush.f
        plabl.f
        plclos.f
        pleigt.f
        plline.f
        plopen.f
        plot9.f
        plstop.f
        plstrt.f
        pltcur.f
        pltdos.f
        pltefl.f
        pltelm.f
        pltext.f
        pltftx.f
        pltime.f
        pltnod.f
        pppcol.f
        pstart.f
        pwopn.f
        tplot.f
)
