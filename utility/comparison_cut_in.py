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


def run_loop(speed_range):

    length = gp.length
    width = gp.width
    iterations = gp.iterations
    freq = gp.freq

    '''speed_range can be high or low '''
    out_dir = 'results/cut_in_' + speed_range + '_speed/'
    print('Cut-in case: ', speed_range)

    models_list = ["FSM", "CC_human_driver", "RSS", "Reg157"]

    for model in models_list:
        print("Selected model:", model)
        model_functions = {"FSM": [md.FSM_check_safety, md.FSM_react],
                           "CC_human_driver": [md.CC_check_safety_cut_in, md.CC_react],
                           "RSS": [md.RSS_check_safety, md.RSS_react],
                           "Reg157": [md.Reg157_check_safety_cut_in, md.Reg157_react]}

        check = model_functions[model][0]
        react = model_functions[model][1]

        if speed_range == 'high':
            long_dists = np.arange(1, 120, 2)
            ego_speeds = [70, 90, 110, 130]
            cut_in_speeds_step = 30
        elif speed_range == 'low':
            long_dists = np.arange(1, 60, 1)
            ego_speeds = [10, 20, 30, 40, 50, 60]
            cut_in_speeds_step = 10
        else:
            print("speed_range can be 'high' or 'low' ")
            exit(1)

        lat_vels = np.arange(0., 1.8, 0.1)

        for ego_speed in ego_speeds:
            for cut_in_speed in range(10, ego_speed, cut_in_speeds_step):

                result_d = {'long_dist': [], 'lat_vel': [], 'Crash': [], 'Crash type': [], 'minTTC': [], 'PFS': [],
                            'CFS': []}

                for long_dist in long_dists:
                    for lat_vel in lat_vels:
                        init_pos_c = np.array([long_dist + length, 1.6 + width])
                        init_pos_ego = np.array([0, 0])
                        init_long_speed_c = cut_in_speed / 3.6  # 9.
                        init_long_speed_ego = ego_speed / 3.6  # 15.
                        lateral_speed = -lat_vel
                        lat_accel = -1.5
                        cut_in_veh = mvt.create_profile_cutting_in(init_pos_c, init_long_speed_c, lateral_speed, iterations,
                                                                   freq)
                        ego_veh = mvt.create_profile_cutting_in(init_pos_ego, init_long_speed_ego, 0, iterations, freq)

                        ego_veh.large_TTC = False

                        '''new speeds'''
                        lat_speed_append = np.arange(0, lateral_speed, lat_accel / freq)
                        lon_speed_append = np.array([init_long_speed_c] * len(lat_speed_append))
                        '''new positions'''
                        lat_pos_append = np.append(np.cumsum(-lat_speed_append[::-1] / freq)[::-1] + init_pos_c[1],
                                                   init_pos_c[1])
                        lon_pos_append = np.append(np.cumsum(-lon_speed_append[::-1] / freq)[::-1] + init_pos_c[0],
                                                   init_pos_c[0])

                        '''add one needed'''
                        lat_speed_append = np.append(lat_speed_append, [lateral_speed])
                        lon_speed_append = np.append(lon_speed_append, [init_long_speed_c])

                        '''save to cutting in'''
                        cut_in_veh.speed_profile_long = np.append(lon_speed_append, cut_in_veh.speed_profile_long)
                        cut_in_veh.speed_profile_lat = np.append(lat_speed_append, cut_in_veh.speed_profile_lat)
                        cut_in_veh.pos_profile_long = np.append(lon_pos_append, cut_in_veh.pos_profile_long)
                        cut_in_veh.pos_profile_lat = np.append(lat_pos_append, cut_in_veh.pos_profile_lat)

                        '''new speeds'''
                        lat_speed_append = np.array([0] * (len(lat_speed_append) - 1))
                        lon_speed_append = np.array([init_long_speed_ego] * len(lat_speed_append))
                        '''new positions'''
                        lat_pos_append = np.append(np.cumsum(-lat_speed_append[::-1] / freq)[::-1] + init_pos_ego[1],
                                                   init_pos_ego[1])
                        lon_pos_append = np.append(np.cumsum(-lon_speed_append[::-1] / freq)[::-1] + init_pos_ego[0],
                                                   init_pos_ego[0])

                        '''add one needed'''
                        lat_speed_append = np.append(lat_speed_append, [0])
                        lon_speed_append = np.append(lon_speed_append, [init_long_speed_ego])

                        '''save to ego'''
                        ego_veh.speed_profile_long = np.append(lon_speed_append, ego_veh.speed_profile_long)
                        ego_veh.speed_profile_lat = np.append(lat_speed_append, ego_veh.speed_profile_lat)
                        ego_veh.pos_profile_long = np.append(lon_pos_append, ego_veh.pos_profile_long)
                        ego_veh.pos_profile_lat = np.append(lat_pos_append, ego_veh.pos_profile_lat)

                        cut_in_veh.width = width
                        cut_in_veh.length = length
                        ego_veh.width = width
                        ego_veh.length = length

                        vehs = [ego_veh, cut_in_veh]

                        CFS = 0
                        PFS = 0
                        for i in range(iterations + len(lat_speed_append) - 1):
                            ego_veh.cfs, ego_veh.pfs = 0, 0
                            mvt.control(ego_veh, cut_in_veh, freq, check, react, i)
                            if ego_veh.large_TTC:
                                break
                            CFS = max(ego_veh.cfs, CFS)
                            PFS = max(ego_veh.pfs, PFS)

                        result_d['long_dist'].append(long_dist)
                        result_d['lat_vel'].append(lat_vel)
                        result_d['Crash'].append(ego_veh.crash)
                        result_d['Crash type'].append(ego_veh.crash_type)
                        result_d['CFS'].append(CFS)
                        result_d['PFS'].append(PFS)

                        '''2d TTC'''
                        headway_lat = (abs(np.array(ego_veh.pos_profile_lat) - np.array(
                            cut_in_veh.pos_profile_lat)) - ego_veh.width / 2 - cut_in_veh.width / 2)
                        headway_lon = ((np.array(cut_in_veh.pos_profile_long) - np.array(
                            ego_veh.pos_profile_long)) - ego_veh.length / 2 - cut_in_veh.length / 2)
                        rel_speed_lon = np.array(ego_veh.speed_profile_long) - np.array(cut_in_veh.speed_profile_long)
                        rel_speed_lat = - np.array(cut_in_veh.speed_profile_lat)
                        rel_speed_lat[rel_speed_lat == 0] = 0.001
                        max_ttc = 4

                        length_of_series = len(rel_speed_lat)
                        ttc_lon = np.array([max_ttc] * length_of_series)
                        ttc_lat = np.array([max_ttc] * length_of_series)

                        ttc_lon = np.minimum(headway_lon / rel_speed_lon, ttc_lon)
                        ttc_lon[rel_speed_lon < 0] = max_ttc
                        ttc_lon[headway_lon < - ego_veh.length - cut_in_veh.length] = 10
                        ttc_lon[(headway_lon > - ego_veh.length - cut_in_veh.length) & (headway_lon <= 0)] = 0

                        ttc_lat = np.minimum(headway_lat / rel_speed_lat, ttc_lat)
                        ttc_lat[headway_lat < 0] = 0

                        ttc = np.maximum(ttc_lon, ttc_lat)
                        result_d['minTTC'].append(np.nanmin(ttc))

                df = pd.DataFrame(result_d)
                if model != 'FSM':
                    del df['CFS'], df['PFS']

                if not (os.path.exists(out_dir)):
                    os.mkdir(out_dir)
                df.to_csv(out_dir + '/' + model + '_' + str(ego_speed) + '_' + str(cut_in_speed) + '.csv', index=False)
