# coding=UTF-8
__author__ = 'zheng.zhenjia'

import sys
reload(sys)
sys.setdefaultencoding('utf8')  # @UndefinedVariable
import requests
import simplejson
import re
from jinja2 import Template
import os
import unittest
import pymysql
import time
from config import conf

folder = os.environ.get('CASE_FOLDER', "M0")
SUITE_DIR = os.path.join(os.path.dirname(__file__), folder)
path = SUITE_DIR


def backup_db(target):
    """
    :param target:  target for backup the database
    :return: null
    """
    # print 'Start to backup'
    command = '%s -h%s -u%s -p%s %s > %s' % (conf.btool, conf.host, conf.user, conf.psw, conf.dbname, target)
    #print command
    try:
        os.system(command)
        #print 'Success'
    except Exception, e:
        #print 'Fail'
        print e


def restore_db(source):
    """
    :param source:  the source for restore the sql data from specified location to the destination database.
    :return: null
    """
    # print 'Start to restore sql'
    command = '%s -h%s -u%s -p%s -P3306 %s < %s' % (conf.rtool, conf.host, conf.user, conf.psw, conf.dbname, source)
    #print command
    try:
        os.system(command)
        #print 'Success'
    except Exception, e:
        #print 'Fail'
        print e


def exec_sql(sql):
    """
    :param sql: sql language for query / update / add /delete for the test.
    :return:  data for query , null for update/delete and id or other key for add.
    """
    try:
        conn = pymysql.connect(host=conf.host, user=conf.user, passwd=conf.psw, db=conf.dbname, charset='utf8')
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        r = cur.fetchall()
        cur.close()
        conn.close()
        return r
    except Exception, e:
        print 'Mysql Error %d: %s' % (e.args[0], e.args[1])


class Context(object):
    """
    Define the Context to store the return value.
    """

    def __init__(self):
        self.lastResponse = []
        self.allResponses = []
        self.allValues = {}
        self.checker = None
        self.error = None
        self.valueDict = {}
        self.Keys = {}


def get_value_by_key(in_dict, param):
    """
    :param jdict:
    :param param:
    :return:
    """
    # value = {}
    if isinstance(in_dict, list):
        if type(in_dict).__name__ == "int":
            print "The response value is type int."
            pass
        else:
            for element in in_dict:
                if type(element).__name__ == "int":
                    pass
                else:
                    get_value_by_key(element,param)
                    if element.has_key(param):
                        value = element[param]
                    else:
                        pass
    elif isinstance(in_dict, dict):
        for key in in_dict.keys():
            if param == key:
                value = in_dict[param]
            if isinstance(in_dict[key], dict):
                get_value_by_key(in_dict[key], param)
                if param in in_dict[key].keys():
                    value = in_dict[param]
                else:
                    pass
    else:
        for x in in_dict.keys():
            get_value_by_key(in_dict[x], param)
            if x == param:
                value = in_dict[param]
                    #print Context.valueDict
            else:
                pass
    return value


def type_validator( params, value):
    if type(params).__name__ == value:
        return True
    else:
        return False


def type_in_validator( params, value):
    for key in value:
        if type(params).__name__ == key:
            return True
        else:
            pass
    return False


def between_validator(params, value):
    if not isinstance(params, int):
        return False
    if value[0] <= params  <= value[1]:
        return True
    else:
        return False


def values_validator(params, value):
    mark = 0;
    for i in xrange(len(value)):
        if params == value[i]:
            mark += 1
    if mark == len(value):
        return True
    else:
        return False


def len_validator(params, value):
    if len(params) == len(value) :
        return True
    else:
        return False


def equal_validator( params, value):
    if params == value:
        return True
    else:
        return False


def in_validator(param,value):
    lm = 0
    for i in range(len(value)):
        if param == value[i]:
            lm += 1
            print "Find the value in index : %d" % (i+1)
        else:
            pass
    if lm == 1:
        return True
    else:
        return False


