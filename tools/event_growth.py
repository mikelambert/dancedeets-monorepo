#!/usr/bin/python

import re

'cat local_data/DBEvent.csv | cut -f4 -d, | sort | cut -c1-6 | uniq -c | cut -b1-4'

a = """
  60
  65
 116
 195
 209
 225
 348
 333
 390
 419
 673
 675
 740
 669
1011
1173
1071
1113
1603
1781
"""

b = re.split(r'\s+', a.strip())

c = [int(x) for x in b]

# turn this on to get total growth curves
c = reduce(lambda x, y: x + [y+x[-1]], c[1:], c[:1])
#[57, 121, 226, 434, 660, 901, 1263, 1602, 2020, 2429, 3161, 3900]

d = [x*100/max(c) for x in c]

e = ','.join([str(x) for x in d])

'7,8,14,28,30,32,48,45,56,55,99,100'

f = "https://chart.googleapis.com/chart?cht=lc&chs=300x200&chd=t:%s&chxt=x,y&chxr=1,0,%s,%s&chxl=0:|Jul'10|Jan'10|Jul'11|Jan'11" % (e, max(c), int(max(c)/5))

print f

