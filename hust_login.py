#!/usr/bin/env python3

import sys
import re
import binascii
import json
import Crypto
from Crypto.PublicKey import RSA
try:
    from Crypto.Cipher import PKCS1_v1_5
except ModuleNotFoundError:
    pass
from getpass import getpass
import urllib.request
import urllib.parse
import argparse

def get_zerobytes(N):
    return b'\0' * N

def encr_pw(pw):
    key = RSA.construct([0x9c2899b8ceddf9beafad2db8e431884a79fd9b9c881e459c0e1963984779d6612222cee814593cc458845bbba42b2d3474c10b9d31ed84f256c6e3a1c795e68e18585b84650076f122e763289a4bcb0de08762c3ceb591ec44d764a69817318fbce09d6ecb0364111f6f38e90dc44ca89745395a17483a778f1cc8dc990d87c3,0x10001])
    ohdave=""
    length=len(pw)
    for i in range(0,length):
        ohdave += pw[length-1-i]
    try:
        ciphertxt = key.encrypt(bytes(ohdave,'us-ascii'),0)[0]
    except NotImplementedError:
        cipher = PKCS1_v1_5.new(key)
        ciphertxt = cipher.encrypt(bytes(ohdave,'us-ascii'))
    return ciphertxt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="specify username in command line")
    parser.add_argument("-q", "--quiet", help = "only output when error occurs", action = "store_true")
    parser.add_argument("-p", "--pass", help = "specify password in command line, if used without any value, read from stdin without any prompt", const = "", default = None, nargs = "?", dest = "pw")
    args = parser.parse_args()
    try:
        resp = urllib.request.urlopen("http://123.123.123.123",timeout=5)
    except urllib.error.URLError:
        print("Failed to get redirect info, maybe already logged in?", file=sys.stderr)
        exit(1)
    if (resp.status != 200):
        print("Got unexpected HTTP status code "+str(resp.status), file=sys.stderr)
        exit(1)
    try:
        redirect_url = re.search(r"(http://[^']+)",str(resp.peek())).group()
        queryString = re.search(r"(\?.*$)",redirect_url).group()
        queryString = queryString.replace("?","")
        post_url = re.search(r"(http://.*/)",redirect_url).group()+"InterFace.do?method=login"
    except AttributeError:
        print("Got unexpected HTTP content\nresp.peek()="+str(resp.peek()),file=sys.stderr)
        exit(1)

    queryString = urllib.parse.quote_plus(urllib.parse.quote_plus(queryString))
    if args.user:
        userId = args.user
    else:
        print("Enter userId:")
        userId = input()
    if args.pw != None:
        if args.pw == "":
            pw = getpass(prompt='')
        else:
            pw = args.pw
    else:
        pw = getpass()
    post_data = "userId="+userId+"&password="+binascii.hexlify(encr_pw(pw)).decode('ascii')+"&service=&queryString="+queryString+"&operatorPwd=&validcode=&passwordEncrypt=true"
    resp = urllib.request.urlopen(post_url,bytes(post_data,'us-ascii'))
    authResult = json.loads(resp.peek().decode('utf-8'))            
    if (authResult["result"] == 'success'):
        if not args.quiet:
            print("Login successful!")
    else:
        print("Message from server: "+authResult["message"],file=sys.stderr)
        print("Login failed!",file=sys.stderr)
        exit(1)

if __name__ == '__main__':
    main()