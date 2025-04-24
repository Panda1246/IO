# import csv
# import io
# import json
#
# class ReportGenerator:
#     @staticmethod
#     def to_json(report):
#         return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
#
#     @staticmethod
#     def to_csv(report):
#         fieldnames = ["resource_name", "quantity", "location"]
#         output = io.StringIO()
#         writer = csv.DictWriter(output, fieldnames=fieldnames)
#         writer.writeheader()
#         for entry in report.entries:
#             writer.writerow(entry)
#         return output.getvalue()
