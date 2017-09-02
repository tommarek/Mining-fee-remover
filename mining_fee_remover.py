#!/usr/bin/env python

import json
import logging
import nfqueue
import os
import re
import string

from collections import OrderedDict
from scapy.all import *


logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

class FeeRemover(object):
    SLASH_POOLS = ['nanopool.org','dwarfpool.com']
    DOT_POOLS = ['ethpool.org','ethermine.org','alpereum.ch']

    def __init__(self, pool, port, eth_wallet, password, worker_name=None):
        self.pool = pool
        self.port = port
        self.eth_wallet = self._format_wallet_string(eth_wallet)
        self.password = password
        self.worker_suffix = self._format_worker_suffix(pool, worker_name)

        self.logfile = open('fee_remover.log', 'w', 0)

    def _format_worker_suffix(self, pool, worker_name):
        worker_suffix = ''
        if worker_name:
            if any(s in pool for s in self.SLASH_POOLS):
                worker_suffix = '/' + worker_name
            elif any(s in pool for s in self.DOT_POOLS):
                worker_suffix = '.' + worker_name
            else:
                print 'Unknown pool, no worker suffix will be used'
        return worker_suffix

    def _format_wallet_string(self, eth_wallet):
        if len(eth_wallet) == 40:
            addr = eth_wallet
        elif len(eth_wallet) == 42:
            addr = eth_wallet[2:]
        else:
            addr = '0x'

        if all(c in string.hexdigits for c in addr):
            return '0x' + addr
        else:
            raise ValueError('eth_wallet in wrong format')

    def _callback(self, payload):
        data = payload.get_data()
        pkt = IP(data)

        pl_text, pl_len = str(pkt[TCP].payload), len(pkt[TCP].payload)
        new_pl_text, new_pl_len = pl_text, pl_len

        # edit the payload here
        if pl_text:
            if 'eth_submitLogin' in pl_text:
                if not self.eth_wallet in pl_text:
                    print 'Received: "{0}"'.format(pl_text.strip())
                    #new_pl_text = re.sub(r'"0x[0-9A-Fa-f\.\/]+.*?"', '"'+self.eth_wallet+self.worker_suffix+'"', pl_text)
                    new_pl_text = re.sub(r'0x[0-9A-Fa-f]+', self.eth_wallet, pl_text)
                    print 'Sending: "{0}"'.format(new_pl_text.strip())

            # update packet
            pkt[TCP].payload.setfieldval('load', new_pl_text)
            pkt[IP].len = pkt[IP].len + (len(new_pl_text) - pl_len)
            pkt[IP].ttl = 64
            del pkt[IP].chksum
            del pkt[TCP].chksum

        # update it
        payload.set_verdict_modified(nfqueue.NF_ACCEPT, str(pkt), len(pkt))

    def run(self):
        print 'Starting mining fee remover...'
        os.system('iptables -A OUTPUT -p tcp --dport {0} -j NFQUEUE --queue-num 0'.format(int(self.port)))
        q = nfqueue.queue()
        q.open()
        q.set_callback(self._callback)
        q.create_queue(0)
        print 'Started.'

        try:
            q.try_run()
        except KeyboardInterrupt:
            q.unbind(socket.AF_INET)
            q.close()
        finally:
            os.system('iptables -D OUTPUT -p tcp --dport {0} -j NFQUEUE --queue-num 0'.format(int(self.port)))

if __name__ == "__main__":
    fr = FeeRemover(
        pool='eu1.ethermine.org',
        port=4444,
        eth_wallet='0xda3e1e7822589a26e9705E184fC340e0731935eA',
        password='x',
        #worker_name='wizard2', # TODO: this doesn't work atm because of packet length (probably)
    )
    fr.run()