def greater_validator(params, value):
    if params >= value:
        return True
    else:
        return False


def reg_validator(params, value):
    try:
        val = re.match(value, params)
        if val.group(0):
            return True
        else:
            return False
    except:
        return False


class ValidatorRegistry(object):

    registry = {}

    @classmethod
    def register(cls,name, validate):
        cls.registry[name] = validate

    @classmethod
    def validate(cls,name, params, value):
        return cls.registry[name].validate(params, value)

def checker(typo,params,value):
    val = ValidatorRegistry()
    if typo == "TYPE":
        val.register("TYPE", type_validator(params, value))
    if typo == "LEN":
        val.register("LEN", len_validator(params, value))
    if typo == "BETWEEN":
        val.register("BETWEEN", between_validator(params, value))
    if typo == "EQ":
        val.register("EQ", equal_validator(params, value))
    if typo == "IN":
        val.register("In", in_validator(params, value))
    if typo == "GE":
        val.register("GE", greater_validator(params, value))
    if typo == "RE":
        val.register("RE", reg_validator(params, value))
    if typo == "ALLIN":
        val.register("ALLIN", values_validator(params, value))
    if typo == "TYPEIN":
        val.register("TYPEIN", type_in_validator(params, value))
    return val.registry[typo]



def APIReq(input):
    """
    :param input:
    :return:
    """
    result = {}
    for key in input:
        if key != "method" and key != "clientType":
            dic = {key: input[key]}
            result.update(dic)
    url = "%s/%s" % (conf.url, input["clientType"])
    param = {"jsonrpc": "2.0", "params": result, "id": 100, "method": input["method"]}
    print "Request url:\n" + url
    print "The request parameter is: "
    print param
    resp = requests.post(url, json=param)
    print "This is the response from the request:"
    print resp.content.encode("utf-8")
    if resp.status_code != 200 or "error" in resp.content:
        return resp.json()["error"]["code"]
    result.update(resp.json())
    return result["result"]


def case_list(case_path):
    for root, dirs, files in os.walk(case_path):
        cases = dirs
        return cases


def get_test_steps(folder):
    """
    :param caseFolder:  Case folder to list.
    :return: The case step.
    """
    for root, dirs, files in os.walk(os.path.join(path, folder)):
        steps = []
        for each in files:
            each = os.path.join(os.path.join(path, folder), each)
            steps.append(each)
        return steps


# print getTestSteps(CaseList(path)[0])

# exit()
def check_resp(context, file):
    """
    :param context:
    :param file:
    :return: Boolean
    """
    val = open(file).read()
    # print val
    try:
        t = Template(val)
        val = t.render(key=context.allValues, last=context.lastResponse, all=context.allResponses, pre=conf.preData)
    except Exception,e:
        print e
        return False
    val = simplejson.loads(val)
    # print val

    if "sql" in val.keys():
        try:
            print val["sql"]
            result = exec_sql(val["sql"])
            print result
            if "SELECT" in val["sql"]:
                if "key" in val.keys() and isinstance(val["key"],list):
                    for i in xrange(len(val["key"])):
                        context.allValues.update({val["key"][i]: result[0][i]})
            if isinstance(result,tuple):
                print "SQL : Execute SQL PASS."
                return True
        except Exception, e:
            print e
            print "SQL : Execute SQL FAIL."
            return False
    else:
        ret = APIReq(val["input"])
        if val["output"] is None:
            if ret is None:
                return True
            else:
                print "Expected null but actually return not null."
                return False
        # print type(ret)
        if "key" in val.keys():
            if isinstance(ret, int) and re.findall("-[\d]{5}", str(ret)):
                return False
            if isinstance(ret,dict):
                for i in xrange(len(val["key"])):
                    ma = re.findall("[a-z]*[1-9]{1}", val["key"][i])
                    if ma:
                        value = get_value_by_key(ret, val["key"][i][0:-1])
                    else:
                        value = get_value_by_key(ret, val["key"][i])
                    context.allValues.update({val["key"][i]: value})
            else:
                context.allValues.update({val["key"][0]: ret})

        if "code" not in val["output"].keys():
            count = 0
            for each in val["output"].keys():

                if isinstance(ret, int) and re.findall("-[\d]{5}", str(ret)):
                    print "Response the error code but actually need the result without error."
                    return False
                try:
                    if not isinstance(ret, dict) and not isinstance(ret, list):
                        if not isinstance(ret, int):
                            ret = ret.encode("utf-8")
                        if checker(each, ret, val["output"][each]):
                            count += 1
                        else:
                            print "Response : %s is FAIL." % ret
                            return False
                    else:
                        for typo in val["output"][each].keys():
                            if not checker(typo, ret[each], val["output"][each][typo]):
                                print "Checker for key: %s is FAIL." % each
                                return False
                        count += 1
                except Exception, e:
                    print e
                    return False
        else:
            if val["output"]["code"] == ret:
                return True
            else:
                print "There is no error code response for the abnormally case."
                return False
        if count == len(val["output"].keys()):
            return True


