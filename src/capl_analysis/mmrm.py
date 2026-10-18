"""REML MMRM + CR2/Satterthwaite; numerical engine used in the study.

No student records or absolute paths are included.
Class enters the sandwich covariance; it is not a random intercept.
The 3x3 within-student covariance is separate in GE and GK.
"""
import numpy as np
from scipy import stats,optimize,linalg
def design(group, time, school, schools):
    x = np.zeros(6 + len(schools) - 1)
    x[(0 if group == 'GK' else 3) + time - 1] = 1
    for i, s in enumerate(schools[1:]):
        x[6 + i] = float(school == s)
    return x

def cr2(X, y, beta, B, clusters):
    residual = y - X @ beta
    meat = np.zeros_like(B)
    cache = []
    for cl in np.unique(clusters):
        ix = np.flatnonzero(clusters == cl)
        xc = X[ix]
        ec = residual[ix]
        H = xc @ B @ xc.T
        ev, Q = np.linalg.eigh(np.eye(len(ix)) - H)
        assert min(ev) > 1e-08, (cl, min(ev))
        A = Q * (1 / np.sqrt(ev)) @ Q.T
        score = xc.T @ (A @ ec)
        meat += np.outer(score, score)
        cache.append((ix, xc, A))
    cov = B @ meat @ B
    return (cov, cache)

def inference(c, beta, cov, B, X, cache):
    estimate = float(c @ beta)
    se = float(np.sqrt(c @ cov @ c))
    vectors = []
    for ix, xc, A in cache:
        u = A @ xc @ B @ c
        vec = -X @ B @ xc.T @ u
        vec[ix] += u
        vectors.append(vec)
    G = np.array(vectors) @ np.array(vectors).T
    dof = float(np.trace(G) ** 2 / np.sum(G * G))
    crit = stats.t.ppf(0.975, dof)
    return {'estimate': estimate, 'se': se, 'df': dof, 't': estimate / se, 'p': float(2 * stats.t.sf(abs(estimate / se), dof)), 'lo': estimate - crit * se, 'hi': estimate + crit * se}

