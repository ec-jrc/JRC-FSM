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


def plot_results(**kwargs):
    if os.path.isfile('results/cut_out/FSM_cut_out.csv'):
        dfFSM = pd.read_csv('results/cut_out/FSM_cut_out.csv')
        dfRSS = pd.read_csv('results/cut_out/RSS_cut_out.csv')
        dfCC = pd.read_csv('results/cut_out/CC_human_driver_cut_out.csv')
    else:
        print("Error, result files not found, run corresponding analysis first")
        exit(5)

    for ur in range(10, 131, 10):
        plt.figure(str(ur) + ' FSM')
        plt.title('FSM')
        df = dfFSM[dfFSM['velocity'] == ur]

        fuzzy_mask1 = (df['Crash']) & (df['Crash_front'] != True)
        fuzzy_mask2 = (~df['Crash']) & (~df['Crash_front'])
        fuzzy_mask3 = df['Crash_front']

        plt.plot(df[fuzzy_mask1]['front_distance'], -df[fuzzy_mask1]['lateral_velocities'], 'rx', markersize=10, alpha=0.2,
                 label='Crash')
        plt.plot(df[fuzzy_mask2]['front_distance'], -df[fuzzy_mask2]['lateral_velocities'], 'go', markersize=10, alpha=0.2,
                 label='Safe')
        plt.plot(df[fuzzy_mask3]['front_distance'], -df[fuzzy_mask3]['lateral_velocities'], 'yo', markersize=10, alpha=0.2,
                 label='Crash leader')

        plt.xlabel('Distance front (m)')
        plt.ylabel('Lateral velocity (m/s)')
        plt.legend()
        plt.tight_layout()
        if kwargs.get('save_image', False):
            plt.savefig('results/cut_out/Fuzzy_' + str(ur) + '.png')
            plt.close()
        else:
            plt.show()

    for ur in range(10, 131, 10):
        plt.figure(str(ur) + ' Difficulty FSM')
        plt.title('FSM ' + str(ur) + ' km/h')
        df = dfFSM[dfFSM['velocity'] == ur]

        fuzzy_mask1 = (df['Crash']) & (df['Crash_front'] != True)
        plt.plot(df[fuzzy_mask1]['front_distance'], -df[fuzzy_mask1]['lateral_velocities'], 'rx', markersize=10,
                 label='Crash')

        fuzzy_mask2 = (~df['Crash']) & (~df['Crash_front'])
        df = df[fuzzy_mask2]
        df.loc[df['PFS'] > 0., 'color'] = 'y'
        df.loc[df['CFS'] >= 0.5, 'color'] = 'r'
        df.loc[df['PFS'] <= 0., 'color'] = 'g'

        plt.scatter(df['front_distance'], -df['lateral_velocities'], c=df['color'], alpha=0.4)

        plt.xlabel('Distance front (m)')
        plt.ylabel('Lateral velocity (m/s)')
        plt.tight_layout()
        if kwargs.get('save_image', False):
            plt.savefig('results/cut_out/challenge_level_' + str(ur) + '.png')
            plt.close()
        else:
            plt.show()

    for ur in range(10, 131, 10):
        plt.figure(str(ur) + ' CC')
        plt.title('CC_human_driver')
        df = dfCC[dfCC['velocity'] == ur]

        CC_mask1 = (df['Crash']) & (df['Crash_front'] != True)
        CC_mask2 = (~df['Crash']) & (~df['Crash_front'])
        CC_mask3 = df['Crash_front']

        plt.plot(df[CC_mask1]['front_distance'], -df[CC_mask1]['lateral_velocities'], 'rx', markersize=10, alpha=0.2,
                 label='Crash')
        plt.plot(df[CC_mask2]['front_distance'], -df[CC_mask2]['lateral_velocities'], 'go', markersize=10, alpha=0.2,
                 label='Safe')
        plt.plot(df[CC_mask3]['front_distance'], -df[CC_mask3]['lateral_velocities'], 'yo', markersize=10, alpha=0.2,
                 label='Crash leader')

        plt.xlabel('Distance front (m)')
        plt.ylabel('Lateral velocity (m/s)')
        plt.legend()
        plt.tight_layout()
        if kwargs.get('save_image', False):
            plt.savefig('results/cut_out/CC_human_driver_' + str(ur) + '.png')
            plt.close()
        else:
            plt.show()

    for ur in range(10, 131, 10):
        plt.figure(str(ur) + 'rss')
        plt.title('RSS')
        df = dfRSS[dfRSS['velocity'] == ur]

        rss_mask1 = (df['Crash']) & (df['Crash_front'] != True)
        rss_mask2 = (~df['Crash']) & (~df['Crash_front'])
        rss_mask3 = df['Crash_front']

        plt.plot(df[rss_mask1]['front_distance'], -df[rss_mask1]['lateral_velocities'], 'rx', markersize=10, alpha=0.2,
                 label='Crash')
        plt.plot(df[rss_mask2]['front_distance'], -df[rss_mask2]['lateral_velocities'], 'go', markersize=10, alpha=0.2,
                 label='Safe')
        plt.plot(df[rss_mask3]['front_distance'], -df[rss_mask3]['lateral_velocities'], 'yo', markersize=10, alpha=0.2,
                 label='Crash leader')

        plt.xlabel('Distance front (m)')
        plt.ylabel('Lateral velocity (m/s)')
        plt.legend()
        plt.tight_layout()
        if kwargs.get('save_image', False):
            plt.savefig('results/cut_out/RSS_' + str(ur) + '.png')
            plt.close()
        else:
            plt.show()
