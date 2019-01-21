
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
# "runsim",             # Only required if you want to check the calibration
# "plotcascade",        # Only required if you want to check the calibration
# "makeblankprogbook",  # Only required if framework has changed or if you want to use different programs
"loadprogbook",         # Always required
# "reconcile",          # Only required the first time you load a program book
"runsim_programs",    # Only required if you want to check the programs
# "budget_scenarios",   # Only required if you want to check the programs
# "optimize",             # Main purpose of script
]

load_reconciled = True

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

    reconciled_progset.save("hiv_southafrica_progbook_reconciled.xlsx")

    print(progset_comparison)
    print(parameter_comparison)

if "runsim_programs" in torun:

    parset = P.parsets[0]
    original_progset = P.progsets[0]
    instructions = at.ProgramInstructions(start_year=2016.)
    parresults = P.run_sim(parset="default", result_name="default-noprogs", store_results=True)
    progresults = P.run_sim(parset="default", progset='default', progset_instructions=instructions,
                            result_name="default-progs", store_results=True)
    at.plot_multi_cascade([parresults, progresults], year=[2017])


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
    alloc = sc.odict([
            ("Client-initiated clinic-based testing",at.TimeSeries([2017,2018,2019,2020,2021,2022],[52472254,55443655,62508819,75795653,79585435,83564707])),#???
            ("Provider-initiated testing",at.TimeSeries([2017,2018,2019,2020,2021,2022],[1925766,2034818,2294114,2781750,2920837,3066879])),
            ("Mobile testing",at.TimeSeries([2017,2018,2019,2020,2021,2022],[1905274,2013166,2269703,2752150,2889757,3034245])),
            ("Door-to-door testing",at.TimeSeries([2017,2018,2019,2020,2021,2022],[1406539,1486188,1675573,2031731,2133318,2239984])),
            ("Workplace testing",at.TimeSeries([2017,2018,2019,2020,2021,2022],[659472,696817,785612,952601,1000231,1050243])),
            ("Youth-friendly  SRH testing",at.TimeSeries([2017,2018,2019,2020,2021,2022],[705089,745016,839954,1018494,1069418,1122889])),
            ("Self-testing",at.TimeSeries([2017,2018,2019,2020,2021,2022],[833300,880488,992689,1203694,1263879,1327073])),
            ("CD4 testing",at.TimeSeries([2017,2018,2019,2020,2021,2022],[855224,903654,1018806,1235363,1297131,1361988])),
            ("Community support - link to care",at.TimeSeries([2017,2018,2019,2020,2021,2022],[448284,473670,534029,647542,679919,713915])),
            ("Additional education (prof)",at.TimeSeries([2017,2018,2019,2020,2021,2022],[803548,849051,957245,1160717,1218753,1279690])),
            ("Additional education (lay)",at.TimeSeries([2017,2018,2019,2020,2021,2022],[281242,297168,335036,406251,426563,447892])), #???
            ("Classic ART initiation",at.TimeSeries([2017,2018,2019,2020,2021,2022],[1453013,1535294,1730936,2098863,2203806,2313996])),
            ("Fast-track ART initiation",at.TimeSeries([2017,2018,2019,2020,2021,2022],[145845,154104,173742,210672,221206,232266])),#???
            ("Same day ART initiation",at.TimeSeries([2017,2018,2019,2020,2021,2022],[72924,77053,86872,105338,110605,116135])),
            ("Community support - adherence",at.TimeSeries([2017,2018,2019,2020,2021,2022],[1404456,1483988,1673092,2028723,2130160,2236668])),
            ("WhatsApp messaging - adherence",at.TimeSeries([2017,2018,2019,2020,2021,2022],[10168,10744,12113,14688,15422,16193])),
            ("Tracing of ART clients",at.TimeSeries([2017,2018,2019,2020,2021,2022],[829899,876895,988637,1198782,1258721,1321657])),
            ("Enhanced adherence (prof)",at.TimeSeries([2017,2018,2019,2020,2021,2022],[1312675,1387009,1563755,1896145,1990953,2090500])),#???
            ("Enhanced adherence (lay)",at.TimeSeries([2017,2018,2019,2020,2021,2022],[157523,166443,187652,227540,238917,250863])),#???
            ("Facility-based ART dispensing",at.TimeSeries([2017,2018,2019,2020,2021,2022],[152880716,161538050,182122785,220834684,231876419,243470240])),#???
            ("Decentralized delivery",at.TimeSeries([2017,2018,2019,2020,2021,2022],[24543302,25933141,29237792,35452558,37225186,39086445])),
            ("Adherence clubs",at.TimeSeries([2017,2018,2019,2020,2021,2022],[11385988,12030754,13563828,16446947,17269294,18132759])),
            ("PMTCT",at.TimeSeries([2017,2018,2019,2020,2021,2022],[26006258,27478942,30980573,37565783,39444073,41416276]))])

    instructions = at.ProgramInstructions(alloc=alloc,start_year=2017) # Instructions for default spending

    # SET ADJUSTMENTS
    adjustments = []
    for progname in P.progsets[0].programs.keys():
        adjustments.append(at.SpendingAdjustment(progname, [2017,2018,2019,2020,2021,2022], 'rel', 0., 100.))

    # SET CONSTRAINTS - THIS INCLUDES BUDGET RAMP-UP
    constraints = at.TotalSpendConstraint(t=[2017,2018,2019,2020,2021,2022],total_spend=[282498759,298496108,336533358,408066668,428470001,449893502]) # Cap total spending in all years

    # SET CASCADE MEASURABLE
    measurables = at.MaximizeCascadeConversionRate('HIV care cascade', [2022],
                                                   pop_names='all')  # NB. make sure the objective year is later than the program start year, otherwise no time for any changes

    # DO OPTIMIZATION
    optimization = at.Optimization(name='default', adjustments=adjustments, measurables=measurables,
                                   constraints=constraints, maxtime=10) #, method='pso') # Use PSO because this example seems a bit susceptible to local minima with ASD


    # COLLECT RESULTS
    unoptimized_result = P.run_sim(parset=P.parsets["default"], progset=P.progsets['default'],
                                   progset_instructions=instructions, result_name="unoptimized", store_results=True)
    optimized_instructions = at.optimize(P, optimization, parset=P.parsets["default"],
                                         progset=P.progsets['default'], instructions=instructions)
    optimized_result = P.run_sim(parset=P.parsets["default"], progset=P.progsets['default'],
                                 progset_instructions=optimized_instructions, result_name="optimized", store_results=True)


    # MAKE CASCADE PLOT
    at.plot_multi_cascade([unoptimized_result, optimized_result], year=[2022], pops=['Males 25-34'])

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
    at.export_results(P.results, 'hiv_southafrica_results_0103.xlsx')
