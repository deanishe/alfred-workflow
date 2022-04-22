#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-07-9
#

"""
"""




import sys

from workflow import Workflow

log = None


def main(wf):
    """Do nothing."""
    log.debug('datadir=%r', wf.datadir)


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
