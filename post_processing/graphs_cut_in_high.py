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
import os
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')


def plot_results(**kwargs):
    if not os.path.isfile('results/cut_in_high_speed/RSS_70_10.csv'):
        print("Error, result files not found, run corresponding analysis first")
        exit(5)

    for ego_speed in [70, 90, 110, 130]:
        for cut_in_speed in range(10, ego_speed, 30):
            plt.figure()
            plt.title(f'Ego speed {ego_speed} (km/h), Cut-in speed {cut_in_speed} (km/h)')
            df_RSS = pd.read_csv(f'results/cut_in_high_speed/RSS_{ego_speed}_{cut_in_speed}.csv')
            df_Reg157 = pd.read_csv(f'results/cut_in_high_speed/Reg157_{ego_speed}_{cut_in_speed}.csv')
            df_Fuz = pd.read_csv(f'results/cut_in_high_speed/FSM_{ego_speed}_{cut_in_speed}.csv')
            df_CC = pd.read_csv(f'results/cut_in_high_speed/CC_human_driver_{ego_speed}_{cut_in_speed}.csv')

            df_RSS = df_RSS[df_RSS['Crash']]
            df_Reg157 = df_Reg157[df_Reg157['Crash']]
            df_Fuz = df_Fuz[df_Fuz['Crash']]
            df_CC = df_CC[df_CC['Crash']]

            plt.plot(df_RSS['long_dist'], df_RSS['lat_vel'], 'go', label='RSS')
            plt.plot(df_Reg157['long_dist'], df_Reg157['lat_vel'], 'm1', markersize=10, label='Reg157 ')
            plt.plot(df_Fuz['long_dist'], df_Fuz['lat_vel'], 'bo', markersize=15, alpha=0.2, label='Fuzzy SM')
            plt.plot(df_CC['long_dist'], df_CC['lat_vel'], 'rx', markersize=10, alpha=0.2, label='CC human driver')

            plt.xlabel('Initial distance (m)')
            plt.ylabel('Lateral velocity (m/s)')
            plt.legend()
            plt.tight_layout()
            plt.xlim([0, 120])
            plt.ylim([0, 1.8])

            if kwargs.get('save_image', False):
                plt.savefig(f'results/cut_in_high_speed/comparison_for_speeds_{ego_speed}_{cut_in_speed}.png', dpi=150)
                plt.close()
            else:
                plt.show()
