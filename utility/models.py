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
from utility import fuzzy_functs as ff

models_list = ['FSM', 'CC_human_driver', 'RSS', 'Reg157']

''' ================== utility functions ================== '''


def check_safety_model(ego_veh, cutting_in_veh, speed_log, speed_lat, freq, i):
    # return True
    if abs(ego_veh.pos_profile_long[i] - cutting_in_veh.pos_profile_long[i]) + \
            - ego_veh.length / 2 - cutting_in_veh.length / 2 > 1:
        return True
    elif (abs(ego_veh.pos_profile_long[i] - cutting_in_veh.pos_profile_long[i]) +
          - ego_veh.length / 2 - cutting_in_veh.length / 2) / ego_veh.speed_profile_long[i] > 1:
        return True
    return False


def model_react(ego_veh, speed_log, freq):
    return speed_log - ego_veh.max_a / freq, 0


''' ================== CC_human_driver model ================== '''
"""
    Reg 157
    Annex 4 - Appendix 3
"""


def CC_calc_dist_to_react(lane_width, cut_in_width, ego_dist_to_lane):
    lane_marking_to_center_cut_in = (lane_width - cut_in_width) / 2
    wp_dist_to_react = lane_marking_to_center_cut_in - 0.72 - 0.375
    return ego_dist_to_lane + wp_dist_to_react


def CC_check_safety(ego_veh, cutting_in_veh, speed_log, speed_lat, freq, i):
    return False


def CC_check_safety_cut_in(ego_veh, cutting_in_veh, speed_log, speed_lat, freq, i):
    if ego_veh.pos_profile_long[i] > cutting_in_veh.pos_profile_long[i]:
        return True
    if abs(ego_veh.pos_profile_lat[i] - cutting_in_veh.pos_profile_lat[i]) + \
            - ego_veh.width / 2 - cutting_in_veh.width / 2 > 0:
        return True
    elif abs(abs((cutting_in_veh.pos_profile_long[i] - ego_veh.pos_profile_long[i] +
                  - ego_veh.length / 2 - cutting_in_veh.length / 2)) / \
             (ego_veh.speed_profile_long[i] - cutting_in_veh.speed_profile_long[i])) > ego_veh.CC_critical_ttc:
        ego_veh.large_TTC = True
        return True
    return False


def CC_check_safety_lane_info(ego_veh, cutting_in_veh, speed_log, speed_lat, freq, i):
    # return True
    if ego_veh.pos_profile_long[i] > cutting_in_veh.pos_profile_long[i]:
        return True
    if abs(ego_veh.pos_profile_lat[i] - cutting_in_veh.pos_profile_lat[i]) + \
            - ego_veh.width / 2 - cutting_in_veh.width / 2 > ego_veh.dist_to_react:
        return True
    elif abs((abs(ego_veh.pos_profile_long[i] - cutting_in_veh.pos_profile_long[i]) +
              - ego_veh.length / 2 - cutting_in_veh.length / 2) / (
                     ego_veh.speed_profile_long[i] - cutting_in_veh.speed_profile_long[i])) > ego_veh.CC_critical_ttc:
        return True
    return False

def CC_distance(ego_veh, ur):
    return 2 * ur


def CC_react(ego_veh, speed_log, freq):
    if ego_veh.CC_rt_counter > 0:
        ego_veh.CC_rt_counter -= 1 / freq
        ego_veh.deceleration = ego_veh.CC_release_deceleration
        return speed_log - ego_veh.deceleration / freq, 0
    ego_veh.deceleration = min(ego_veh.deceleration + ego_veh.CC_min_jerk / freq,
                               ego_veh.CC_max_deceleration)
    return max(speed_log - ego_veh.deceleration / freq, 0), 0


''' ================== RSS model ================== '''
"""
    Shalev-Shwartz, Shai, Shaked Shammah, and Amnon Shashua. 
    "On a formal model of safe and scalable self-driving cars." 
    arXiv preprint arXiv:1708.06374 (2017).
"""


