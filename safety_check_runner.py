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

import sys
import os
# loop functions
from utility import comparison_cut_out
from utility import comparison_car_following
from utility import comparison_cut_in
# one scenario functions
from utility import one_case_cut_out
from utility import one_case_car_following
from utility import one_case_cut_in
# post processing
from post_processing import graphs_car_following
from post_processing import graphs_cut_in_low
from post_processing import graphs_cut_in_high
from post_processing import graphs_cut_out
from post_processing import FSM_cut_in_low
from post_processing import FSM_cut_in_high
from post_processing import crashes_cut_in_low
from post_processing import crashes_cut_in_high
from post_processing import TTC_cut_in_low
from post_processing import TTC_cut_in_high


def test_run(analysis, scenario, **kwargs):

    print("Selected analysis: " + analysis)
    print("Selected scenario: " + scenario)

    if analysis == 'comparison':
        out_dir = 'results'
        if not(os.path.exists(out_dir)):
            os.mkdir(out_dir)
        if scenario == 'cut_out':
            comparison_cut_out.run_loop()
        elif scenario == 'car_following':
            comparison_car_following.run_loop()
        elif scenario == 'cut_in':
            comparison_cut_in.run_loop('high')
            comparison_cut_in.run_loop('low')
        else:
            print("Wrong scenario")
            exit(2)

    elif analysis == 'one_case':
        model = kwargs.get('model', 'FSM')
        if scenario == 'cut_out':
            one_case_cut_out.run_one_case(model, **kwargs)
        elif scenario == 'car_following':
            one_case_car_following.run_one_case(model, **kwargs)
        elif scenario == 'cut_in':
            one_case_cut_in.run_one_case(model, **kwargs)
        else:
            print("Wrong scenario")
            exit(2)

    elif analysis == 'post_processing':
        if scenario == 'car_following':
            graphs_car_following.plot_results(**kwargs)
        elif scenario == 'cut_in':
            if 'model' in kwargs:
                TTC_cut_in_low.plot_results(**kwargs)
                TTC_cut_in_high.plot_results(**kwargs)
                if kwargs.get('model', '') == 'FSM':
                    FSM_cut_in_low.plot_results(**kwargs)
                    FSM_cut_in_high.plot_results(**kwargs)
            else:
                crashes_cut_in_low.plot_results()
                crashes_cut_in_high.plot_results()
                graphs_cut_in_low.plot_results(**kwargs)
                graphs_cut_in_high.plot_results(**kwargs)
        elif scenario == 'cut_out':
            graphs_cut_out.plot_results(**kwargs)
        else:
            print("Wrong scenario")
            exit(2)

    else:
        print("Wrong analysis")
        exit(1)

    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error, script should be launched with minimum two arguments:\n")
        print(" 1. Type of analysis: 'one_case', 'comparison', 'post_processing' \n")
        print(" 2. Scenario: 'cut_in', 'cut_out', 'car_following' \n")
        exit(1)
    elif len(sys.argv) == 3:
        test_run(sys.argv[1], sys.argv[2])
    else:
        kwargs = {}
        for i in range(3, len(sys.argv)):
            key, value = sys.argv[i].split('=', 1)
            kwargs[key] = value

        test_run(sys.argv[1], sys.argv[2], **kwargs)

else:
    print("Running external configuration")
