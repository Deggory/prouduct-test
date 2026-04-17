import numpy as np

def compute_correlation(a, b):
    a, b = np.array(a), np.array(b)
    n = min(len(a), len(b))
    if n < 10:
        return 0
    a, b = a[:n], b[:n]
    if np.std(a) == 0 or np.std(b) == 0:
        return 0
    return np.corrcoef(a, b)[0,1]

def cross_correlation(a, b, max_lag=10):
    best = 0
    for lag in range(-max_lag, max_lag):
        if lag > 0:
            corr = compute_correlation(a[lag:], b[:-lag])
        elif lag < 0:
            corr = compute_correlation(a[:lag], b[-lag:])
        else:
            corr = compute_correlation(a, b)
        if abs(corr) > abs(best):
            best = corr
    return best

def smoothness_score(values):
    v = np.array(values)
    if len(v) < 2:
        return 0
    diffs = np.abs(np.diff(v))
    return np.mean(diffs) / (np.max(v) - np.min(v) + 1e-5)

def classify_signal(values):
    uniq = len(set(values))
    smooth = smoothness_score(values)

    if uniq <= 2:
        return "binary"
    if smooth < 0.01:
        return "very_smooth"
    if smooth < 0.05:
        return "smooth"
    if smooth < 0.2:
        return "moderate"
    return "noisy"
