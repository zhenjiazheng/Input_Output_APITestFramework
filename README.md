# requests-framework-api-test

The API automation test framework base on python requests plugin.

The data input and output check is like,example:
Step1:
{
    "input":{"clientType":"ClientService","method":"user_login","account":"{{pre.User1}}","password":"123456"},
    "output":{"TYPE":"str"},
    "key":["sessionId"]
}

Step2:
{
    "input":{"clientType":"ClientService","method":"user_logout","sessionId":"{{key["sessionId"]}}"},
    "output":null
}

The start running method:
3 parameters:
1. Case Number
2. Cases Folder
3.SleepTime, support second,milisecond,default 0 second.

command:
python main.py 3 "milestones/Test/client" 1
