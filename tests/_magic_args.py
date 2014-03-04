#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-03-04
#

"""
"""

from __future__ import print_function, unicode_literals


from workflow import Workflow


def main(wf):
    args = wf.args
    wf.logger.debug('cachedir : %s', wf.cachedir)
    wf.logger.debug('datadir : %s', wf.datadir)


if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)
