from __future__ import print_function
import sys
import os

from pyspark import SparkContext
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.classification import LogisticRegressionWithSGD
from pyspark.mllib.linalg import _convert_to_vector
from numpy import *


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python runEyes.py <eyes location> <cfg file> <weight file> <SOCKET>")
        exit(-1)
    print (sys.argv[3])
    sc = SparkContext(appName="Eyes")
    cfgFile = sc.textFile(sys.argv[2])
    weightFile = sc.textFile(sys.argv[3])
    lineLengths = cfgFile.map(lambda s: len(s))
    totalLength = cfgFile.reduce(lambda a, b: a + b)

    cmdline = sys.argv[1]+' stream demo ' + sys.argv[2] + ' ' + sys.argv[3] +' '+ sys.argv[4]
    print("Implement [%s]" % (cmdline))
    #output = os.popen(cmdline).readlines()
    os.system(cmdline)
    
    #print (output)
    sc.stop()
