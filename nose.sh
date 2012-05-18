#!/usr/bin/bash

nosetests --with-gae --exclude="mapreduce|gdata|atom|httplib2" $1 $2 $3 $4 $5

# needed to change nose/case.py's MethodTestCase.__init__ as follows.
# Otherwise the attempt to create cls() without a parameter fails due to runTest missing
#        if self.test is None:
#            method_name = self.method.__name__
#            self.inst = self.cls(method_name)
#            self.test = getattr(self.inst, method_name)
#        else:
#            self.inst = self.cls()