def RSS_check_safety(ego_veh, cutting_in_veh, speed_log, speed_lat, freq, i):
    if ego_veh.pos_profile_long[i] > cutting_in_veh.pos_profile_long[i]:
        return True
    d_safe_rss_log = speed_log * ego_veh.RSS_rt + ego_veh.max_a * np.power(ego_veh.RSS_rt, 2) / 2 + np.power(
        speed_log + ego_veh.RSS_rt * ego_veh.max_a, 2) / (2 * ego_veh.max_d) + \
                     - np.power(cutting_in_veh.speed_profile_long[i], 2) / (2 * cutting_in_veh.max_d)

    if abs(ego_veh.pos_profile_long[i] - cutting_in_veh.pos_profile_long[i]) + \
            - ego_veh.length / 2 - cutting_in_veh.length / 2 < d_safe_rss_log:
        cut_in_lat = np.abs(cutting_in_veh.speed_profile_lat[i])
        d_safe_rss_lat = ego_veh.RSS_mu + np.abs(
            (2 * cut_in_lat + cutting_in_veh.max_a_lat * ego_veh.RSS_rt) * ego_veh.RSS_rt / 2) + \
                         + np.power(cut_in_lat + cutting_in_veh.max_a_lat * ego_veh.RSS_rt, 2) / \
                         (2 * cutting_in_veh.max_a_lat)
        if abs(ego_veh.pos_profile_lat[i] - cutting_in_veh.pos_profile_lat[i]) + \
                - ego_veh.width / 2 - cutting_in_veh.width / 2 < d_safe_rss_lat:
            return False
    return True


def RSS_react(ego_veh, speed_log, freq):
    if ego_veh.RSS_rt_counter > 0:
        ego_veh.RSS_rt_counter -= 1 / freq
        return speed_log, 0
    ego_veh.deceleration = min(ego_veh.deceleration + ego_veh.RSS_min_jerk / freq, ego_veh.RSS_max_deceleration)
    return max(speed_log - ego_veh.deceleration / freq, 0), 0


def RSS_distance(ego_veh, ur):
    """
    to find this we have to make some calculations
    After reaction time, the speed of the leader vehicle can be :
    ul(t0+τ) = ur + deceleration*reaction time
    so the next distance is:
    distance(t0+reaction_time) = distance_eq - (deceleration*reaction time**2)/2
    this distance must be equal to the RSS safe distance with the new speeds
    """
    d_safe_rss_log = ur * ego_veh.RSS_rt + ego_veh.max_a * np.power(ego_veh.RSS_rt, 2) / 2 + np.power(
        ur + ego_veh.RSS_rt * ego_veh.max_a, 2) / (2 * ego_veh.max_d) + \
                     - np.power(max(ur - ego_veh.RSS_rt * ego_veh.max_d, 0), 2) / \
                     (2 * ego_veh.max_d) + 1 / 2 * ego_veh.max_d * np.power(ego_veh.RSS_rt, 2)
    return d_safe_rss_log


''' ================== Reg157 model ================== '''
"""
    Reg 157
    5.2.5.2.
"""


def Reg157_check_safety_cut_in(ego_veh, cutting_in_veh, speed_log, speed_lat, freq, i):
    if ego_veh.pos_profile_long[i] > cutting_in_veh.pos_profile_long[i]:
        return True
    if abs(ego_veh.pos_profile_lat[i] - cutting_in_veh.pos_profile_lat[i]) + \
            - ego_veh.width / 2 - cutting_in_veh.width / 2 > ego_veh.Reg157_lat_safe_dist:
        return True
    elif abs((abs(ego_veh.pos_profile_long[i] - cutting_in_veh.pos_profile_long[i]) + \
              - ego_veh.length / 2 - cutting_in_veh.length / 2) /
             (ego_veh.speed_profile_long[i] - cutting_in_veh.speed_profile_long[i])) >  (ego_veh.speed_profile_long[i] - cutting_in_veh.speed_profile_long[i]) / (
            2 * ego_veh.Reg157_max_deceleration) + ego_veh.Reg157_rt+0.1:

        return True
    return False


