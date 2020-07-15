import requests
import sqlite_utils
from dateutil import parser
from datetime import timezone

schedule_url = "https://raw.githubusercontent.com/OpenNews/srccon-2020/master/schedule/sessions.json"


def parse_times(s, datestring):
    begin, end = s.split(" ")[0].split("-")
    if not begin.endswith("m"):
        # Copy am/pm from end
        begin += end[-2:]
    begin_dt = parser.parse(
        begin + " ET " + datestring, tzinfos={"ET": "America/New_York"}
    )
    end_dt = parser.parse(end + " ET " + datestring, tzinfos={"ET": "America/New_York"})
    return begin_dt, end_dt


def transform_session(session):
    session = {k: v for k, v in session.items()}
    date = {
        "Wednesday": "2020-07-15",
        "Thursday": "2020-07-16",
        "Friday": "2020-07-17",
    }[session["day"]]
    start_ny, end_ny = parse_times(session["time"], date)
    session["event_name"] = session.pop("title")
    session["event_dtstart"] = start_ny.isoformat().split("+")[0]
    session["event_dtend"] = end_ny.isoformat().split("+")[0]
    session["event_description"] = session.pop("description")
    session["event_tzid"] = "America/New_York"
    session["event_uid"] = "srccon-2020/{}".format(session["id"])
    return session


if __name__ == "__main__":
    sessions = requests.get(schedule_url).json()
    db = sqlite_utils.Database("srccon.db")
    db["sessions"].insert_all(
        [transform_session(s) for s in sessions],
        pk="id",
        truncate=True,
        column_order=[
            "id",
            "day",
            "time",
            "event_name",
            "event_description",
            "facilitators",
        ],
    )
    db["sessions"].enable_fts(["event_name", "event_description", "facilitators"])
