# Try alpine docker

## Build enviroment

```
(base) ➜  ethos git:(main) ✗ docker run --name ethos --rm -it alpine /bin/sh
/ # apk update
/ # apk upgrade
/ # apk add bash
/ # apk add bash-completion

/ # cat /etc/shells
# valid login shells
/bin/sh
/bin/ash
/bin/bash
/ # /bin/bash

bash-5.1# apk add git
```

## Build FluffOS

```
bash-5.1# apk add linux-headers gcc g++ clang-dev make cmake python2 bash \
    mariadb-dev mariadb-static postgresql-dev sqlite-dev sqlite-static\
    libevent-dev libevent-static libexecinfo-dev libexecinfo-static \
    openssl-dev openssl-libs-static zlib-dev zlib-static icu-dev icu-static \
    pcre-dev bison
bash-5.1# wget -O - https://github.com/jemalloc/jemalloc/releases/download/5.2.1/jemalloc-5.2.1.tar.bz2 | tar -xj && \
    cd jemalloc-5.2.1 && \
    ./configure --prefix=/usr && \
    make && \
    make install

bash-5.1# git clone https://github.com/twinsant/fluffos
bash-5.1# cd fluffos/
bash-5.1# mkdir build
bash-5.1# cd build/
bash-5.1# cmake .. -DMARCH_NATIVE=OFF -DSTATIC=ON
bash-5.1# make install
```


## Run EthOS

### Run FluffOS

```
bash-5.1# git clone https://github.com/twinsant/ethos
bash-5.1# cd mudcore/
bash-5.1# git submodule init
bash-5.1# git submodule update

bash-5.1# cd ethos/
bash-5.1# ./bin/driver.alpine lib/config.ini
```