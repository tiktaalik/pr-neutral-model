import numpy
from random import shuffle



def old_generate(weights, sum):
    rnd = random() * sum
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

def generate(n, probs):
    samples = numpy.random.multinomial(n, probs)
    instances = []
    for i, num_instances in enumerate(samples):
        for n in range(num_instances):
            instances.append(i)
    shuffle(instances)
    return instances