def fit(data, v, complete=False):
    data = data[data.group.isin(['GE', 'GK'])].copy()
    cols = [f'{v}_{t}' for t in (1, 2, 3)]
    if complete:
        data = data[data[cols].notna().all(axis=1)].copy()
    data = data[data[cols].notna().any(axis=1)].copy()
    schools = sorted(data.school.unique())
    p = 6 + len(schools) - 1
    patterns = {}
    ids = []
    for _, row in data.iterrows():
        ts = tuple((t for t in (1, 2, 3) if np.isfinite(getattr(row, f'{v}_{t}'))))
        if not ts:
            continue
        key = (row.group, ts)
        patterns.setdefault(key, []).append((np.array([design(row.group, t, row.school, schools) for t in ts]), np.array([getattr(row, f'{v}_{t}') for t in ts]), row.id, row['class']))
        ids.append(row.id)
    all_y = np.concatenate([a[1] for z in patterns.values() for a in z])
    center = all_y.mean()
    scale = all_y.std(ddof=1)
    stacks = {k: (np.stack([a[0] for a in z]), (np.stack([a[1] for a in z]) - center) / scale, z) for k, z in patterns.items()}
    N = len(all_y)

    def unpack(theta):
        covs = {}
        for group, off in [('GK', 0), ('GE', 6)]:
            th = theta[off:off + 6]
            L = np.array([[np.exp(th[0]), 0, 0], [th[1], np.exp(th[2]), 0], [th[3], th[4], np.exp(th[5])]])
            covs[group] = L @ L.T
        return covs

    def profile(theta, details=False):
        covs = unpack(theta)
        A = np.zeros((p, p))
        b = np.zeros(p)
        yy = 0.0
        logdet = 0.0
        for (group, ts), (Xs, Ys, z) in stacks.items():
            indexes = np.array(ts) - 1
            V = covs[group][np.ix_(indexes, indexes)]
            W = np.linalg.inv(V)
            A += np.einsum('nip,ij,njq->pq', Xs, W, Xs)
            b += np.einsum('nip,ij,nj->p', Xs, W, Ys)
            yy += np.einsum('ni,ij,nj->', Ys, W, Ys)
            logdet += len(z) * np.linalg.slogdet(V)[1]
        beta = np.linalg.solve(A, b)
        rss = yy - b @ beta
        objective = 0.5 * (logdet + np.linalg.slogdet(A)[1] + rss + (N - p) * np.log(2 * np.pi))
        return (objective, covs, beta, A) if details else objective
    starts = []
    for corr in [0.1, 0.6]:
        R = np.full((3, 3), corr)
        np.fill_diagonal(R, 1)
        L = np.linalg.cholesky(R)
        th = [np.log(L[0, 0]), L[1, 0], np.log(L[1, 1]), L[2, 0], L[2, 1], np.log(L[2, 2])]
        starts.append(np.tile(th, 2))
    solutions = [optimize.minimize(profile, x, method='L-BFGS-B', bounds=[(-5, 3), (-4, 4), (-5, 3), (-4, 4), (-4, 4), (-5, 3)] * 2, options={'maxiter': 1000, 'ftol': 1e-11, 'gtol': 2e-05}) for x in starts]
    solution = min(solutions, key=lambda r: r.fun)
    objective, covs, bs, A = profile(solution.x, True)
    assert solution.success, solution.message
    assert abs(solutions[0].fun - solutions[1].fun) < 0.005, (v, [s.fun for s in solutions])
    beta = bs * scale
    beta[:6] += center
    X = []
    Y = []
    CL = []
    res = []
    for (group, ts), (Xs, Ys, z) in stacks.items():
        ix = np.array(ts) - 1
        V = covs[group][np.ix_(ix, ix)] * scale ** 2
        L = np.linalg.cholesky(V)
        for xx, (_, yy, ident, cl) in zip(Xs, z):
            X.append(linalg.solve_triangular(L, xx, lower=True))
            Y.append(linalg.solve_triangular(L, yy, lower=True))
            CL.extend([cl] * len(ts))
    X = np.vstack(X)
    Y = np.concatenate(Y)
    CL = np.array(CL)
    B = np.linalg.inv(X.T @ X)
    assert np.max(np.abs(np.linalg.solve(X.T @ X, X.T @ Y) - beta)) < 1e-07
    cov, cache = cr2(X, Y, beta, B, CL)
    contrasts = {}

    def contrast(parts):
        c = np.zeros(p)
        for g, t, w in parts:
            c[(0 if g == 'GK' else 3) + t - 1] += w
        return c
    cs = {'immediate': contrast([('GE', 2, 1), ('GE', 1, -1), ('GK', 2, -1), ('GK', 1, 1)]), 'lasting': contrast([('GE', 3, 1), ('GE', 1, -1), ('GK', 3, -1), ('GK', 1, 1)]), 'erosion': contrast([('GE', 3, 1), ('GE', 2, -1), ('GK', 3, -1), ('GK', 2, 1)]), 'GE_pre_post': contrast([('GE', 2, 1), ('GE', 1, -1)]), 'GE_pre_year': contrast([('GE', 3, 1), ('GE', 1, -1)]), 'GE_post_year': contrast([('GE', 3, 1), ('GE', 2, -1)]), 'GK_post_year': contrast([('GK',3,1),('GK',2,-1)])}
    baseline = data[data[f'{v}_1'].notna()]
    groups = [baseline.loc[baseline.group == g, f'{v}_1'].values for g in ['GE', 'GK']]
    pooled = np.sqrt(sum(((len(a) - 1) * np.var(a, ddof=1) for a in groups)) / (sum((len(a) for a in groups)) - 2))
    for name, c in cs.items():
        contrasts[name] = inference(c, beta, cov, B, X, cache)
        contrasts[name]['standardized'] = contrasts[name]['estimate'] / pooled
    assert abs(contrasts['lasting']['estimate'] - contrasts['immediate']['estimate'] - contrasts['erosion']['estimate']) < 1e-10
    residual = Y - X @ beta
    leave = []
    for cl in np.unique(CL):
        keep = CL != cl
        bk = np.linalg.lstsq(X[keep], Y[keep], rcond=None)[0]
        leave.append(float(cs['lasting'] @ bk))
    normal = stats.shapiro(residual)
    levene = []
    for t in (1, 2, 3):
        a = data.loc[data.group == 'GE', f'{v}_{t}'].dropna()
        b = data.loc[data.group == 'GK', f'{v}_{t}'].dropna()
        z = stats.levene(a, b, center='median')
        levene.append({'time': t, 'W': float(z.statistic), 'p': float(z.pvalue), 'variance_ratio': float(np.var(a, ddof=1) / np.var(b, ddof=1))})
    correlations = {g: (covs[g] / np.sqrt(np.outer(np.diag(covs[g]), np.diag(covs[g])))).tolist() for g in ['GE', 'GK']}
    result = {'n_students': len(data), 'n_obs': N, 'n_classes': len(set(CL)), 'n_schools': len(schools), 'group_n': data.group.value_counts().to_dict(), 'complete_by_group': data[data[cols].notna().all(axis=1)].group.value_counts().to_dict(), 'contrasts': contrasts, 'residual_shapiro': {'W': float(normal.statistic), 'p': float(normal.pvalue)}, 'levene': levene, 'residual_outliers_gt3': int(sum(abs(residual) > 3)), 'leave_class_out_lasting_min': min(leave), 'leave_class_out_lasting_max': max(leave), 'covariance': {g: (covs[g] * scale ** 2).tolist() for g in covs}, 'correlations': correlations, 'optimizer': {'success': bool(solution.success), 'message': str(solution.message), 'objective': float(objective), 'gradient_max': float(max(abs(solution.jac))), 'restart_difference': float(abs(solutions[0].fun - solutions[1].fun))}, 'baseline_pooled_sd': float(pooled)}
    means = {}
    for group in ['GE','GK']:
        means[group] = []
        weights = data.school.value_counts(normalize=True).to_dict()
        for t in [1,2,3]:
            c = sum(weight * design(group,t,school,schools) for school,weight in weights.items())
            means[group].append(inference(c,beta,cov,B,X,cache))
    result['means'] = means
    return (result, residual)

def holm(ps):
    order = np.argsort(ps)
    adjusted = np.empty(len(ps))
    previous = 0.0
    for rank, i in enumerate(order):
        previous = max(previous, min(1.0, (len(ps) - rank) * ps[i]))
        adjusted[i] = previous
    return adjusted.tolist()