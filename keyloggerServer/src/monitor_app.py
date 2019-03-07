from tornado.web import Application, RequestHandler, URLSpec
from tornado.gen import coroutine as tornado_coroutine

from bson.json_util import dumps

from report_collector import ReportCollector


class MonitorApp(Application):
    def __init__(self, args):
        handlers = [
            URLSpec(r"/", UsersHandler, name="index"),
            URLSpec(r"/user/([0-9a-f]+)", UserDetailHandler, name="userDetail"),
        ]
        super(MonitorApp, self).__init__(handlers,
                                  template_path="templates/monitor")

        self.report_collector = ReportCollector(args.db)


class BaseMonitorHandler(RequestHandler):
    def report_collector(self):
        return self.application.report_collector


class UsersHandler(BaseMonitorHandler):
    @tornado_coroutine
    def get(self):
        users = yield self.report_collector().get_users()
        self.render("index.html", users=users)


class UserDetailHandler(BaseMonitorHandler):
    @tornado_coroutine
    def get(self, user_id):
        user = yield self.report_collector().get_user(user_id)
        if user:
            self.render("user.html", user=user)
        else:
            self.finish("O.o")

