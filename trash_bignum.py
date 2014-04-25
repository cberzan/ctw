# Investigating whether 64-bit ints are slower than smaller ints.

import timeit


print "1 <<  13:", timeit.timeit(
    stmt='a & mask',
    setup='a = (1 << 13) - 1; mask = 1 << 7',
    number=10000000)

print "1 <<  38:", timeit.timeit(
    stmt='a & mask',
    setup='a = (1 << 38) - 1; mask = 1 << 27',
    number=10000000)

print "1 <<  62:", timeit.timeit(
    stmt='a & mask',
    setup='a = (1 << 62) - 1; mask = 1 << 60',
    number=10000000)

print "1 <<  63:", timeit.timeit(
    stmt='a & mask',
    setup='a = (1 << 63) - 1; mask = 1 << 60',
    number=10000000)

print "1 <<  64:", timeit.timeit(
    stmt='a & mask',
    setup='a = (1 << 64) - 1; mask = 1 << 60',
    number=10000000)

print "1 <<  78:", timeit.timeit(
    stmt='a & mask',
    setup='a = (1 << 78) - 1; mask = 1 << 70',
    number=10000000)

print "1 << 120:", timeit.timeit(
    stmt='a & mask',
    setup='a = (1 << 120) - 1; mask = 1 << 110',
    number=10000000)
