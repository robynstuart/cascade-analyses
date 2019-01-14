
"""
Script to analyse the T2DM care cascade in Poltava
"""


## IMPORTS
import atomica as at
import sciris as sc
import pylab as pl
import numpy as np

## THINGS TO RUN
torun = [
"loadframework",        # Always required
# "makedatabook",       # Only required if framework has changed
"makeproject",          # Always required
"loaddatabook",         # Always required
"makeparset",           # Always required
"runsim",             # Only required if you want to check the calibration
# "plotcascade",        # Only required if you want to check the calibration
# "makeblankprogbook",  # Only required if framework has changed or if you want to use different programs
# "loadprogbook",         # Always required
# "reconcile",          # Only required the first time you load a program book
# "runsim_programs",    # Only required if you want to check the programs
# "budget_scenarios",   # Only required if you want to check the programs
# "optimize",             # Main purpose of script
]

load_reconciled = False
compare = False

## BEGIN ANALYSES
if "loadframework" in torun:
    F = at.ProjectFramework('t2dm_poltava_framework.xlsx')

if "makedatabook" in torun:
    P = at.Project(framework=F)  # Create a project with an empty data structure based on the model framework
    args = {"num_pops": 10, "num_transfers": 0, "data_start": 2014, "data_end": 2017, "data_dt": 1.0}
    P.create_databook(databook_path="t2dm_poltava_databook_blank.xlsx", **args)

if "makeproject" in torun:
    P = at.Project(name="Poltava T2DM project", framework=F, do_run=False)

if "loaddatabook" in torun:
    P.load_databook(databook_path='t2dm_poltava_databook.xlsx', make_default_parset=False, do_run=False)

if "makeparset" in torun:
    P.make_parset(name="default")
    P.update_settings(sim_start=2014.0, sim_end=2020., sim_dt=1.)

if "runsim" in torun:
    P.run_sim(parset="default", result_name="default", store_results=True)
#    at.export_results(P.results, 't2dm_poltava_blresults_0107.xlsx')
#    P.calibrate(max_time=300, new_name="auto")
#    P.run_sim(parset="auto", result_name="auto")
    print(P.results[-1].get_variable('adults','txs_vd')[0].vals+P.results[-1].get_variable('adults','txf_vd')[0].vals)
    print(P.results[-1].get_variable('adults','txs_uncomp')[0].vals+P.results[-1].get_variable('adults','txf_uncomp')[0].vals)

if 'plotcascade' in torun:
    at.plot_multi_cascade(P.results[-1], pops='all', year=[2014,2015,2016,2017,2018,2019,2020], data=P.data)
    at.plot_cascade(P.results[-1], pops='adults', year=[2016], data=P.data) # This doesn't show the datapoints for some reason
    pl.show()

if "makeblankprogbook" in torun:
    filename = "t2dm_poltava_progbook_blank.xlsx"
    P.make_progbook(filename, progs=23)

if "loadprogbook" in torun:
    if load_reconciled: filename = "t2dm_poltava_progbook_reconciled.xlsx"
    else:               filename = "t2dm_poltava_progbook.xlsx"
    P.load_progbook(progbook_path=filename)

if "reconcile" in torun:

    parset = P.parsets[0]
    original_progset = P.progsets[0]
    reconciled_progset, progset_comparison, parameter_comparison = at.reconcile(project=P, parset=parset,
                                                                                progset=original_progset,
                                                                                reconciliation_year=2016.,
                                                                                max_time=100,
                                                                                baseline_bounds=0.75,
                                                                                outcome_bounds=0.75,
                                                                                unit_cost_bounds=0.1)
    instructions = at.ProgramInstructions(start_year=2016.)
    parresults = P.run_sim(parset="default", result_name="default-noprogs", store_results=True)
    progresults = P.run_sim(parset="default", progset='default', progset_instructions=instructions,
                            result_name="default-progs", store_results=True)
    recresults = P.run_sim(parset="default", progset=reconciled_progset, progset_instructions=instructions,
                            result_name="reconciled-progs", store_results=True)
    at.plot_multi_cascade([parresults, progresults, recresults], year=[2017])

    reconciled_progset.save("t2dm_poltava_progbook_reconciled.xlsx")

    print(progset_comparison)
    print(parameter_comparison)

