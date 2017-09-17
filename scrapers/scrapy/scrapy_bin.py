#!/usr/local/opt/python/bin/python2.7

# -*- coding: utf-8 -*-
import re
import site
import sys

site.addsitedir('lib-local')
site.addsitedir('lib-both')

from scrapy.cmdline import execute

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(execute())