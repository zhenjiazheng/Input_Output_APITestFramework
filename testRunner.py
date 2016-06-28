# -*- coding: utf-8 -*-
"""
Author: Zheng.zhenjia
"""

from unittest import TestSuite

from HTMLTestRunner import HTMLTestRunner as tr
from testReport import TestReport

# from util.sendEmail import send_email
import platform

DASH = '__'


def test_suite():
#     moduleNames=build_test_suite()
    if "Windows" in platform.platform():
        module_names = ["API-Windows"]
    else:
        module_names = ["API"]
    suite = TestSuite()

    for module_name in module_names:
        #print module_name
        import importlib
        m = importlib.import_module(module_name)
        #modules=map(__import__,moduleNames)
        suite.addTest(m.suite())
        #suite.addTest(element(module.suite()))
    return suite


def main():
    global report_file, runner, fp, Report_title
#     tolist=cfgValue.mailToList
#    tolist = mailToList = ["zzj@echiele.com","liubaohua@echiele.com","yehaiyuan@echiele.com","xiaowang@echiele.com"]
    report = "report"
    report_file = TestReport.generate_report(report)
    runner = tr()
    fp = file(report_file, 'wb')
    report_title = report + DASH + test_suite.__name__
    runner = tr(stream=fp, title=report_title, description=report_file)
    runner.run(test_suite())
    fp.close()
    #send_the_Mail(report_file, tolist)


if __name__ == '__main__':
    main()