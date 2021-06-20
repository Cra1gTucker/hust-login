# hust-login
**Command line** login scripts for HUST\_WIRELESS Wi-Fi, which enables logging into the campus network **without a browser**.

**2021-3-24**： 发现Bash脚本加密时openssl报错，排查加密出错原因，结果发现pubkey.pub有问题(E值错了)，但修正后还是登录失败。再对网页登录界面进行调试，结果发现在网页登录时调用的rsa实现库采用的端序方式似乎与openssl不一样，故Bash脚本不需要反转密码，同时为密码增加了两次URL Encode以与官方网页保持一致 *PS:不懂Python/Powershell，暂时不改*

**2020-9-29**： 学校工作人员认为老的加密算法不安全（JavaScript注释里写着的原话），于是修改了RSA密钥和服务端的解密方式。~~好像没有对加密算法做任何更改呢。~~ 现在服务端不再接受`PKCS#1 V1.5` padding的密文了，只接受~~不知从哪复制过来的~~JavaScript库里写的一种奇怪的padding，而恰好`Pycryptodome`又不支持自己写padding，更巧的是deprecated的`Pycrypto`却正好能够方便地实现这种padding，理论上使用后者或者shell脚本因为本来就是手写的padding甚至几乎不用改代码（正在测试当中）。

由于某些不可描述的原因，目前校园网密码使用了RSA加密而不是之前的明文传输。经检验[hust\_wireless.py](https://github.com/haoqixu/hust_wireless)仍然可以使用，**但是没有任何安全性**，本repo中含有根据当前登录方式重写的登录脚本。

## 用法
您可以根据需要选择下面的Python脚本或Shell脚本。
### Python脚本
---
`hust_login.py`和`hust_login_nocrypt.py`使用Python内置的`urllib`，使用时直接用python3运行即可

* **hust_login.py** 依赖`Pycrypto` ~~或`Pycryptodome`进行密码的加密，需要用户自行安装两模块中的任意一个~~
* **hust_login_nocrypt.py** 不依赖任何第三方模块，但是**不进行加密**，只是在原版本的POST参数后添加了`passwordEncrypt=false`以告知服务端接收明文


### Shell脚本
---
如果您~~不是Python选手~~出于某些原因没有安装Python，可以使用本脚本登录

**脚本依赖**：`curl`,`openssl`,`grep`以及一个bash-compatible的shell，大多数Linux发行版（甚至macOS）都已包含上述包。~~Alpine？不存在的~~

为了使用本脚本，您需要下载`hust_login.sh`以及`pubkey.pub`并置于同一目录中，后者存放了加密使用的RSA公钥

该脚本接受用户名作为唯一可选参数或向用户询问用户名，由于尝试完全按照校园网提供的JavaScript进行RSA padding造成脚本中有些可读性较差的部分（事实证明学校程序员认为这一padding有其高明之处，自2020年起只接受这种padding的密文了），~~请忽略~~

## FAQ

**为什么使用`Pycrypto`和使用`Pycryptodome`进行加密得到的密文不同？**
> ~~`Pycrypto`（以及校园网JavaScript）RSA加密使用的是全零padding，而`Pycryptodome`默认使用[PKCS#1 V1.5](https://en.wikipedia.org/wiki/PKCS_1) padding，这导致二者密文不同且后者每次加密得到的密文均有不同，但是事实证明经过后者padding的密文仍然可以被服务端成功解密。但由于后者加密padding带有随机数据实际上防止了对密文进行爆破，所以使用后者其实是更安全的选择。~~

> **注意**：现在校园网只认全零padding，后者无法使用。

**服务端返回“设备未认证”?**
> 实际使用中发现极少数情况下服务端会返回“设备未认证”消息，由于再次运行发现可以成功登录，所以未研究此现象的原因（可能是使用`urllib`没有存Cookie的原因？），出现上述情况，重新运行可以解决问题。自2020年起添加了一个参数，如果用的是之前的版本，请更新。
