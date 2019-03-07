"""
todo:
    - hook obfuscation
    - 304
"""

from sys import stdout

from tornado.web import Application, RequestHandler
from tornado.template import Template
from tornado.httpserver import HTTPServer
from tornado.gen import coroutine as tornado_coroutine

from json import loads
from jsmin import jsmin

from report_collector import ReportCollector

def debug_log(str):
    print(str)
    stdout.flush()

class CollectorApp(Application):
    def __init__(self, args):
        handlers = [
            (r"/report", ReportHandler),
            (r"/hook", HookHandler)
        ]
        super(CollectorApp, self).__init__(handlers,
                                  cookie_secret="da1wdaw9mewMlqme9pokdwFrgCipetvqkdOqwd=d48g4")

        self.report_collector = ReportCollector(args.db)

        self.http_hook = CollectorApp.compile_hook("http", args.hook_host, args.hook_port_http, "report")
        self.https_hook = CollectorApp.compile_hook("https", args.hook_host, args.hook_port_https, "report")

    @staticmethod
    def compile_hook(protocol, host, port, path):
        with open("templates/hook.js", "r") as f:
            t = Template(f.read())
            js = t.generate(
                protocol=protocol,
                host=host,
                port=str(port),
                path=path
            )
            return jsmin(js)


class BaseRequestHandler(RequestHandler):
    def get_remote_ip(self):
        return self.request.headers.get("X-Forwarded-For", self.request.remote_ip)

class HookHandler(BaseRequestHandler):
    def get(self):
        debug_log("Serving hook to %s" % self.get_remote_ip())
        self.set_header("Content-Type", 'text/javascript; charset="utf-8"')
        protocol = self.request.headers.get("X-Forwarded-Proto")
        if protocol == "https":
            self.finish(self.application.https_hook)
        else:
            self.finish(self.application.http_hook)


class ReportHandler(BaseRequestHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", self.request.headers.get("Origin", "*"))
        self.set_header("Access-Control-Allow-Methods", "POST,OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header("Access-Control-Allow-Credentials", "true")

    # CORS preflight
    def options(self):
        self.set_header("Allow", "POST,OPTIONS")
        self.finish()

    @tornado_coroutine
    def post(self):
        debug_log("Receiving report from %s" % self.get_remote_ip())
        report = loads(self.request.body)
        yield self.application.report_collector.save(report, self)

        self.finish({
            "msg": "thank you for your cooperation"
        })