if "runsim_programs" in torun:

    parset = P.parsets[0]
    original_progset = P.progsets[0]
    instructions = at.ProgramInstructions(start_year=2016.)

    progresults = P.run_sim(parset="default", progset='default', progset_instructions=instructions,
                            result_name="default-progs", store_results=True)

    at.plot_multi_cascade(progresults, year=[2016,2017,2018,2019,2020])

    if compare:
        parresults = P.run_sim(parset="default", result_name="default", store_results=True)
        at.plot_multi_cascade([parresults, progresults], year=[2017])

    at.export_results(P.results, 't2dm_poltava_results_0103.xlsx')

#    coverage = sc.odict([('Blood glucose test (PHC level)', np.array([0.0164])),
#                      ('Blood glucose test (Feldsher post family nurse)', np.array([0.0062])),
#                      ('Blood glucose test (outreach/community-based)', np.array([0.0021])) ])
#    outcomes = original_progset.covouts[0].get_outcome(coverage) #
#    print(outcomes)
#    print(P.results[-1].get_variable('adults','pos_screen')[0].vals)
#    print(P.results[0].get_variable('adults','pos_screen')[0].vals)
#    print(progresults.get_variable('adults','treat_suc')[0].vals)
#    print(parresults.get_variable('adults','treat_suc')[0].vals)


if "budget_scenarios" in torun:

    default_budget = at.ProgramInstructions(start_year=2016, alloc=P.progsets[0])
    doubled_budget = sc.dcp(default_budget)
    for p in doubled_budget.alloc.values():
        p.vals[0] *= 2

    parresults = P.run_sim(parset="default", result_name="default-noprogs", store_results=True)
    default_baseline = P.run_sim(P.parsets[0], progset=P.progsets[0], progset_instructions=default_budget,
                                 result_name='default', store_results=True)
    doubled_baseline = P.run_sim(P.parsets[0], progset=P.progsets[0], progset_instructions=doubled_budget,
                                 result_name='doubled', store_results=True)

    at.plot_multi_cascade([parresults, default_baseline, doubled_baseline], year=[2017,2020])


if "optimize" in torun:

    # SET BASELINE SPENDING
    instructions = at.ProgramInstructions(start_year=2016) # Instructions for default spending

    # SET ADJUSTMENTS
    adjustments = []
    for progname in P.progsets[0].programs.keys():
        adjustments.append(at.SpendingAdjustment(progname, [2016,2017,2018,2019,2020,2021,2022], 'rel', 0., 100.))

    # SET CONSTRAINTS
    constraints = at.TotalSpendConstraint() # Cap total spending in all years

    # SET CASCADE MEASURABLE
    measurables = at.MaximizeCascadeConversionRate('Diabetes care cascade', [2022],
                                                   pop_names='all')

    # DO OPTIMIZATION
    optimization = at.Optimization(name='default', adjustments=adjustments, measurables=measurables,
                                   constraints=constraints)


    # COLLECT RESULTS
    unoptimized_result = P.run_sim(parset=P.parsets["default"], progset=P.progsets['default'],
                                   progset_instructions=instructions, result_name="unoptimized", store_results=True)
    optimized_instructions = at.optimize(P, optimization, parset=P.parsets["default"],
                                         progset=P.progsets['default'], instructions=instructions)
    optimized_result = P.run_sim(parset=P.parsets["default"], progset=P.progsets['default'],
                                 progset_instructions=optimized_instructions, result_name="optimized", store_results=True)


    # MAKE CASCADE PLOT
    at.plot_multi_cascade([unoptimized_result, optimized_result], year=[2022])

    # MAKE PLOTS TO COMPARE BUDGETS
    d = at.PlotData.programs([optimized_result, unoptimized_result])
    d.interpolate(2018)
    at.plot_bars(d, stack_outputs='all')

    # EXPORT RESULTS
#    at.export_results(P.results, 't2dm_poltava_results_0103.xlsx')
