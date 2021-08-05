#  Copyright (c) 2021 European Union
#  *
#  Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
#  European Commission – subsequent versions of the EUPL (the "Licence");
#  You may not use this work except in compliance with the Licence.
#  You may obtain a copy of the Licence at:
#  *
#  https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
#  *
#  Unless required by applicable law or agreed to in writing,
#  software distributed under the Licence is distributed on an "AS IS" basis,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the Licence for the specific language governing permissions and limitations
#  under the Licence.
#
#

import pandas as pd
import numpy as np
import os
from . import movement as mvt
from . import models as md
from . import global_parameters as gp


def run_loop():

    length = gp.length
    width = gp.width
    iterations = gp.iterations
    freq = gp.freq

    out_dir = 'results/car_following'

    models_list = ["FSM", "CC_human_driver", "RSS"]

    for model in models_list:
        print("Selected model:", model)
        model_functions = {"FSM": [md.FSM_check_safety, md.FSM_react, md.FSM_distance],
                           "CC_human_driver": [md.CC_check_safety, md.CC_react, md.CC_distance],
                           "RSS": [md.RSS_check_safety, md.RSS_react, md.RSS_distance]}

        max_decelerations = np.arange(0.05, 1, 0.05)
        velocities = np.arange(12, 130, 2)

        check = model_functions[model][0]
        react = model_functions[model][1]
        initial_dist = model_functions[model][2]

        result_d = {'max_deceleration': [], 'velocity': [], 'Crash': [], 'initial_distance': [], 'speed_difference': [],
                    'CFS': [], 'PFS': []}

        imaginary_veh = mvt.create_profile_decel(np.array([42 + length, 0]), 0, 10, 10, 10)

        for max_dec in max_decelerations:
            for ur in velocities:

                initial_distance = initial_dist(imaginary_veh, ur / 3.6)

                init_pos_c = np.array([initial_distance + length, 0])
                init_pos_ego = np.array([0, 0])
                init_long_speed = ur / 3.6
                deceleration = gp.g * max_dec

                cut_in_veh = mvt.create_profile_decel(init_pos_c, deceleration, init_long_speed, iterations, freq)
                ego_veh = mvt.create_profile_decel(init_pos_ego, 0, init_long_speed, iterations, freq)

                cut_in_veh.width = width
                cut_in_veh.length = length
                ego_veh.width = width
                ego_veh.length = length

                vehs = [ego_veh, cut_in_veh]

                speed_difference = 0
                CFS, PFS = 0., 0.
                ego_veh.cfs, ego_veh.pfs = 0, 0
                for i in range(iterations - 1):

                    mvt.control(ego_veh, cut_in_veh, freq, check, react, i)
                    CFS = max(CFS, ego_veh.cfs)
                    PFS = max(PFS, ego_veh.pfs)
                    if ego_veh.speed_profile_long[i] == 0:
                        ego_veh.pos_profile_long[i:] = ego_veh.pos_profile_long[i]
                        ego_veh.speed_profile_long[i:] = 0
                        break
                    if ego_veh.crash:
                        speed_difference = ego_veh.speed_profile_long[i] - cut_in_veh.speed_profile_long[i]
                        break
                result_d['max_deceleration'].append(max_dec)
                result_d['velocity'].append(ur)
                result_d['Crash'].append(ego_veh.crash)
                result_d['initial_distance'].append(initial_distance)
                result_d['speed_difference'].append(speed_difference)
                result_d['CFS'].append(CFS)
                result_d['PFS'].append(PFS)
        df = pd.DataFrame(result_d)

        if model != 'FSM':
            del df['CFS'], df['PFS']

        if not(os.path.exists(out_dir)):
            os.mkdir(out_dir)
        df.to_csv(out_dir + '/' + model + '_car_following.csv', index=False)
