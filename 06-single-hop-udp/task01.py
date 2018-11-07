#! /usr/bin/env python3
import sys  # noqa: E402
import os
import argparse
sys.path.append("../testutils")
from testutils import Board  # noqa: E402
from iotlab import create_experiment, stop_experiment, get_nodes_addresses, \
                   prepare_experiment  # noqa: E402
from common import SingleHopUdpNode, single_hop_udp_run,\
                   print_results  # noqa: E402
from time import sleep  # noqa: E402

CHANNEL = 26
COUNT = 10
INTERVAL_US = 1000000
PORT = 1337
PAYLOAD_SIZE = 1024
EXPERIMENT_DURATION = 60
TOLERANCE = 5  # %


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('riotbase', nargs='?',
                   help='Location of RIOT folder')
    p.add_argument('-d', '--iotlab_dur', help='IOTLAB experiment duration')
    p.add_argument('-i', '--iotlab_exp', help='IOTLAB experiment id')
    args = p.parse_args()

    riotbase = args.riotbase
    exp_id = args.iotlab_exp
    exp_dur = args.iotlab_dur or EXPERIMENT_DURATION

    if not riotbase:
        p.print_help()
        sys.exit(1)

    os.chdir(os.path.join(riotbase, "tests/gnrc_udp"))

    # Create IoTLAB experiment
    if not exp_id:
        print('creating experiment')
        exp_id = create_experiment(2)
        addr = get_nodes_addresses(exp_id)
    else:
        addr = prepare_experiment(exp_id)

    try:
        iotlab_cmd = "make IOTLAB_NODE={} BOARD=iotlab-m3 term"
        source = SingleHopUdpNode(iotlab_cmd.format(addr[0]))
        dest = SingleHopUdpNode(iotlab_cmd.format(addr[1]))
        sleep(3)
        source.reboot()
        dest.reboot()

        packets_received = single_hop_udp_run(source, dest, CHANNEL, COUNT,
                                              INTERVAL_US, PORT, PAYLOAD_SIZE)

        print_results(COUNT, packets_received, TOLERANCE)
        assert((COUNT - packets_received) / COUNT * 100 < TOLERANCE)
        print("OK")

    except Exception as e:
        print(str(e))
        print("Test failed!")
        pass

    if not args.iotlab_exp:
        stop_experiment(exp_id)
