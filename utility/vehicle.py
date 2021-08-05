'''Definiton the vehicle class and default values'''

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


class vehicle(object):

    def __init__(self):
        # self.position = np.array([0,0])

        self.speed_profile_long = []
        self.speed_profile_lat = []
        self.pos_profile_long = []
        self.pos_profile_lat = []

        self.width = 1.9
        self.length = 5

        self.max_a = 3
        self.max_a_CF = 1
        self.max_d = 6
        self.max_a_lat = 1

        self.safe = True
        self.crash = False
        self.crash_type = 0

        self.deceleration = 0

        ''' CC_human_driver '''
        self.CC_rt = 0.75
        self.CC_rt_counter = self.CC_rt
        self.CC_min_jerk = 12.65
        self.CC_max_deceleration = 0.774 * 9.81
        self.CC_release_deceleration = 0.4  # deceleration when not stepping on the accelerator pedal (I think)
        self.CC_critical_ttc = 2

        ''' Reg157 '''
        self.Reg157_rt = 0.35
        self.Reg157_rt_counter = self.Reg157_rt
        self.Reg157_max_deceleration = 6
        self.Reg157_lat_safe_dist = 0.5

        ''' RSS '''
        self.RSS_rt = 0.75
        self.RSS_rt_counter = self.RSS_rt
        self.RSS_min_jerk = 12.65
        self.RSS_max_deceleration = 0.774 * 9.81
        self.RSS_mu = 0.3

        ''' FSM '''
        self.FSM_rt = 0.75
        self.FSM_rt_counter = self.FSM_rt
        self.FSM_br_min = 4
        self.FSM_br_max = 6
        self.FSM_bl = 7
        self.FSM_ar = 2
        self.FSM_margin_dist = 2
        self.FSM_margin_safe_dist = 2
        self.FSM_max_deceleration = 0.774 * 9.81