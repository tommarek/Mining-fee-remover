#!python

import json
import logging
import os
import re
import string

from collections import OrderedDict
from netfilterqueue import NetfilterQueue
from scapy.all import *

logging.basicConfig(
    filename='/var/log/mining-fee-remover.log',
    filemode='w',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.DEBUG,
)
logger = logging.getLogger("mining-fee-remover")

class FeeRemover(object):
    SLASH_POOLS = ['nanopool.org','dwarfpool.com']
    DOT_POOLS = ['ethpool.org','ethermine.org','alpereum.ch']

    def __init__(self, pool, port, eth_wallet, password, worker_name=None):
        self.pool = pool
        self.port = port
        self.eth_wallet = self._format_wallet_string(eth_wallet)
        self.password = password
        self.worker_suffix = self._format_worker_suffix(pool, worker_name)

        #self.logfile = open('fee_remover.log', 'w', 0)

    def _format_worker_suffix(self, pool, worker_name):
        worker_suffix = ''
        if worker_name:
            if any(s in pool for s in self.SLASH_POOLS):
                worker_suffix = '/' + worker_name
            elif any(s in pool for s in self.DOT_POOLS):
                worker_suffix = '.' + worker_name
            else:
                logger.error('Unknown pool, no worker suffix will be used')
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

    def _callback(self, raw_pkt):
        pkt = IP(raw_pkt.get_payload())
        if 'load' in pkt[TCP].payload.fields:
            payload = pkt[TCP].payload.getfieldval('load')
            if b'submitLogin' in payload or b'eth_login' in payload:
                if not bytes(self.eth_wallet, 'utf-8') in payload:
                    logger.info('Received: "{0}"'.format(payload.decode().strip()))
                    new_payload = re.sub(b'0x[0-9A-Fa-f]+', bytes(self.eth_wallet, 'utf-8'), payload)
                    logger.info('Sending: "{0}"'.format(new_payload.decode().strip()))
                    pkt[TCP].payload.setfieldval('load', new_payload)

                    # update packet
                    #pkt[IP].len = pkt[IP].len + (len(new_pl_text) - pl_len)
                    pkt[IP].ttl = 64
                    del pkt[IP].chksum
                    del pkt[TCP].chksum
                    raw_pkt.set_payload(bytes(pkt))
            else:
                logger.debug('Sending: "{0}"'.format(payload.strip()))

        raw_pkt.accept()

    def run(self):
        logger.info('Starting mining fee remover...')
        os.system('iptables -A OUTPUT -p tcp --dport {0} -j NFQUEUE --queue-num 0'.format(int(self.port)))
        q = NetfilterQueue()
        q.bind(0, self._callback)
        logger.info('Started.')

        try:
            q.run()
        except KeyboardInterrupt:
            q.unbind()
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


