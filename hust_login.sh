#!/usr/bin/env bash

rawurlencode() {
  local string="${1}"
  local strlen=${#string}
  local encoded=""
  local pos c o

  for (( pos=0 ; pos<strlen ; pos++ )); do
     c=${string:$pos:1}
     case "$c" in
        [-_.~a-zA-Z0-9] ) o="${c}" ;;
        * )               printf -v o '%%%02x' "'$c"
     esac
     encoded+="${o}"
  done
  echo "${encoded}"
}

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ $# -gt 1 ]
then
  echo "Usage: $0 <userId>"
  exit 1
fi

INFO=$(curl -sm 3 http://123.123.123.123)
if [ $? -ne 0 ]
then
  echo "Failed to get redirect page info!"
  exit 1
fi

if [ $# -ne 1 ]
then
  echo -n "Enter userId:"
  read USER
else
  USER=$1
fi

SUFFIX='/eportal/InterFace.do?method=login'
URL=$(echo $INFO|grep -oe "http://[^/]*")
URL="$URL$SUFFIX" #get post URL
QS=$(echo $INFO|grep -oe "wlan[^']*") #get query string
QS=`rawurlencode $(rawurlencode "$QS")`

echo -n "Password:"
read -s PASS
echo -e '\n'
LEN=$(echo -n "$PASS"|wc -c)

# start padding password, assuming password is LESS than 128 bytes long
PADDED=$(mktemp)
while [ $LEN -lt 128 ]
do
  echo -ne '\0' >> $PADDED
  LEN=$(expr $LEN + 1)
done
echo -n `rev <<< "$PASS"` >> $PADDED

# encrypt and build post data
PASS=`cat $PADDED|openssl rsautl -encrypt -pubin -inkey "$DIR/pubkey.pub" -raw|xxd -ps -c 256`
POST="userId=$USER&password=$PASS&service=&queryString=$QS&operatorPwd=&operatorUserId=&validcode=&passwordEncrypt=true"
rm $PADDED

# get response
if [ $(curl -sd "$POST" $URL|grep 'success') ]
then
  echo "Login successful!"
else
  echo "Login failed!"
fi
