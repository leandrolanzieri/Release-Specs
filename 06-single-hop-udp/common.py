from testutils import Board
from mixins import GNRC, PktBuf
from time import sleep

PAYLOAD_SIZE = 1024
DELAY_US = 1000000

#Declare node
class SingleHopUdpNode(Board, GNRC, PktBuf):
    pass

def print_results(count, received, tolerance):
    print("Summary of test")
    print("Packets sent: {}".format(count))
    print("Packets received: {}".format(received))
    print("Packet loss: {}%".format((count-received) / count * 100))

def single_hop_udp_run(source, dest, channel, count, interval_us, port, payload_size):
    source.reboot()
    dest.reboot()

    # Get useful information
    src_iface = source.get_first_iface()
    dst_iface = dest.get_first_iface()
    ip_dest = dest.get_ip_addr()

    # Set channels
    source.set_channel(src_iface, channel)
    dest.set_channel(dst_iface, channel)

    # Start UDP server
    dest.udp_server_start(port)

    # Sleep 1 second before sending data
    sleep(1)

    # Send UDP packets
    source.udp_send(ip_dest, port, count = count, \
                    payload_size = payload_size, delay_us = interval_us)

    pkts_received = dest.udp_receive(count)

    return pkts_received
