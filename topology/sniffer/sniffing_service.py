from __future__ import absolute_import

import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import threading
from threading import Lock

from topology.sniffer.daemon import SniffingDaemon

from service.components import Component
from service.server import Server
from service.server import config

class PacketExporter(Component):
    def __init__(self, shared_packets, lock):
        self.shared_packets = shared_packets
        self.lock = lock

    def process(self, unused=None):
        self.lock.acquire()

        packets = self.shared_packets[:]
        self.shared_packets[:] = []

        self.lock.release()
        return packets

class SniffingService():
    def __init__(self, ):
        shared_lock = Lock()
        shared_list = []

        self.server = Server("sniffer", config["sniffer"])
        self.server.add_component_get("/newpackets",
            PacketExporter(shared_list, shared_lock))

        self.daemon = SniffingDaemon(shared_list, shared_lock)

def sniffing_service():
    service = SniffingService()

    threading.Thread(target=service.server.run).start()
    threading.Thread(target=service.daemon.run).start()

if __name__ == "__main__":
    sniffing_service()