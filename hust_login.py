#!/usr/bin/env python3

import sys
import re
import binascii
import json
import rsa # to fit new crypto algorithm

from getpass import getpass
import urllib.request
import urllib.parse
import argparse

def get_zerobytes(N):
    return b'\0' * N

class REncrypt(object):
    def __init__(self,e,m):
        self.e = e
        self.m = m
    def encrypt(self,message):
        mm = int(self.m, 16)
        ee = int(self.e, 16)
        rsa_pubkey = rsa.PublicKey(mm, ee)
        crypto = self._encrypt(message.encode(), rsa_pubkey)
        return crypto.hex()
    def _pad_for_encryption(self, message, target_length):
        message = message[::-1]
        max_msglength = target_length - 11
        msglength = len(message)
 
        padding = b''
        padding_length = target_length - msglength - 3
 
        for i in range(padding_length):
            padding += b'\x00'
 
        return b''.join([b'\x00\x00',padding,b'\x00',message])
    def _encrypt(self, message, pub_key):
        keylength = rsa.common.byte_size(pub_key.n)
        padded = self._pad_for_encryption(message, keylength)
 
        payload = rsa.transform.bytes2int(padded)
        encrypted = rsa.core.encrypt_int(payload, pub_key.e, pub_key.n)
        block = rsa.transform.int2bytes(encrypted, keylength)
        return block

    @staticmethod
    def RuijieEncrypt(m,e,mac,pw):
        pw = "".join([pw, '>', mac])
        pw = pw[::-1]
        inst = REncrypt(e,m)
        return str(inst.encrypt(pw))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="specify username in command line")
    parser.add_argument("-q", "--quiet", help = "only output when error occurs", action = "store_true")
    parser.add_argument("-p", "--pass", help = "specify password in command line, if used without any value, read from stdin without any prompt", const = "", default = None, nargs = "?", dest = "pw")
    parser.add_argument("-c", "--cipher", help = "specify password cipher text in hex, will override '-p'")
    args = parser.parse_args()
    try:
        resp = urllib.request.urlopen("http://192.168.50.1",timeout=5)
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
        returned_mac = re.search(r"mac=([^&]*)",redirect_url).group()
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
    elif args.cipher:
        pass
    else:
        pw = getpass()
    pw = args.cipher if args.cipher else REncrypt.RuijieEncrypt("94dd2a8675fb779e6b9f7103698634cd400f27a154afa67af6166a43fc26417222a79506d34cacc7641946abda1785b7acf9910ad6a0978c91ec84d40b71d2891379af19ffb333e7517e390bd26ac312fe940c340466b4a5d4af1d65c3b5944078f96a1a51a5a53e4bc302818b7c9f63c4a1b07bd7d874cef1c3d4b2f5eb7871","10001",returned_mac,pw)
    post_data = "userId="+userId+"&password="+pw+"&service=&queryString="+queryString+"&operatorPwd=&operatorUserId=&validcode=&passwordEncrypt=true"
    resp = urllib.request.urlopen(post_url,bytes(post_data,'us-ascii'))
    authResult = json.loads(resp.peek().decode('utf-8'))            
    if (authResult["result"] == 'success'):
        if not args.quiet:
            print("Login successful!")
    else:
        print("Message from server: "+authResult["message"],file=sys.stderr)
        print("Login failed!",file=sys.stderr)
        exit(1)
    exit(0)

if __name__ == '__main__':
    main()
