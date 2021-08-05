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

    ur = float(kwargs.get('initial_speed', 50))
    deceleration = float(kwargs.get('deceleration', gp.g * 0.5))

    print('Starting speed car following: ' + str(ur) + ' (km/h)')
    print('Deceleration car following: ' + str(deceleration) + ' (m/s^2)')

    imaginary_veh = mvt.create_profile_decel(np.array([42 + gp.length, 0]), 0, 10, 10, 10)

    iterations = gp.iterations
    freq = gp.freq

    if use_model == 'FSM':
        check = md.FSM_check_safety
        react = md.FSM_react
        initial_distance = md.FSM_distance(imaginary_veh, ur / 3.6)
        print("Selected model: FSM")
    elif use_model == 'CC_human_driver':
        check = md.CC_check_safety
        react = md.CC_react
        initial_distance = md.CC_distance(imaginary_veh, ur / 3.6)
        print("Selected model: CC_human_driver")
    elif use_model == 'RSS':
        check = md.RSS_check_safety
        react = md.RSS_react
        initial_distance = md.RSS_distance(imaginary_veh, ur / 3.6)
        print("Selected model: RSS")
    elif use_model == 'Reg157':
        check = md.Reg157_check_safety
        react = md.Reg157_react
        initial_distance = md.CC_distance(imaginary_veh, ur / 3.6)
        print("Selected model: Reg157")
    else:
        print("Error, unsupported safety model\n")
        exit(4)

    init_pos_c = np.array([initial_distance + gp.length, 0])
    init_pos_ego = np.array([0, 0])
    init_long_speed = ur / 3.6

    leader_veh = mvt.create_profile_decel(init_pos_c, deceleration, init_long_speed, iterations, freq)
    ego_veh = mvt.create_profile_decel(init_pos_ego, 0, init_long_speed, iterations, freq)

    leader_veh.width = gp.width
    leader_veh.length = gp.length
    ego_veh.width = gp.width
    ego_veh.length = gp.length

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    plt.axis('off')
    vehs = [ego_veh, leader_veh]

    for i in range(iterations - 1):

        if i == 1:
            plt.pause(2)

        mvt.control(ego_veh, leader_veh, freq, check, react, i)
        li.plot_map(vehs, ax1, i)
        if ego_veh.crash == 1:
            fig.patch.set_facecolor((1, 0, 0, 0.2))
        if ego_veh.speed_profile_long[i] == 0:
            ego_veh.pos_profile_long[i:] = ego_veh.pos_profile_long[i]
            ego_veh.speed_profile_long[i:] = 0
            break

    print('Crash = ', ego_veh.crash)

    ''' post processing '''
    plt.figure('Trajectory')
    plt.plot(leader_veh.pos_profile_long, leader_veh.pos_profile_lat, 'rx', label='Cut-in vehicle')
    plt.plot(ego_veh.pos_profile_long, ego_veh.pos_profile_lat, 'bx', label='Ego vehicle')
    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    plt.legend()

    plt.figure('Speed')
    plt.plot(np.linspace(0, (iterations-1)/freq, iterations), ego_veh.speed_profile_long, '-bx', label='Ego vehicle')
    plt.plot(np.linspace(0, (iterations-1)/freq, iterations), leader_veh.speed_profile_long, 'r', label='Leader vehicle')
    plt.xlabel('Time (s)')
    plt.ylabel('Speed (m/s)')
    plt.legend()

    plt.figure('Acceleration')
    plt.plot(np.linspace(0, (iterations-2)/freq, iterations-1), np.diff(ego_veh.speed_profile_long) * freq, '-bx', label='Ego vehicle')
    plt.xlabel('Time (s)')
    plt.ylabel('Acceleration (m/s$^2$)')
    plt.legend()

    # plt.axis('off')
    # ax1.set_facecolor((1, 0, 0, 0.2))
    plt.show()
