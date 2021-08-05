# Regulation 157 Safety Models

This document describes how to use the following repository to 
investigate the behavior of the proposed safety models for UNECE R157.

Three reference scenarios are implemented in the current formulation:

1. 'cut_in';
2. 'cut_out';
3. 'car_following'.

Four models are here discussed:

1. 'FSM' : Fuzzy Safety Model [1];
2. 'RSS' : Responsibility Sensitive Safety [2];
3. 'CC_human_driver' : [3];
4. 'Reg157' : [4];

The python script 'safety_check_runner.py' provides the possibility of selecting
three types of analyses: 

1. 'one_case' : enables selecting one concrete scenario, one model, and 
   visually inspecting the result of the simulation;
2. 'comparison' : aims at a systematic investigation of the safety models 
   on a selection of logical scenario and then stores data for later processing;
3. 'post_processing' : provides the possibility of visually inspect the results of 
    the previously executed 'comparison' scenario.

The 'safety_check_runner.py' can be launched either via command line providing 
the minimum number of arguments or called from another python script as shown 
in the 'example.py' file.


### One Case
The 'one_case' analysis is a single simulation which involves a concrete scenario with 
a specified safety model. 

An example command line instruction to execute a 'cut_in' scenario is:

`python safety_check_runner.py one_case cut_in` 

The default model for the 'one_case' analysis is FMS, however other models can be 
executed too as:

`python safety_check_runner.py one_case cut_in model=RSS`

The concrete scenarios can be modified via passing optional parameters.<br> 
In particular, the following parameters can be adjusted on the fly:
- the *initial velocity* of the simulation can be set via passing `initial_speed` optional 
command in (km/h):

`python safety_check_runner.py one_case cut_in model=RSS initial_speed=50`

- the leader *deceleration* of car-following scenario can be adjusted (in m/s<sup>2</sup>) as: 

`python safety_check_runner.py one_case car_following model=Reg157 deceleration=3`

- the *obstacle speed* in the cut-in scenario can be updated (in km/h, default=) via:

`python safety_check_runner.py one_case cut_in model=CC_human_driver obstacle_speed=20`

- the *lateral speed* of cut-out and cut-in maneuvers can be adjusted (in m/s, default=-1.) as:

`python safety_check_runner.py one_case cut_in model=CC_human_driver lateral_speed=-2.`

- the *front distance* of cut-out and cut-in maneuvers can be adjusted (in m, default=50) as:

`python safety_check_runner.py one_case cut_in model=FSM front_distance=30`    

### Comparison

The comparison cases loop over the safety models for a range concrete scenarios belonging to 
the same class.

Three alternatives are possible corresponding to the 

- cut-in scenario:

`python safety_check_runner.py comparison cut_in`

- cut-out scenario

`python safety_check_runner.py comparison cut_out`

- car-following scenario

`python safety_check_runner.py comparison car_following`

No optional parameters can be provided in the 'comparison' analysis. 

### Post processing

Eventually, a post processing analysis can be run to save/visualize the results 
of the comparisons.

- cut-in post-processing:

`python safety_check_runner.py post_processing cut_in`

    - a detailed analysis on TTC is possible for the cut_in case by passing a safety model specification  
     
        `python safety_check_runner.py post_processing cut_in model=RSS` 

    - a detailed analysis on FSM criticality is possible for the cut_in case by passing the FSM model specification  
     
        `python safety_check_runner.py post_processing cut_in model=FSM` 

- cut-out scenario

`python safety_check_runner.py post_processing cut_out`

- car-following scenario

`python safety_check_runner.py post_processing car_following`

Finally, a 'save_image' boolean can be passed to automatically store the image on the 
hard drive instead of the graphical visualization only.

`python safety_check_runner.py post_processing car_following save_image=True`

## Dependencies
The following python packages are required to run the models:
- pandas (New BSD License, 3-clause);
- numpy (New BSD License, 3-clause);
- numba (BSD 2-clause);
- scipy (BSD);
- matplotlib (BSD).


## References
[1] Mattas, Konstantinos, et al. "Fuzzy Surrogate Safety Metrics for real-time assessment of rear-end collision risk. 
    A study based on empirical observations." Accident Analysis & Prevention 148 (2020): 105794.

[2] Shalev-Shwartz, Shai, Shaked Shammah, and Amnon Shashua. 
    "On a formal model of safe and scalable self-driving cars." 
    arXiv preprint arXiv:1708.06374 (2017).

[3] UNECE Reg 157 Annex 4 - Appendix 3

[4] UNECE Reg 157 Paragraph 5.2.5.2.