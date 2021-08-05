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
plt.style.use('ggplot')
import matplotlib.cm as cm


def plot_results(**kwargs):
    if not os.path.isfile('results/cut_in_low_speed/FSM_20_10.csv'):
        print("Error, result files not found, run corresponding analysis first")
        exit(5)

    for ego_speed in [10, 20, 30, 40, 50, 60]:
        for cut_in_speed in range(10, ego_speed, 10):
            plt.figure()
            plt.title(f'Ego speed {ego_speed} (km/h), Cut-in speed {cut_in_speed} (km/h)')
            df = pd.read_csv(f'results/cut_in_low_speed/FSM_{ego_speed}_{cut_in_speed}.csv')

            df['color'] = 0
            df['PFS'] = np.round(df['PFS'], 1)
            df.loc[df['PFS'] >= 0.85, 'color'] = 'y'
            df.loc[df['CFS'] >= 0.9, 'color'] = 'r'
            df.loc[df['PFS'] < 0.85, 'color'] = 'g'

            plt.scatter(df['long_dist'], df['lat_vel'], c=df['color'], alpha=0.4)

            # plt.colorbar()

            df = df[df['Crash']]
            plt.plot(df['long_dist'], df['lat_vel'], 'kx', label='Crash')

            plt.xlabel('Initial distance (m)')
            plt.ylabel('Lateral velocity (m/s)')
            # plt.legend()
            plt.tight_layout()

            if kwargs.get('save_image', False):
                plt.savefig(f'results/cut_in_low_speed/speeds_{ego_speed}_{cut_in_speed}_FSM_Fuzzy.png', dpi=150)
                plt.close()
            else:
                plt.show()
