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
    wandering_zone = gp.wandering_zone

    out_dir = 'results/cut_out'

    models_list = ["FSM", "CC_human_driver", "RSS"]

    velocities = np.arange(10, 132, 10)
    front_distances = np.arange(2, 152, 5)
    lateral_velocities = -np.arange(0.1, 3.1, 0.2)

    for model in models_list:
        print("Selected model:", model)

        model_functions = {"FSM": [md.FSM_check_safety, md.FSM_react, md.FSM_distance],
                           "CC_human_driver": [md.CC_check_safety, md.CC_react, md.CC_distance],
                           "RSS": [md.RSS_check_safety, md.RSS_react, md.RSS_distance]}

        check = model_functions[model][0]
        react = model_functions[model][1]
        initial_dist = model_functions[model][2]

        imaginary_veh = mvt.create_profile_decel(np.array([42 + length, 0]), 0, 10, 10, 10)

        result_d = {'velocity': [], 'front_distance': [], 'lateral_velocities': [], 'Crash': [],
                    'Crash_front': [], 'initial_distance': [], 'PFS': [], 'CFS': []}


        for ur in velocities:
            for dx0_f in front_distances:
                for lateral_speed_cut_out in lateral_velocities:

                    initial_distance = initial_dist(imaginary_veh, ur / 3.6)

                    init_pos_c = np.array([initial_distance + length, 4])
                    init_pos_ego = np.array([0, 0])
                    init_long_speed = ur / 3.6  # 9.

                    init_pos_st = np.array([init_pos_c[0] + dx0_f + length, 0])

                    stopped_veh = mvt.create_profile_decel(init_pos_st, 0, 0, iterations, freq)
                    cut_out_veh = mvt.create_profile_cutting_in(init_pos_c, init_long_speed, lateral_speed_cut_out,
                                                                iterations, freq)
                    cut_out_veh.pos_profile_lat = cut_out_veh.pos_profile_lat - 4
                    ego_veh = mvt.create_profile_decel(init_pos_ego, 0, init_long_speed, iterations, freq)

                    cut_out_veh.width = width
                    cut_out_veh.length = length
                    ego_veh.width = width
                    ego_veh.length = length

                    vehs = [ego_veh, cut_out_veh, stopped_veh]

                    ego_veh.cfs, ego_veh.pfs = 0, 0

                    u = 0
                    for i in range(iterations - 1):
                        if abs(stopped_veh.pos_profile_lat[i] - cut_out_veh.pos_profile_lat[
                            i]) - stopped_veh.width / 2 - cut_out_veh.width / 2 < 0 and abs(
                            stopped_veh.pos_profile_long[i] - cut_out_veh.pos_profile_long[
                                i]) - stopped_veh.length / 2 - \
                                cut_out_veh.length / 2 < 0:
                            cut_out_veh.crash = True
                            cut_out_veh.speed_profile_long[i:] = 0
                            cut_out_veh.speed_profile_lat[i:] = 0
                            cut_out_veh.pos_profile_lat[i:] = cut_out_veh.pos_profile_lat[i]
                            cut_out_veh.pos_profile_long[i:] = cut_out_veh.pos_profile_long[i]

                        if cut_out_veh.crash:
                            mvt.control(ego_veh, cut_out_veh, freq, check, react, i)
                            CFS = 0
                            PFS = 0

                        elif cut_out_veh.pos_profile_lat[i] < wandering_zone:
                            mvt.control(ego_veh, stopped_veh, freq, check, react, i)
                            if u == 0:
                                u = 1
                                CFS = ego_veh.cfs
                                PFS = ego_veh.pfs

                        if ego_veh.speed_profile_long[i] == 0:
                            ego_veh.pos_profile_long[i:] = ego_veh.pos_profile_long[i]
                            ego_veh.speed_profile_long[i:] = 0
                            break

                    result_d['velocity'].append(ur)
                    result_d['front_distance'].append(dx0_f)
                    result_d['lateral_velocities'].append(lateral_speed_cut_out)
                    result_d['Crash'].append(ego_veh.crash)
                    result_d['Crash_front'].append(cut_out_veh.crash)
                    result_d['initial_distance'].append(initial_distance)
                    result_d['CFS'].append(CFS)
                    result_d['PFS'].append(PFS)

        df = pd.DataFrame(result_d)
        if model != 'FSM':
            del df['CFS'], df['PFS']

        if not (os.path.exists(out_dir)):
            os.mkdir(out_dir)
        df.to_csv(out_dir + '/' + model + '_cut_out.csv', index=False)

    exit(0)
