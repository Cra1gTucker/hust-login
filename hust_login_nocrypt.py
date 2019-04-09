#!/usr/bin/python3

import re
import binascii
import json
from getpass import getpass
import urllib.request
import urllib.parse

try:
    resp = urllib.request.urlopen("http://123.123.123.123",timeout=5)
except urllib.error.URLError as e:
    print("Failed to get redirect info, maybe already logged in?")
    exit(1)
if (resp.status != 200):
    print("Got unexpected HTTP status code "+str(resp.status))
    exit(1)
try:
    redirect_url = re.search(r"(http://[^']+)",str(resp.peek())).group()
    queryString = re.search(r"(\?.*$)",redirect_url).group()
    queryString = queryString.replace("?","")
    post_url = re.search(r"(http://.*/)",redirect_url).group()+"InterFace.do?method=login"
except AttributeError as e:
    print("Got unexpected HTTP content\nresp.peek()="+str(resp.peek()))
    exit(1)

queryString = urllib.parse.quote_plus(urllib.parse.quote_plus(queryString))
print("Enter userId:")
userId = input()
pw = getpass()
post_data = "userId="+userId+"&password="+pw+"&service=&queryString="+queryString+"&operatorPwd=&validcode=&passwordEncrypt=false"
resp = urllib.request.urlopen(post_url,bytes(post_data,'us-ascii'))
authResult = json.loads(resp.peek().decode('utf-8'))
print("Message from server: "+authResult["message"])
if (authResult["result"] == 'success'):
    print("Login successful!")
else:
    print("Login failed!")
    exit(1)
