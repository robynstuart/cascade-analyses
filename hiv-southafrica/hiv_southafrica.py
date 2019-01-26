
"""
Script to analyse the HIV care cascade in South Africa
"""


## IMPORTS
import atomica as at
import sciris as sc
import pylab as pl

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
"loadprogbook",         # Always required
# "reconcile",          # Only required the first time you load a program book
# "runsim_programs",    # Only required if you want to check the programs
# "budget_scenarios",   # Only required if you want to check the programs
"optimize",             # Main purpose of script
]

load_reconciled = False

## BEGIN ANALYSES
if "loadframework" in torun:
    F = at.ProjectFramework('hiv_southafrica_framework.xlsx')

if "makedatabook" in torun:
    P = at.Project(framework=F)  # Create a project with an empty data structure based on the model framework
    args = {"num_pops": 10, "num_transfers": 0, "data_start": 2017, "data_end": 2019, "data_dt": 1.0}
    P.create_databook(databook_path="hiv_southafrica_databook_blank.xlsx", **args)

if "makeproject" in torun:
    P = at.Project(name="SA HIV project", framework=F, do_run=False)

if "loaddatabook" in torun:
    P.load_databook(databook_path='hiv_southafrica_databook.xlsx', make_default_parset=False, do_run=False)

if "makeparset" in torun:
    P.make_parset(name="default")

if "runsim" in torun:
    P.update_settings(sim_start=2017.0, sim_end=2030, sim_dt=0.25)
    P.run_sim(parset="default", result_name="default", store_results=True)
#    P.calibrate(max_time=300, new_name="auto")
#    P.run_sim(parset="auto", result_name="auto")

    # Print estimates of the number of new infections
    inf = sc.odict()
    death = sc.odict()
    for pname in P.results[-1].pop_names:
        inf[pname] = P.results[-1].get_variable(pname, 'num_acq')[0].vals
        death[pname] = P.results[-1].get_variable(pname, 'num_hiv_deaths')[0].vals
    print(inf[:][:,0:10].sum(axis=0))
    print(death[:][:,0:10].sum(axis=0))

if 'plotcascade' in torun:
    at.plot_multi_cascade(P.results[-1], pops='all', year=[2017,2018,2020], data=P.data)
    pl.show()

if "makeblankprogbook" in torun:
    filename = "hiv_southafrica_progbook_blank.xlsx"
    P.make_progbook(filename, progs=23)

if "loadprogbook" in torun:
    if load_reconciled: filename = "hiv_southafrica_progbook_reconciled.xlsx"
    else:               filename = "hiv_southafrica_progbook.xlsx"
    P.load_progbook(progbook_path=filename)

if "reconcile" in torun:

    parset = P.parsets[0]
    original_progset = P.progsets[0]
    reconciled_progset, progset_comparison, parameter_comparison = at.reconcile(project=P, parset=parset,
                                                                                progset=original_progset,
                                                                                reconciliation_year=2017.,
                                                                                max_time=100,
                                                                                baseline_bounds=0.75,
                                                                                outcome_bounds=0.75,
                                                                                unit_cost_bounds=0.0)
    instructions = at.ProgramInstructions(start_year=2017.)
    parresults = P.run_sim(parset="default", result_name="default-noprogs", store_results=True)
    progresults = P.run_sim(parset="default", progset='default', progset_instructions=instructions,
                            result_name="default-progs", store_results=True)
    recresults = P.run_sim(parset="default", progset=reconciled_progset, progset_instructions=instructions,
                            result_name="reconciled-progs", store_results=True)
    at.plot_multi_cascade([parresults, progresults, recresults], year=[2018])

    reconciled_progset.save("hiv_southafrica_progbook_reconciled.xlsx")

    print(progset_comparison)
    print(parameter_comparison)

if "runsim_programs" in torun:

    parset = P.parsets[0]
    original_progset = P.progsets[0]
    instructions = at.ProgramInstructions(start_year=2017.)
    parresults = P.run_sim(parset="default", result_name="default-noprogs", store_results=True)
    progresults = P.run_sim(parset="default", progset='default', progset_instructions=instructions,
                            result_name="default-progs", store_results=True)
    at.plot_multi_cascade(cascade='Extended HIV care cascade', results=[parresults, progresults], year=[2018])
    at.plot_multi_cascade(cascade='Extended HIV care cascade', results=progresults, year=[2018,2019,2020,2021,2022])