def Reg157_check_safety(ego_veh, cutting_in_veh, speed_log, speed_lat, freq, i):
    return False


def Reg157_react(ego_veh, speed_log, freq):
    if ego_veh.Reg157_rt_counter > 0:
        ego_veh.Reg157_rt_counter -= 1 / freq
        return speed_log, 0
    return max(speed_log - ego_veh.Reg157_max_deceleration / freq, 0), 0


''' ================== Fuzzy model ================== '''
"""
    Mattas, Konstantinos, et al. "Fuzzy Surrogate Safety Metrics for real-time assessment of rear-end collision risk. 
    A study based on empirical observations." Accident Analysis & Prevention 148 (2020): 105794.
"""


def FSM_check_safety(ego_veh, cutting_in_veh, speed_log, speed_lat, freq, i):
    if ego_veh.pos_profile_long[i] > cutting_in_veh.pos_profile_long[i]:
        return True

    if abs(ego_veh.pos_profile_lat[i] - cutting_in_veh.pos_profile_lat[i]) + \
            - ego_veh.width / 2 - cutting_in_veh.width / 2 > 0:
        cutin_speed = -cutting_in_veh.speed_profile_lat[i]
        if cutin_speed > 0:
            headway_lat = (abs(ego_veh.pos_profile_lat[i] - cutting_in_veh.pos_profile_lat[i]) +
                           - ego_veh.width / 2 - cutting_in_veh.width / 2) / cutin_speed
            headway_lon_gross = (abs(ego_veh.pos_profile_long[i] - cutting_in_veh.pos_profile_long[i]) +
                                 + ego_veh.length / 2 + cutting_in_veh.length / 2) / \
                                (ego_veh.speed_profile_long[i] - cutting_in_veh.speed_profile_long[i])
            if headway_lat > headway_lon_gross + 0.1:
                return True
        else:
            return True

    ar = (ego_veh.speed_profile_long[i] - ego_veh.speed_profile_long[i - 1]) * freq
    dist = abs(ego_veh.pos_profile_long[i] - cutting_in_veh.pos_profile_long[i]) - ego_veh.length / 2 + \
           - cutting_in_veh.length / 2
    cfs = ff.CFS(dist, ego_veh.speed_profile_long[i], cutting_in_veh.speed_profile_long[i], ego_veh.FSM_rt,
                 ego_veh.FSM_br_min, ego_veh.FSM_br_max, ego_veh.FSM_bl, ar)
    pfs = ff.PFS(dist, ego_veh.speed_profile_long[i], cutting_in_veh.speed_profile_long[i], ego_veh.FSM_rt,
                 ego_veh.FSM_br_min, ego_veh.FSM_br_max, ego_veh.FSM_bl, ego_veh.FSM_margin_dist,
                 ego_veh.FSM_margin_safe_dist)
    ego_veh.cfs = cfs
    ego_veh.pfs = pfs
    if cfs + pfs == 0:
        return True
    return False


def FSM_distance(ego_veh, ur):
    return ur * ego_veh.FSM_rt + np.power(ur, 2) / (2 * ego_veh.FSM_br_min) - np.power(ur, 2) / (2 * ego_veh.FSM_bl) +\
           + ego_veh.FSM_margin_safe_dist + ego_veh.FSM_margin_dist


def FSM_react(ego_veh, speed_log, freq):
    if ego_veh.FSM_rt_counter > 0:
        ego_veh.FSM_rt_counter -= 1 / freq
        return speed_log, 0

    if ego_veh.cfs > 0:
        acc = ego_veh.cfs * (ego_veh.FSM_br_max - ego_veh.FSM_br_min) + ego_veh.FSM_br_min
    else:
        acc = ego_veh.pfs * ego_veh.FSM_br_min
    ego_veh.deceleration = min(min(ego_veh.deceleration + ego_veh.CC_min_jerk / freq, ego_veh.FSM_max_deceleration),
                               acc)
    return max(speed_log - ego_veh.deceleration / freq, 0), 0
