#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-03
#

"""Simple tests for Duden parser."""

from __future__ import print_function, unicode_literals

# from pprint import pprint

from workflow import Workflow
import duden

wf = Workflow()
duden.log = wf.logger

terms = [
    'Untergang',
    'Lageru',
    'Eröffnung',
    'skandieren',
    'Pumps',
    'in puncto',
]


for t in terms:

    results = duden.lookup(t)
    print('{} results for `{}`'.format(len(results), t))

    for d in results:
        print(d['term'])
        print(d['description'])
        print(d['url'])
        print()
