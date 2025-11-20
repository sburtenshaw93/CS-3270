import statistics as _stats

def mean(values):
    return _stats.mean(values)

def median(values):
    return _stats.median(values)

def mode(values):
    return _stats.mode(values) 

def data_range(values): 
    return max(values) - min(values)

# ---------------New----------------------------
def describe(values):
    # Added to describe to make it a one stop summary
    vals = list(values)
    if not vals:
        return {'mean': None, 'median': None, 'mode': None, 'data_range': None, 'count': 0}
    return {
        'mean': mean(vals),
        'median': median(vals),
        'mode': mode(vals),
        'data_range': data_range(vals),
        'count': len(vals),
    }
