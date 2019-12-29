import json

from PyBugger import Report


class ReportIO:
    path_to_file = None
    report = None

    def __init__(self, path):
        self.path_to_file = path

    def save_as_json(self, report):
        self.report = report
        report_json = json.dumps(report, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        file = open(self.path_to_file, "w")
        file.writelines(report_json)
        file.close()

    def open_report(self):
        file = open(self.path_to_file, 'r')
        raw_json = file.read()
        report = Report(raw_json=raw_json)
        return report
