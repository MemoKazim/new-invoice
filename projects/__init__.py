import os

report_folders = [f for f in os.listdir("projects") if "." not in f]

if not os.path.exists("../reports/invoices"): os.mkdir("../reports/invoices")

for folder in report_folders:
    if not os.path.exists(f"reports/{folder}"): os.mkdir(f"reports/{folder}")
