
"""
Script to analyse the HIV care cascade in South Africa
"""


## IMPORTS
import os
import atomica as at
import sciris as sc
import pylab as pl
import matplotlib.pyplot as plt
from atomica.optimization import optimize
import numpy as np

## THINGS TO RUN
torun = [
"loadframework",
# "saveframework",
# "makedatabook",
"makeproject",
"loaddatabook",
"makeparset",
"runsim",
"plotcascade",
# "makeblankprogbook",
# "runsim_programs",
# "makeplots",
# "export",
# "manualcalibrate",
# "autocalibrate",
# "parameterscenario",
# "coveragescenario",
# 'budgetscenarios',
# 'optimization',
]


## BEGIN ANALYSES
if "loadframework" in torun:
    F = at.ProjectFramework('hiv_southafrica_framework.xlsx')

if "saveframework" in torun:
    F.save('hiv_southafrica_framework.xlsx')

if "makedatabook" in torun:
    P = at.Project(framework=F)  # Create a project with an empty data structure.
    args = {"num_pops": 10, "num_transfers": 0, "data_start": 2016, "data_end": 2019, "data_dt": 1.0}
    P.create_databook(databook_path="hiv_southafrica_databook_blank.xlsx", **args)

if "makeproject" in torun:
    P = at.Project(name="SA HIV project", framework=F, do_run=False)

if "loaddatabook" in torun:
    P.load_databook(databook_path='hiv_southafrica_databook.xlsx', make_default_parset=False, do_run=False)

if "makeparset" in torun:
    P.make_parset(name="default")

if "runsim" in torun:
    P.update_settings(sim_start=2000.0, sim_end=2030, sim_dt=0.25)
    P.run_sim(parset="default", result_name="default")

if 'plotcascade' in torun:
    at.plot_cascade(P.results[-1], pops='all', year=[2017], data=P.data)
    pl.show()

if "makeblankprogbook" in torun:
    filename = "hiv_southafrica_progbook_blank.xlsx"
    P.make_progbook(filename, progs=23)

if "runsim_programs" in torun:

    parset = P.parsets[0]
    original_progset = P.progsets[0]
    reconciled_progset, progset_comparison, parameter_comparison = at.reconcile(project=P, parset=parset,
                                                                                progset=original_progset,
                                                                                reconciliation_year=2016.,
                                                                                unit_cost_bounds=0.2)
    instructions = at.ProgramInstructions(start_year=2016.)
    newalloc = {'Client-initiated clinic-based testing': 2000000}
    parresults = P.run_sim(parset="default", result_name="default-noprogs")
    progresults = P.run_sim(parset="default", progset='default', progset_instructions=instructions,
                            result_name="default-progs")
    at.plot_multi_cascade([parresults, progresults], 'TB care cascade', year=[2017])


