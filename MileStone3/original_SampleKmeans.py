
from __future__ import print_function

import sys

import numpy as np
from pyspark import SparkContext


def parseVector(line):
    return np.array([float(x) for x in line.split(' ')])


def closestPoint(p, centers):
    bestIndex = 0
    closest = float("+inf")
    for i in range(len(centers)):
        tempDist = np.sum((p - centers[i]) ** 2)
        if tempDist < closest:
            closest = tempDist
            bestIndex = i
    return bestIndex


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage: kmeans <file> <k> <convergeDist>", file=sys.stderr)
        exit(-1)

    print("""WARN: This is a naive implementation of KMeans Clustering and is given
       as an example! Please refer to examples/src/main/python/mllib/kmeans.py for an example on
       how to use MLlib's KMeans implementation.""", file=sys.stderr)

    sc = SparkContext(appName="PythonKMeans")
    lines = sc.textFile(sys.argv[1])
    data = lines.map(parseVector).cache()
    K = int(sys.argv[2])
    convergeDist = float(sys.argv[3])

    kPoints = data.takeSample(False, K, 1)
    tempDist = 1.0

    while tempDist > convergeDist:
        closest = data.map(
            lambda p: (closestPoint(p, kPoints), (p, 1)))
        pointStats = closest.reduceByKey(
            lambda p1_c1, p2_c2: (p1_c1[0] + p2_c2[0], p1_c1[1] + p2_c2[1]))
        newPoints = pointStats.map(
            lambda st: (st[0], st[1][0] / st[1][1])).collect()

        tempDist = sum(np.sum((kPoints[iK] - p) ** 2) for (iK, p) in newPoints)

        for (iK, p) in newPoints:
            kPoints[iK] = p

    print("Final centers: " + str(kPoints))

    sc.stop()
