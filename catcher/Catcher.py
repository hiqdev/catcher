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
        self.stats = None

    def dump(self):
        print "DUMP"
        pprint(self.config)

    def start(self):
        print "START"
        self._reload_domains()
        self._check_domains()
        #self.daemon = Daemon(config)
        #self.daemon.start()
        self._loop()

    def _loop(self):
        while True:
            time.sleep(0.5)
            domain = self.random.random_key()
            if 'count' in self.domains[domain]:
                self.domains[domain]['count'] += 1
            else:
                self.domains[domain]['count'] = 1
            #print '  %d %s' % (self.domains[domain]['count'], domain)
            self._refresh()

    def _refresh(self):
        if datetime.now() < self.lastRefreshed + self.refreshPeriod:
            return

        #print "- refresh"
        self.lastRefreshed = datetime.now()
        self._refresh_stats()
        if self.lastRefreshed > self.domainsLastReloaded + self.domainsReloadPeriod:
            self._reload_domains()
        if self.lastRefreshed > self.domainsLastChecked + self.domainsCheckPeriod:
            self._check_domains()

    def _refresh_stats(self):
        if not self.stats:
            self.stats = Config(self.config['statsFilePath'], False)
        else:
            self.stats.load(False)

        if not self.stats.lock():
            return

        for domain, data in self.domains.items():
            self.stats[domain] = self._merge_domain(self.stats.get(domain, {}), data)
            data['count'] = 0

        self.stats.save()

    def _merge_domain(self, stat, data):
        res = dict(data)
        res['count'] = stat.get('count', 0) + data.get('count', 0)
        return res

    def _reload_domains(self):
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
                self.domains[domain]['disabled'] = True

        self.random = Random(self.domains)
        #print "! DOMAINS RELOADED"
        self.domainsLastReloaded = datetime.now()
        self.domainsReloadPeriod = timedelta(**self.config['domainsReloadPeriod'])

    def _check_domains(self):
        self.domainsLastChecked = datetime.now()
        self.domainsCheckPeriod = timedelta(**self.config['domainsCheckPeriod'])
        #print "! DOMAINS CHECKED"
