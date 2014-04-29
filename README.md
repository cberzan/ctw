Final project for UC Berkeley CS281B, Statistical Learning Theory, spring 2014,
by Constantin Berzan and Eric Tzeng. The driving question was: Why did the
authors of CTW use [the concept of
phases][http://www.ele.tue.nl/ctw/overview/structure.html] to organize their
trees?

Note: The CTW algorithm is unfortunately [patent
encumbered][http://www.ele.tue.nl/ctw/ipr.html].


## Setup

Install pypy: http://doc.pypy.org/en/latest/getting-started.html

Create virtualenv:
```
mkvirtualenv -p /home/cberzan/install/pypy-2.2.1-linux64/bin/pypy ctw-pypy
```

Install pypy's numpy fork:
```
pip install git+https://bitbucket.org/pypy/numpy.git
```

## Running tests

```
nosetests
```
