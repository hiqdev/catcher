#!/usr/bin/env python

import os
import sys
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
        self.name = config.get('name', config['epp']['host'])
        self.num = config['catchersNum']
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

    def systemd(self):
        name = sys.argv[3]
        func = 'systemd_' + name
        if hasattr(self, func):
            getattr(self, func)()
        else:
            self.systemd_runcmd(name)

    def systemd_up(self):
        self.systemd_setup()
        self.systemd_runcmd('enable')
        self.systemd_runcmd('start')

    def systemd_down(self):
        self.systemd_setup()
        self.systemd_runcmd('stop')
        self.systemd_runcmd('disable')

    def systemd_status(self):
        self.systemd_unsafe('status')

    def systemd_runcmd(self, command):
        for i in range(self.num):
            self.runcmd('systemctl %s %s' % (command, self.systemd_service_name(i)))

    def systemd_unsafe(self, command):
        for i in range(self.num):
            self.unsafe('systemctl %s %s' % (command, self.systemd_service_name(i)))

    def runcmd(self, command):
        ret = self.unsafe(command)
        if ret:
            raise Exception('failed ' + command)

    def unsafe(self, command):
        print command
        return os.system(command)

    def systemd_setup(self):
        with open(self.systemd_service_path(), 'w') as file:
            file.write(self.systemd_service_config())

    def systemd_service_path(self):
        return '/etc/systemd/system/' + self.systemd_service_name()

    def systemd_service_name(self, no = ''):
        return 'catcher-%s@%s.service' % (self.name, no)

    def systemd_service_config(self):
        return '''\
[Unit]
Description=Catcher {name} %i
StopWhenUnneeded=true

[Service]
WorkingDirectory={work_dir}
ExecStart={bin_path} {config_path} start
Restart=always
User=root
Group=root

[Install]
WantedBy=multi-user.target
'''.format(
            name=self.name,
            work_dir=os.path.dirname(os.path.dirname(self.config.bin_path)),
            bin_path=self.config.bin_path,
            config_path=self.config.abs_path
        )

    def _loop(self):
        while True:
            time.sleep(0.5)
            domain = self.random.random_key()
            if 'count' in self.domains[domain]:
                self.domains[domain]['count'] += 1
            else:
                self.domains[domain]['count'] = 1
            print '  %d %s' % (self.domains[domain]['count'], domain)
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
            self.stats = Config(self.config.get_path('statsFilePath'), False)
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
        alldoms = Config(self.config.get_path('domainsFilePath'))

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
