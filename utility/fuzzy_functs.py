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
from numba import njit

@njit
def membership_value(value, points):
    if value < points[0] or value > points[-1]:
        return 0
    elif points[1] < value < points[2]:
        return 1
    elif points[0] < value < points[1]:
        return (value - points[0]) / (points[1] - points[0])
    else:
        return (value - points[-1]) / (points[2] - points[-1])

@njit
def PFS(dist, ur, ul, rt, br_min, br_max, bl, margin_dist, margin_safe_dist):
    dist = dist - margin_dist

    dsafe = ur * rt + np.power(ur, 2) / (2 * br_min) - np.power(ul, 2) / (2 * bl) + margin_safe_dist

    if dist > dsafe:
        return 0
    else:
        dunsafe = ur * rt + np.power(ur, 2) / (2 * br_max) - np.power(ul, 2) / (2 * bl)
        if dist < dunsafe:
            return 1
        else:
            return (dist - dsafe) / (dunsafe - dsafe)

@njit
def CFS(dist, ur, ul, rt, br_min, br_max, bl, ar):
    arF = max(ar, -br_min)  # Do not take into account very hard decelerations
    u_new = ur + rt * arF  # Estimate rear vehicle new speed

    if ur <= ul:
        return 0

    if u_new < ul:
        dsafe = np.power(ur - ul, 2) / np.abs(ar * 2)
        if dist < dsafe:
            return 1
        else:
            return 0
    else:
        dsafe = (ur + arF * rt / 2 - ul) * rt + np.power(ur + arF * rt - ul, 2) / (br_min * 2)

        if dist > dsafe:
            return 0
        else:
            dunsafe = (ur + arF * rt / 2 - ul) * rt + np.power(ur + arF * rt - ul, 2) / (br_max * 2)
            if dist < dunsafe:
                return 1
            else:
                return (dist - dsafe) / (dunsafe - dsafe)
