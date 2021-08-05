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
import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib.cm as cm


def plot_results(**kwargs):
    if os.path.isfile('results/car_following/FSM_car_following.csv'):
        dfFSM = pd.read_csv('results/car_following/FSM_car_following.csv')
        dfRSS = pd.read_csv('results/car_following/RSS_car_following.csv')
        dfCC = pd.read_csv('results/car_following/CC_human_driver_car_following.csv')
    else:
        print("Error, result files not found, run corresponding analysis first")
        exit(5)

    CC_mask = dfCC['Crash'] == True
    plt.figure('CC')
    plt.title('CC_human_driver')
    plt.plot(dfCC[CC_mask]['velocity'], dfCC[CC_mask]['max_deceleration'], 'rx', markersize=10, alpha=0.2,
             label='Crash')
    plt.plot(dfCC[~CC_mask]['velocity'], dfCC[~CC_mask]['max_deceleration'], 'go', markersize=10, alpha=0.2,
             label='Safe')
    plt.ylabel('Deceleration rate (g)')
    plt.xlabel('Ego vehicle velocity (km/h)')
    plt.tight_layout()
    if kwargs.get('save_image', False):
        plt.savefig('results/car_following/CC_CF.png', dpi=150)
        plt.close()

    plt.figure('RSS')
    plt.title('RSS')
    rss_mask = dfRSS['Crash'] == True
    plt.plot(dfRSS[rss_mask]['velocity'], dfRSS[rss_mask]['max_deceleration'], 'rx', markersize=10, alpha=0.2,
             label='Crash')
    plt.plot(dfRSS[~rss_mask]['velocity'], dfRSS[~rss_mask]['max_deceleration'], 'go', markersize=10, alpha=0.2,
             label=' Safe')
    plt.ylabel('Deceleration rate (g)')
    plt.xlabel('Ego vehicle velocity (km/h)')
    plt.tight_layout()
    if kwargs.get('save_image', False):
        plt.savefig('results/car_following/RSS_CF.png', dpi=150)
        plt.close()

    plt.figure('RSS DV')
    plt.title('RSS DV')
    plt.scatter(dfRSS[rss_mask]['velocity'], dfRSS[rss_mask]['max_deceleration'], c=dfRSS[rss_mask]['speed_difference'],
                cmap=cm.RdYlGn_r, alpha=0.4)
    cbar = plt.colorbar()
    cbar.set_label('Velocity difference at crash (m/s)')
    plt.ylabel('Deceleration rate (g)')
    plt.xlabel('Ego vehicle velocity (km/h)')
    plt.ylim([0, 1])
    plt.xlim([0, 130])
    plt.tight_layout()
    if kwargs.get('save_image', False):
        plt.savefig('results/car_following/RSS_CF_DV.png', dpi=150)
        plt.close()

    plt.figure('FSM')
    plt.title('FSM')
    fuzzy_mask = dfFSM['Crash'] == True
    plt.plot(dfFSM[fuzzy_mask]['velocity'], dfFSM[fuzzy_mask]['max_deceleration'], 'rx', markersize=10, alpha=0.2,
             label='Crash')
    plt.plot(dfFSM[~fuzzy_mask]['velocity'], dfFSM[~fuzzy_mask]['max_deceleration'], 'go', markersize=10, alpha=0.2,
             label='Safe')
    plt.ylabel('Deceleration rate (g)')
    plt.xlabel('Ego vehicle velocity (km/h)')
    plt.tight_layout()
    if kwargs.get('save_image', False):
        plt.savefig('results/car_following/FSM_CF.png', dpi=150)
        plt.close()

    plt.figure('Fuzzy FSM')
    plt.title('Fuzzy FSM difficulty index')
    # fuzzy_mask = dfFSM['Crash'] == True
    dfFSM.loc[dfFSM['PFS'] > 0.85, 'color'] = 'y'
    dfFSM.loc[dfFSM['CFS'] >= 0.9, 'color'] = 'r'
    dfFSM.loc[dfFSM['PFS'] <= 0.85, 'color'] = 'g'

    plt.scatter(dfFSM['velocity'], dfFSM['max_deceleration'], c=dfFSM['color'], alpha=0.4)
    plt.ylabel('Deceleration rate (g)')
    plt.xlabel('Ego vehicle velocity (km/h)')
    plt.tight_layout()
    if kwargs.get('save_image', False):
        plt.savefig('results/car_following/FSM_criticality.png', dpi=150)
        plt.close()

    plt.figure('Distances in (s)')
    df = dfFSM[np.abs(dfFSM['max_deceleration'] - 0.05) < 0.01]
    plt.plot(df['velocity'], df['initial_distance'] / df['velocity'] * 3.6, label='Fuzzy THW')

    df = dfRSS[np.abs(dfRSS['max_deceleration'] - 0.05) < 0.01]
    plt.plot(df['velocity'], df['initial_distance'] / df['velocity'] * 3.6, label='RSS THW')

    df = dfCC[np.abs(dfCC['max_deceleration'] - 0.05) < 0.01]
    plt.plot(df['velocity'], df['initial_distance'] / df['velocity'] * 3.6, label='CC human driver THW')

    speed = np.arange(10, 130, 1)
    tg = speed * 0.03597122302158274 / 3.6 + 1.0
    tg[tg > 2] = 2
    plt.plot(speed, tg, label='Regulation table')

    plt.legend()
    plt.xlabel('Velocity (km/h)')
    plt.ylabel('Time headway (s)')
    plt.tight_layout()
    if kwargs.get('save_image', False):
        plt.savefig('results/car_following/THW.png', dpi=150)
        plt.close()
    else:
        plt.show()
