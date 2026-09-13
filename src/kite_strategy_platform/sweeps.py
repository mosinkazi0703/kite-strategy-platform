import itertools
def parameter_sweep(base, matrix, runner):
    keys=list(matrix); results=[]
    for values in itertools.product(*(matrix[k] for k in keys)):
        config={**base, **dict(zip(keys,values))}; results.append({"parameters":config,"metrics":runner(config)})
    return results
