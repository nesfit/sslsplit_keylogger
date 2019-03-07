#!/usr/local/bin/python

from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer

from multiprocessing import Process
from subprocess import call, Popen
from argparse import ArgumentParser
from time import sleep
from signal import SIGKILL
from os import kill
from os.path import isfile

from collector_app import CollectorApp
from monitor_app import MonitorApp


def spawn_worker(args, worker_id, port):
    print("Starting Collector Server worker %d at port %s" % (worker_id, port))
    
    http_server = HTTPServer(CollectorApp(args))
    http_server.listen(port, address="127.0.0.1")
    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass

def spawn_monitor(args):
    print("Starting Monitor Server at port %d" % args.monitor_port)

    http_server = HTTPServer(MonitorApp(args))
    http_server.listen(args.monitor_port, address="127.0.0.1")
    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--workers_num", type=int, default=2)
    arg_parser.add_argument("--workers_base_port", type=int, default=9000)
    arg_parser.add_argument("--hook_host", type=str, default="192.168.1.116")
    arg_parser.add_argument("--hook_port_http", type=int, default=80)
    arg_parser.add_argument("--hook_port_https", type=int, default=443)
    arg_parser.add_argument("--db", type=str, default="localhost")
    arg_parser.add_argument("--haproxy_config", type=str, default="/tmp/haproxy/haproxy.conf")
    arg_parser.add_argument("--monitor_port", type=int, default=7080)
    args = arg_parser.parse_args()
    
    # Security check
    if not isfile(args.haproxy_config):
        raise "Invalid HAProxy config file"

    if args.workers_num == 0:
        raise "No workers specified"

    # Create collector workers and prepare HAProxy config
    haproxy_config_file = open(args.haproxy_config, "a")
    workers = []
    for i in range(args.workers_num):
        # Create and start worker process
        w_port = args.workers_base_port + i
        w = Process(target=spawn_worker, args=(args, i, w_port,))
        workers.append(w)
        w.start()

        # Create backend server entry in HAProxy config
        haproxy_config_file.write("\tserver collector%d localhost:%d check\n" % (i, w_port))
    
    haproxy_config_file.close()

    # Run monitor server
    w = Process(target=spawn_monitor, args=(args,))
    workers.append(w)
    w.start()

    print("Starting HAProxy ...")
    # Run HAProxy
    sleep(0.5)
    haproxy_proc = Popen(["haproxy", "-f", args.haproxy_config]) 
    print("HAProxy started")

    try:
        for w in workers:
            w.join()    
    except KeyboardInterrupt:
        pass
    finally:
        for w in workers:
            w.terminate()
        haproxy_proc.terminate()

if __name__ == '__main__':
    main()
