"""OLS with CR2 sandwich and contrast-specific Satterthwaite degrees of freedom."""
import numpy as np
from scipy import stats
def holm(ps):
    order = np.argsort(ps)
    out = np.empty(len(ps))
    prior = 0
    for rank, i in enumerate(order):
        prior = max(prior, min(1, (len(ps) - rank) * ps[i]))
        out[i] = prior
    return out.tolist()

def robust(X, y, clusters):
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    B = np.linalg.inv(X.T @ X)
    e = y - X @ beta
    meat = np.zeros_like(B)
    cache = []
    for cl in np.unique(clusters):
        ix = np.flatnonzero(clusters == cl)
        xc = X[ix]
        ec = e[ix]
        ev, Q = np.linalg.eigh(np.eye(len(ix)) - xc @ B @ xc.T)
        assert min(ev) > -1e-08
        inv = np.zeros_like(ev)
        inv[ev > 1e-09] = 1 / np.sqrt(ev[ev > 1e-09])
        A = Q * inv @ Q.T
        score = xc.T @ A @ ec
        meat += np.outer(score, score)
        cache.append((ix, xc, A))
    cov = B @ meat @ B
    inf = []
    for j in range(X.shape[1]):
        c = np.eye(X.shape[1])[j]
        vectors = []
        for ix, xc, A in cache:
            u = A @ xc @ B @ c
            v = -X @ B @ xc.T @ u
            v[ix] += u
            vectors.append(v)
        G = np.array(vectors) @ np.array(vectors).T
        dof = float(np.trace(G) ** 2 / np.sum(G * G))
        se = float(np.sqrt(c @ cov @ c))
        t = float(beta[j] / se)
        q = stats.t.ppf(0.975, dof)
        inf.append({'estimate': float(beta[j]), 'se': se, 'df': dof, 't': t, 'p': float(2 * stats.t.sf(abs(t), dof)), 'lo': float(beta[j] - q * se), 'hi': float(beta[j] + q * se)})
    return {'beta': beta, 'B': B, 'cov': cov, 'residual': e, 'inference': inf, 'X': X, 'y': y, 'clusters': clusters}

def demean(a, cl):
    a = np.asarray(a, float)
    out = a.copy()
    for c in np.unique(cl):
        out[cl == c] -= out[cl == c].mean(axis=0)
    return out
