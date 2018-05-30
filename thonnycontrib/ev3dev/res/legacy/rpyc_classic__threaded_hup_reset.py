#!/usr/bin/env python3
import sys
import os
import rpyc
import socket

from rpyc.utils.server import ThreadedServer, ForkingServer, OneShotServer
from rpyc.utils.classic import DEFAULT_SERVER_PORT, DEFAULT_SERVER_SSL_PORT
from rpyc.core import SlaveService
from rpyc.lib import setup_logger
import signal



def _handle_sighup(myrpcserver, signum, unused):
    """Closes (terminates) all of its clients. Though keeps server running."""
    print("SIGHUP: stopping all clients",sys.stderr)
    if myrpcserver._closed:
        return
    for c in set(myrpcserver.clients):
        try:
            c.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        c.close()
    myrpcserver.clients.clear()

ThreadedServer._handle_sighup = _handle_sighup



setup_logger(False, None)

myrpcserver = ThreadedServer(SlaveService, hostname = "", port = DEFAULT_SERVER_PORT, reuse_addr = True, ipv6 = False)
signal.signal(signal.SIGHUP, myrpcserver._handle_sighup)

myrpcserver.start()