def check_case(con, cases):
    sleep_time = float(os.environ.get('SLEEP_TIME', 0))
    time.sleep(sleep_time)
    mark = 0
    for x in xrange(len(cases)):
        print "This is %d step running: " % (x+1)
        print "-"*100
        if check_resp(con, cases[x]):
            mark += 1
        else:
            print "Step %x is FAIL.\n" % (x+1) + "-"*100
            return False
        print "-"*100+"\n"
    if mark == len(cases):
        return True


class UnitTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        backup_db("%s/backup.sql" % os.path.join(os.path.dirname(os.path.abspath(__file__)), "sqldata"))

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        restore_db("%s/backup.sql" % os.path.join(os.path.dirname(os.path.abspath(__file__)), "sqldata"))

    def run_case(self, steps):
        print "Start the test:"
#         for each in allStepList:
        context = Context()
        self.assertTrue(check_case(context, steps), "TEST FAIL")

    @staticmethod
    def get_test_func(steps):
        def func(self):
            self.run_case(steps)
        return func


def __generate_test_cases():
    lists = []
    cases = case_list(SUITE_DIR)
    for i in xrange(len(cases)):
        steps = get_test_steps(cases[i])
        lists.append(steps)
    item = int(os.environ.get('UT_ITEM', -1))
    # print '-' * 60
    # if item == -1:
    #     print 'current test suite is ALL TESTS'
    # else:
    #     print 'current test item is: %d' % (item+1)
    # print '-' * 60
    if item == -1:
        for i in xrange(len(lists)):
            test_func = "test_" + cases[i]
            setattr(UnitTest, test_func, UnitTest.get_test_func(lists[i]))
    else:
        test_func = "test_" + cases[item]
        setattr(UnitTest, test_func, UnitTest.get_test_func(lists[item]))

__generate_test_cases()


def suite():
    lists = []
    cases = case_list(SUITE_DIR)
    for i in xrange(len(cases)):
        steps = get_test_steps(cases[i])
        lists.append(steps)
    item = int(os.environ.get('UT_ITEM', -1))

    print '-' * 60
    if item == -1:
        print 'current test suite is ALL TESTS'
    else:
        print 'current test item is: %d' % (item+1)
    print '-' * 60

    if item == -1:
        for i in xrange(len(lists)):
            test_func = "test_" + cases[i]
            setattr(UnitTest, test_func, UnitTest.get_test_func(lists[i]))
    else:
        test_func = "test_" + cases[item]
        setattr(UnitTest, test_func, UnitTest.get_test_func(lists[item]))
    suit = unittest.TestSuite()
    suit.addTest(unittest.makeSuite(UnitTest))
    return suit
#
# if __name__ == "__main__":
#     restoreDB("%s/backup.sql" % os.path.join(os.path.dirname(os.path.abspath(__file__)),"sqldata"))