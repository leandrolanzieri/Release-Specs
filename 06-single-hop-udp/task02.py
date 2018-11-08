#! /usr/bin/env python3
import sys  # noqa: E402
import os
import argparse
sys.path.append("../testutils")
from testutils import Board  # noqa: E402
from iotlab import IoTLABNode, IoTLABExperiment  # noqa: E402
from common import SingleHopUdpNode, single_hop_udp_run,\
                   print_results  # noqa: E402
from time import sleep  # noqa: E402

CHANNEL = 26
COUNT = 1000
INTERVAL_US = 1000000
PORT = 61616
PAYLOAD_SIZE = 1024
EXPERIMENT_DURATION = 60
TOLERANCE = 5  # %


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('riotbase', nargs='?',
                   help='Location of RIOT folder')
    p.add_argument('-d', '--iotlab_dur', help='IOTLAB experiment duration')
    args = p.parse_args()

    riotbase = args.riotbase
    exp_dur = args.iotlab_dur or EXPERIMENT_DURATION

    if not riotbase:
        p.print_help()
        sys.exit(1)

    os.chdir(os.path.join(riotbase, "tests/gnrc_udp"))

    try:
        exp = IoTLABExperiment("RIOT-release-test-06-01",
                               [IoTLABNode(extra_modules=["gnrc_pktbuf_cmd"]),
                                IoTLABNode(extra_modules=["gnrc_pktbuf_cmd"])],
                               duration=exp_dur)
        addr = exp.nodes_addresses
        iotlab_cmd = "make IOTLAB_NODE={} BOARD=iotlab-m3 term"
        source = SingleHopUdpNode(iotlab_cmd.format(addr[0]))
        dest = SingleHopUdpNode(iotlab_cmd.format(addr[1]))

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

    exp.stop()
