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

import numpy as np
import matplotlib.pyplot as plt
from post_processing import live_graph as li
from . import movement as mvt
from . import models as md
from . import global_parameters as gp


def run_one_case(use_model, **kwargs):

    length = gp.length
    width = gp.width
    iterations = gp.iterations
    freq = gp.freq
    wandering_zone = gp.wandering_zone

    # default parameters
    ur = float(kwargs.get('initial_speed', 50))
    lateral_speed_cut_out = float(kwargs.get('lateral_speed', -1.))
    dx0_f = float(kwargs.get('front_distance', 50))

    print('Starting speed cut out: ' + str(ur) + ' (km/h)')
    print('Lateral speed cut out: ' + str(lateral_speed_cut_out) + ' (m/s)')
    print('Front distance cut out: ' + str(dx0_f) + ' (m)')

    imaginary_veh = mvt.create_profile_decel(np.array([42 + length, 0]), 0, 10, 10, 10)

    init_pos_ego = np.array([0, 0])
    init_long_speed = ur / 3.6

    if use_model == 'FSM':
        check = md.FSM_check_safety
        react = md.FSM_react
        dist  = md.FSM_distance
        print("Selected model: FSM")
    elif use_model == 'CC_human_driver':
        check = md.CC_check_safety
        react = md.CC_react
        dist  = md.CC_distance
        print("Selected model: CC_human_driver")
    elif use_model == 'RSS':
        check = md.RSS_check_safety
        react = md.RSS_react
        dist  = md.RSS_distance
        print("Selected model: RSS")
    elif use_model == 'Reg157':
        check = md.Reg157_check_safety
        react = md.Reg157_react
        dist  = md.CC_distance
        print("Selected model: Reg157")
    else:
        print("Error, unsupported safety model\n")
        exit(4)

    initial_distance = dist(imaginary_veh, ur / 3.6)
    init_pos_c = np.array([initial_distance + length, 4])

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

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    plt.axis('off')
    vehs = [ego_veh, cut_out_veh, stopped_veh]

    CFS = []
    PFS = []

    ego_veh.cfs, ego_veh.pfs = 0, 0

    for i in range(iterations - 1):
        CFS.append(ego_veh.cfs)
        PFS.append(ego_veh.pfs)

        if abs(stopped_veh.pos_profile_lat[i] - cut_out_veh.pos_profile_lat[
            i]) - stopped_veh.width / 2 - cut_out_veh.width / 2 < 0 and abs(
            stopped_veh.pos_profile_long[i] - cut_out_veh.pos_profile_long[i]) - stopped_veh.length / 2 - \
                cut_out_veh.length / 2 < 0:
            cut_out_veh.crash = True
            cut_out_veh.speed_profile_long[i:] = 0
            cut_out_veh.speed_profile_lat[i:] = 0
            cut_out_veh.pos_profile_lat[i:] = cut_out_veh.pos_profile_lat[i]
            cut_out_veh.pos_profile_long[i:] = cut_out_veh.pos_profile_long[i]

        if cut_out_veh.crash:
            mvt.control(ego_veh, cut_out_veh, freq, check, react, i)

        elif cut_out_veh.pos_profile_lat[i] < wandering_zone:
            mvt.control(ego_veh, stopped_veh, freq, check, react, i)

        li.plot_map_cout_out(vehs, ax1, i)
        if ego_veh.crash == 1:
            fig.patch.set_facecolor((1, 0, 0, 0.2))
        if ego_veh.speed_profile_long[i] == 0:
            ego_veh.pos_profile_long[i:] = ego_veh.pos_profile_long[i]
            ego_veh.speed_profile_long[i:] = 0
            break

    print('Crash = ', ego_veh.crash)

    plt.figure('Trajectory')
    plt.plot(cut_out_veh.pos_profile_long, cut_out_veh.pos_profile_lat, 'rx', label='Cut-in vehicle')
    plt.plot(ego_veh.pos_profile_long, ego_veh.pos_profile_lat, 'bx', label='Ego vehicle')
    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    plt.legend()

    plt.figure('Speed')
    plt.plot(np.linspace(0, (iterations-1)/freq, iterations), ego_veh.speed_profile_long, '-bx', label='Ego vehicle')
    plt.plot(np.linspace(0, (iterations-1)/freq, iterations), cut_out_veh.speed_profile_long, 'r', label='Cut-in vehicle')
    plt.xlabel('Time (s)')
    plt.ylabel('Speed (m/s)')
    plt.legend()

    plt.figure('Acceleration')
    plt.plot(np.linspace(0, (iterations-2)/freq, iterations-1), np.diff(ego_veh.speed_profile_long) * freq, '-bx', label='Ego vehicle')
    plt.xlabel('Time (s)')
    plt.ylabel('Acceleration (m/s$^2$)')
    plt.legend()

    if use_model == 'FSM':
        plt.figure('Fuzzy metrics')
        plt.plot(CFS, 'r', label='CFS')
        plt.plot(PFS, 'b', label='PFS')
        plt.legend()

    plt.show()