if "budget_scenarios" in torun:

    default_budget = at.ProgramInstructions(start_year=2016, alloc=P.progsets[0])
    doubled_budget = default_budget.scale(2)

    parresults = P.run_sim(parset="default", result_name="default-noprogs", store_results=True)
    default_baseline = P.run_sim(P.parsets[0], progset=P.progsets[0], progset_instructions=default_budget,
                                 result_name='default', store_results=True)
    doubled_baseline = P.run_sim(P.parsets[0], progset=P.progsets[0], progset_instructions=doubled_budget,
                                 result_name='doubled', store_results=True)

    at.plot_multi_cascade([parresults, default_baseline, doubled_baseline], year=[2017,2020])


if "optimize" in torun:

    # SET BASELINE SPENDING
#    alloc = sc.odict([
    #            ("Client-initiated clinic-based testing",at.TimeSeries([2018,2022],[53354825,70272330])),
    #       ("Provider-initiated testing",at.TimeSeries([2018,2022],[1958157,2579040])),
    #       ("Mobile testing",at.TimeSeries([2018,2022],[1937319,2551596])),
    #       ("Door-to-door testing",at.TimeSeries([2018,2022],[1430195,1883675])),
    #       ("Workplace testing",at.TimeSeries([2018,2022],[670563,883182])),
    #       ("Youth-friendly  SRH testing",at.TimeSeries([2018,2022],[716945,944271])),
    #       ("Self-testing",at.TimeSeries([2018,2022],[847315,1115978])),
    #       ("CD4 testing",at.TimeSeries([2018,2022],[3995486,5262357])),
    #       ("Community support - link to care",at.TimeSeries([2018,2022],[350468,461593])),
    #       ("Additional education (prof)",at.TimeSeries([2018,2022],[231217,304530])),
    #       ("Additional education (lay)",at.TimeSeries([2018,2022],[16105,21211])),
    #       ("Classic ART initiation",at.TimeSeries([2018,2022],[1558316,2052420])),
    #       ("Fast-track ART initiation",at.TimeSeries([2018,2022],[376159,495429])),
    #       ("Same day ART initiation",at.TimeSeries([2018,2022],[97778,128781])),
    #       ("Community support - adherence",at.TimeSeries([2018,2022],[910142,1198725])),
    #       ("WhatsApp messaging - adherence",at.TimeSeries([2018,2022],[449,592])),
    #       ("Tracing of ART clients",at.TimeSeries([2018,2022],[825759,1087587])),
    #       ("Enhanced adherence (prof)",at.TimeSeries([2018,2022],[1325445,1745710])),
    #       ("Enhanced adherence (lay)",at.TimeSeries([2018,2022],[91212,120134])),
    #       ("Facility-based ART dispensing",at.TimeSeries([2018,2022],[274906358,362072411])),
    #       ("Decentralized delivery",at.TimeSeries([2018,2022],[4604686,6064719])),
    #       ("Adherence clubs",at.TimeSeries([2018,2022],[14197414,18699066])),
    #       ("PMTCT",at.TimeSeries([2018,2022],[15727557,20714379]))])
    alloc = sc.odict([
            ("Client-initiated clinic-based testing",at.TimeSeries([2017,2022],[53354825,70272330])),
            ("Provider-initiated testing",at.TimeSeries([2017,2022],[1958157,2579040])),
            ("Mobile testing",at.TimeSeries([2017,2022],[1937319,2551596])),
            ("Door-to-door testing",at.TimeSeries([2017,2022],[1430195,1883675])),
            ("Workplace testing",at.TimeSeries([2017,2022],[670563,883182])),
            ("Youth-friendly  SRH testing",at.TimeSeries([2017,2022],[716945,944271])),
            ("Self-testing",at.TimeSeries([2017,2022],[847315,1115978])),
            ("CD4 testing",at.TimeSeries([2017,2022],[3995486,5262357])),
            ("Community support - link to care",at.TimeSeries([2017,2022],[350468,461593])),
            ("Additional education (prof)",at.TimeSeries([2017,2022],[231217,304530])),
            ("Additional education (lay)",at.TimeSeries([2017,2022],[16105,21211])),
            ("Classic ART initiation",at.TimeSeries([2017,2022],[1558316,2052420])),
            ("Fast-track ART initiation",at.TimeSeries([2017,2022],[376159,495429])),
            ("Same day ART initiation",at.TimeSeries([2017,2022],[97778,128781])),
            ("Community support - adherence",at.TimeSeries([2017,2022],[910142,1198725])),
            ("WhatsApp messaging - adherence",at.TimeSeries([2017,2022],[449,592])),
            ("Tracing of ART clients",at.TimeSeries([2017,2022],[825759,1087587])),
            ("Enhanced adherence (prof)",at.TimeSeries([2017,2022],[1325445,1745710])),
            ("Enhanced adherence (lay)",at.TimeSeries([2017,2022],[91212,120134])),
            ("Facility-based ART dispensing",at.TimeSeries([2017,2022],[274906358,362072411])),
            ("Decentralized delivery",at.TimeSeries([2017,2022],[4604686,6064719])),
            ("Adherence clubs",at.TimeSeries([2017,2022],[14197414,18699066])),
            ("PMTCT",at.TimeSeries([2017,2022],[15727557,20714379]))])

    instructions = at.ProgramInstructions(alloc=alloc,start_year=2017.) # Instructions for default spending

    # SET ADJUSTMENTS
    adjustments = []
    for progname in P.progsets[0].programs.keys():
        if progname != 'PMTCT':
            adjustments.append(at.SpendingAdjustment(progname, [2017,2022], 'rel', 0., 100.))
        else:
            adjustments.append(at.SpendingAdjustment('PMTCT', [2017,2022], 'rel', 0., 100.))

    # SET CONSTRAINTS - THIS INCLUDES BUDGET RAMP-UP
    constraints = at.TotalSpendConstraint(t=[2017,2022],total_spend=[380129870, 500659714]) # Cap total spending in all years

    # SET CASCADE MEASURABLE
    measurables = at.MaximizeCascadeConversionRate('HIV care cascade', [2022],
                                                   pop_names='all')

    # DO OPTIMIZATION
    optimization = at.Optimization(name='default', adjustments=adjustments, measurables=measurables,
                                   constraints=constraints) #, method='pso')


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
    d = at.PlotData.programs([optimized_result, unoptimized_result], t_bins=[2017, 2023])
    at.plot_series(at.PlotData.programs(optimized_result),plot_type='stacked')
    at.plot_series(at.PlotData.programs(unoptimized_result),plot_type='stacked')
    at.plot_bars(d, stack_outputs='all')

    # PRINT EPI DETAILS
    inf_bl = sc.odict()
    inf_op = sc.odict()
    dea_bl = sc.odict()
    dea_op = sc.odict()
    for pname in unoptimized_result.pop_names:
        inf_bl[pname] = unoptimized_result.get_variable(pname, 'num_acq')[0].vals
        inf_op[pname] = optimized_result.get_variable(pname, 'num_acq')[0].vals
        dea_bl[pname] = unoptimized_result.get_variable(pname, 'num_hiv_deaths')[0].vals
        dea_op[pname] = optimized_result.get_variable(pname, 'num_hiv_deaths')[0].vals
    indices = [4,8,12,16,20,24]

    print("Baseline infections by year: %s" % (inf_bl[:][:,indices].sum(axis=0)))
    print(" Optimal infections by year: %s" % (inf_op[:][:,indices].sum(axis=0)))
    print("    Baseline deaths by year: %s" % (dea_bl[:][:,indices].sum(axis=0)))
    print("     Optimal deaths by year: %s" % (dea_op[:][:,indices].sum(axis=0)))

    print("Baseline infections 2017-2022: %s" % (inf_bl[:][:,indices].sum()))
    print(" Optimal infections 2017-2022: %s" % (inf_op[:][:,indices].sum()))
    print("      Reduction in infections: %s" % ((inf_bl[:][:,indices].sum()-inf_op[:][:,indices].sum())/inf_bl[:][:,indices].sum()))
    print("    Baseline deaths 2017-2022: %s" % (dea_bl[:][:,indices].sum()))
    print("     Optimal deaths 2017-2022: %s" % (dea_op[:][:,indices].sum()))
    print("          Reduction in deaths: %s" % ((dea_bl[:][:,indices].sum()-dea_op[:][:,indices].sum())/dea_bl[:][:,indices].sum()))

    # EXPORT RESULTS
#    at.export_results(P.results, 'hiv_southafrica_results_0103.xlsx')
