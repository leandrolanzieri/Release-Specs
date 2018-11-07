import pexpect


class GNRC:
    def get_ip_addr(self):
        self.pexpect.sendline("ifconfig")
        self.pexpect.expect("inet6 addr: ([:0-9a-f]+) ")
        ip_addr = self.pexpect.match.group(1)
        return ip_addr

    def get_first_iface(self):
        self.pexpect.sendline("ifconfig")
        self.pexpect.expect("Iface  ([\\d]+)")
        return int(self.pexpect.match.group(1))

    def disable_rdv(self, iface):
        self.pexpect.sendline("ifconfig {} -rtr_adv".format(iface))
        self.pexpect.expect("success")

    def add_ip(self, iface, source):
        self.pexpect.sendline("ifconfig {} add {}".format(iface, source))
        self.pexpect.expect("success")

    def add_nib_route(self, iface, route, ip_addr):
        self.pexpect.sendline(
                "nib route add {} {} {}".format(iface, route, ip_addr))

    def udp_server_start(self, port):
        self.pexpect.sendline("udp server start {}".format(port))
        self.pexpect.expect("Success: started UDP server on port ([:0-9]+)")
        _port = self.pexpect.match.group(1)
        assert port == int(_port), "UDP server not started"

    def udp_send(self, addr, port, payload_size=10, count=3, delay_us=100000):
        self.pexpect.sendline("udp send {} {} {} {} {}"
                              .format(addr, port, payload_size, count,
                                      delay_us))
        self.pexpect.expect("udp send (?P<addr>[:0-9a-f]+) (?P<port>[:0-9]+)" +
                            " (?P<payload>[:0-9]+) (?P<count>[:0-9]+) " +
                            "(?P<delay>[:0-9]+)")
        for i in range(0, count):
            self.pexpect.expect("Success: send (?P<payload>[:0-9]+) byte to " +
                                "\\[(?P<addr>[:0-9a-f]+)\\]:(?P<port>[:0-9]+)")

    def udp_send_single(self, addr, port, payload_size=10):
        self.pexpect.sendline("udp send {} {} {}".format(addr, port,
                                                         payload_size))
        self.pexpect.expect("Success: send (?P<payload>[:0-9]+) byte to " +
                            "\\[([:0-9a-f]+)\\]:(?P<port>[:0-9]+)")

        _payload = self.pexpect.match.group('payload')
        _port = self.pexpect.match.group('port')

        # TODO assert address value
        assert (int(_port) == port) and (int(_payload) == payload_size), \
            "UDP send error"

    def set_channel(self, iface, channel):
        self.pexpect.sendline("ifconfig {} set channel {}".format(iface,
                                                                  channel))
        self.pexpect.expect("success: set channel on interface ([:0-9]+) to " +
                            "([:0-9]+)")
        _iface = self.pexpect.match.group(1)
        _channel = self.pexpect.match.group(2)

        assert (int(_iface) == iface) and (int(_channel) == channel), \
            "Channel could not be set"

    def ping(self, count, dest_addr, payload_size, delay):
        self.pexpect.sendline(
                "ping6 {} {} {} {}".format(
                    count, dest_addr, payload_size, delay))
        packet_loss = None
        for i in range(count+1):
            exp = self.pexpect.expect(
                    ["bytes from", "([\\d]+) packets transmitted, ([\\d]+) received \
                     , ([\\d]+)% packet loss", "timeout",
                     pexpect.TIMEOUT], timeout=10)

            if exp == 1:
                packet_loss = int(self.pexpect.match.group(3))
                break
            if exp == 2:
                print("x", end="", flush=True)
            else:
                print(".", end="", flush=True)

        return packet_loss


class PktBuf:
    def extract_unused(self):
        self.pexpect.sendline("pktbuf")
        self.pexpect.expect("unused: ([0-9xa-f]+) ")
        return self.pexpect.match.group(1)
