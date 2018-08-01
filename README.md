# Catcher

[![GitHub version](https://badge.fury.io/gh/hiqdev%2Fcatcher.svg)](https://badge.fury.io/gh/hiqdev%2Fcatcher)
[![Scrutinizer Code Coverage](https://img.shields.io/scrutinizer/coverage/g/hiqdev/catcher.svg)](https://scrutinizer-ci.com/g/hiqdev/catcher/)
[![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/g/hiqdev/catcher.svg)](https://scrutinizer-ci.com/g/hiqdev/catcher/)

## Use

```sh
./bin/catcher config.json start
```

## Main Configuration File

```json
{
    "mainRefreshPeriod": {"minutes": 1},
    "domainsCheckPeriod": {"minutes": 10},
    "domainsReloadPeriod": {"minutes": 3},

    "domainsFilePath": "etc/my-domains.json",

    "epp": {
        "host":         "epp.verisign-grs.com",
        "port":         700,
        "bind":         "1.2.3.4",
        "login":        "mylogin",
        "password":     "mypassword",
        "certfile":     "ssl/my.com.cert",
        "keyfile":      "ssl/my.com.key",
        "ca_certs":     "ssl/my.com.intermediate"
    }
}
```

## Domains List File

```json
{
    "facebook.com": {
        "since": "2018-08-01 01:01:01",
        "weight": 100
    },
    "google.com": {
        "since": "2018-08-01 15:03:01",
        "weight": 200
    },
    "yahoo.com": {
        "since": "3018-08-01 15:04:30",
        "weight": 900
    },
    "example.com": {
        "since": "2018-08-01 15:03:01",
        "weight": 200,
        "taken-by": "regid"
    }
}
```

## How it works

- Reads main configuration file
- Reads domain list file (rereads periodically)
- Sends as many `domain:register` commands as possible
- Periodically checks domains list to mark already registered domains

## License

This project is released under the terms of the BSD-3-Clause [license](LICENSE).
Read more [here](http://choosealicense.com/licenses/bsd-3-clause).

Copyright © 2018, HiQDev (http://hiqdev.com/)
