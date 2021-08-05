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

def plot_results():
    RSS = [0, 0]
    Reg157 = [0, 0]
    FSM = [0, 0]
    CC = [0, 0]

    if not os.path.isfile('results/cut_in_low_speed/RSS_20_10.csv'):
        print("Error, result files not found, run corresponding analysis first")
        exit(5)

    for ego_speed in [10, 20, 30, 40, 50, 60]:
        for cut_in_speed in range(10, ego_speed, 10):
            df_RSS = pd.read_csv(f'results/cut_in_low_speed/RSS_{ego_speed}_{cut_in_speed}.csv')
            df_Reg157 = pd.read_csv(f'results/cut_in_low_speed/Reg157_{ego_speed}_{cut_in_speed}.csv')
            df_FSM = pd.read_csv(f'results/cut_in_low_speed/FSM_{ego_speed}_{cut_in_speed}.csv')
            df_CC = pd.read_csv(f'results/cut_in_low_speed/CC_human_driver_{ego_speed}_{cut_in_speed}.csv')

            RSS[0] = RSS[0] + len(df_RSS)
            Reg157[0] = Reg157[0] + len(df_Reg157)
            FSM[0] = FSM[0] + len(df_FSM)
            CC[0] = CC[0] + len(df_CC)

            df_RSS = df_RSS[df_RSS['Crash']]
            df_Reg157 = df_Reg157[df_Reg157['Crash']]
            df_FSM = df_FSM[df_FSM['Crash']]
            df_CC = df_CC[df_CC['Crash']]

            RSS[1] = RSS[1] + len(df_RSS)
            Reg157[1] = Reg157[1] + len(df_Reg157)
            FSM[1] = FSM[1] + len(df_FSM)
            CC[1] = CC[1] + len(df_CC)

    print("Crash percentage RSS low speed:    ", RSS[1] / RSS[0] * 100)
    print("Crash percentage Reg157 low speed: ", Reg157[1] / Reg157[0] * 100)
    print("Crash percentage FSM low speed:    ", FSM[1] / FSM[0] * 100)
    print("Crash percentage CC low speed:     ", CC[1] / CC[0] * 100)
