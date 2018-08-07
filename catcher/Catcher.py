#!/usr/bin/env python

import time
from datetime import timedelta
from datetime import datetime

from pprint import pprint

from catcher.Random import Random
from heppy.Config import Config
from heppy.Daemon import Daemon

class Catcher:
    def __init__(self, config):
        self.config = config
        self.refreshPeriod = timedelta(**config['mainRefreshPeriod'])
        self.lastRefreshed = datetime.now()
        self.domains = {}

    def dump(self):
        print "DUMP"
        pprint(self.config)

    def start(self):
        print "START"
        self.reload_domains()
        self.check_domains()
        #self.daemon = Daemon(config)
        #self.daemon.start()
        self.loop()

    def loop(self):
        while True:
            time.sleep(0.5)
            print '  ' + self.random.random_key()
            self.refresh()

    def refresh(self):
        if datetime.now() < self.lastRefreshed + self.refreshPeriod:
            return

        print "- refresh"
        self.lastRefreshed = datetime.now()
        self.refresh_stats()
        if self.lastRefreshed > self.domainsLastReloaded + self.domainsReloadPeriod:
            self.reload_domains()
        if self.lastRefreshed > self.domainsLastChecked + self.domainsCheckPeriod:
            self.check_domains()

    def refresh_stats(self):
        stats = Config(self.config['statsFilePath'])

    def reload_domains(self):
        alldoms = Config(self.config['domainsFilePath'])

        for domain in alldoms:
            since = datetime.strptime(alldoms[domain]['since'], '%Y-%m-%d %H:%M:%S')
            if since > datetime.now() or 'taken-by' in alldoms[domain]:
                alldoms[domain]['disabled'] = True
            else:
                if domain in self.domains:
                    self.domains[domain].update(alldoms[domain])
                else:
                    self.domains[domain] = alldoms[domain]

        for domain in self.domains.keys():
            if not domain in alldoms or 'disabled' in alldoms[domain]:
                del self.domains[domain]

        self.random = Random(self.domains)
        pprint(self.domains)
        print "! DOMAINS RELOADED"
        self.domainsLastReloaded = datetime.now()
        self.domainsReloadPeriod = timedelta(**self.config['domainsReloadPeriod'])

    def check_domains(self):
        self.domainsLastChecked = datetime.now()
        self.domainsCheckPeriod = timedelta(**self.config['domainsCheckPeriod'])
        print "! DOMAINS CHECKED"
