"""
Script to analyse the vaccine coverage in Pakistan
"""

import matplotlib
matplotlib.use("TkAgg")

## IMPORTS
import atomica as at
import sciris as sc
import pylab as pl
import numpy as np

## THINGS TO RUN
torun = [
"loadframework",        # Always required
"makedatabook",         # Only required if framework has changed
"makeproject",          # Always required
"loaddatabook",         # Always required
"makeparset",           # Always required
"runsim",               # Only required if you want to check the calibration
#"makeblankprogbook",    # Only required if framework has changed or if you want to use different programs
#"loadprogbook",         # Always required
# "reconcile",          # Only required the first time you load a program book
#"runsim_programs",    # Only required if you want to check the programs
# "budget_scenarios",   # Only required if you want to check the programs
#"optimize",             # Main purpose of script
]

load_reconciled = False
compare = False


## BEGIN ANALYSES
if "loadframework" in torun:
    F = at.ProjectFramework('pakistan_vaccines_framework.xlsx')

if "makedatabook" in torun:
    P = at.Project(framework=F)  # Create a project with an empty data structure based on the model framework
    args = {"num_pops": 4, "num_transfers": 0, "data_start": 2018, "data_end": 2020, "data_dt": 1.0}
    P.create_databook(databook_path="pakistan_vaccines_databook_blank.xlsx", **args)

if "makeproject" in torun:
    P = at.Project(name="Pakistan vaccines project", framework=F, do_run=False)

if "loaddatabook" in torun:
    P.load_databook(databook_path='pakistan_vaccines_databook_v1.xlsx', make_default_parset=False, do_run=False)

if "makeparset" in torun:
    P.make_parset(name="default")
    P.update_settings(sim_start=2018.0, sim_end=2025., sim_dt=1.)

if "runsim" in torun:
    P.run_sim(parset="default", result_name="default", store_results=True)

if "makeblankprogbook" in torun:
    filename = "pakistan_vaccines_progbook_blank.xlsx"
    P.make_progbook(filename, progs=6)

if "loadprogbook" in torun:
    if load_reconciled: filename = "pakistan_vaccines_progbook_reconciled.xlsx"
    else:               filename = "pakistan_vaccines_progbook.xlsx"
    P.load_progbook(progbook_path=filename)


