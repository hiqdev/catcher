#!/usr/bin/env python

from random import randint

class Random:
    def __init__(self, items):
        self.keys = items.keys()
        self.vals = items.values()
        self.last = len(items)-1

    def random_key(self):
        # TODO implement non uniform distribution
        return self.keys[randint(0, self.last)]

