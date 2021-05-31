# Norerun

Iterate on Python scripts without rerunning from the beginning.

# Disclaimer

This is a toy project meant only to experiment with this idea and start some
discussion.  This is not yet intended for serious workflows.  It has severe
limitations.

## What Problem Does This Solve?

Norerun is intended to solve the problem of iterating on long running scripts without
have to rerun the long steps.  For example if a script must first load a large amount
of data to run, it would be nice to only have to run that part once and then iterate
on top of it.

## Example Usage:

Let's look at some toy code of a function which loads some data, but requires
a long time.

```python
import time

def load_1():
    time.sleep(10)
    return [1, 2, 3, 4, 5]
```

Lets say we want to do some experimental data analysis.

First we add some code to get the mean of the first data set.

```python
import time

def load_1():
    time.sleep(10)
    return [1, 2, 3, 4, 5]

def mean(data):
    time.sleep(2)
    reutrn sum(data) / len(data)

data_1 = load_1()
mean_1 = mean(data_1)
```
```
3.0
```

Now we want to add some code to get the variance.

```python
import time

def load_1():
    time.sleep(10)
    return [1, 2, 3, 4, 5]

def mean(data):
    time.sleep(2)
    reutrn sum(data) / len(data)

def variance(data, data_mean):
    return sum((d - data_mean)**2 for d in data) / len(data)

data_1 = load_1()
mean_1 = mean(data_1)
variance_1 = variance(data_1, mean_1)
```

The problem is that it took 15 seconds just to reload the data, 2 seconds just
to recompute the intermediate result.

This problem could be solved by running all of this code inside the Python
interpreter and running commands one after the other.  However in this case
there are three issues:
1. You do not have an easy view of the current version of the program.
2. You will not end up with a program that can easily be rerun.
3. If you change a function it is not immediately obvious what code need to be rerun, and
you may lose track of what code has been rerun.

Here is what this development would look like using Norerun:

![](examples/example.gif)

You can check out a real file developed while using Norerun in
`real_example.py`

## Why Not Just Use Notebooks?

Norerun is intended to avoid some bad features of notebooks which:
* Enforce that you work in a certain environment
* Have state dependent on the order that code was run
* Encourage bad habits and discourage good habits

But to obtain some nice features of notebooks which:
* allow for interactive and iterative development
* allow for caching of results which take a while to compute
* allow for logging every single command

## Limitations

The current implementation is very limited.

* It only supports a very simple subset of Python:
    * Defining functions
    * Assigning the return value of a function call to a variable
* It does not yet support modules.
* It will probably break if you look at it wrong.
