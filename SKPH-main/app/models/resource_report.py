class ResourceReport:
    def __init__(self, report_id, created_at, entries):
        self.report_id = report_id
        self.created_at = created_at
        self.entries = entries

    def to_dict(self):
        return {
            "report_id": self.report_id,
            "created_at": self.created_at.isoformat(),
            "entries": self.entries
        }
