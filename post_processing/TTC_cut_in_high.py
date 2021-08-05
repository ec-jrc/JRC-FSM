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
import matplotlib.pyplot as plt
import matplotlib.cm as cm
plt.style.use('ggplot')


def plot_results(**kwargs):
    use_model = kwargs.get('model', 'FSM')
    print("Selected model TTC: ", use_model)

    if not os.path.isfile('results/cut_in_high_speed/'+use_model+'_20_10.csv'):
        print("Error, result files not found, run corresponding analysis first")
        exit(5)

    for ego_speed in [70, 90, 110, 130]:
        for cut_in_speed in range(10, ego_speed, 30):

            plt.figure()
            plt.title(f'Ego speed {ego_speed} (km/h), Cut-in speed {cut_in_speed} (km/h)')

            if use_model == 'FSM':
                df = pd.read_csv(f'results/cut_in_high_speed/FSM_{ego_speed}_{cut_in_speed}.csv')
            elif use_model == 'CC_human_driver':
                df = pd.read_csv(f'results/cut_in_high_speed/CC_human_driver_{ego_speed}_{cut_in_speed}.csv')
            elif use_model == 'RSS':
                df = pd.read_csv(f'results/cut_in_high_speed/RSS_{ego_speed}_{cut_in_speed}.csv')
            elif use_model == 'Reg157':
                df = pd.read_csv(f'results/cut_in_high_speed/Reg157_{ego_speed}_{cut_in_speed}.csv')
            else:
                print("Error, unsupported safety model\n")
                exit(4)

            namefig = use_model + '.png'

            plt.scatter(df['long_dist'], df['lat_vel'], c=df['minTTC'], cmap=cm.RdYlGn, alpha=0.4)
            plt.colorbar()

            df = df[df['Crash']]
            plt.plot(df['long_dist'], df['lat_vel'], 'kx', label='Crash')

            plt.xlabel('Initial distance (m)')
            plt.ylabel('Lateral velocity (m/s)')
            plt.legend()
            plt.tight_layout()

            if kwargs.get('save_image', False):
                plt.savefig(f'results/cut_in_high_speed/TTC_for_speeds_{ego_speed}_{cut_in_speed}_{namefig}', dpi=300)
                plt.close()
            else:
                plt.show()
