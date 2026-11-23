"""Các hàm thống kê dùng chung: bootstrap CI (thường và theo cụm), effect size."""
from __future__ import annotations

import numpy as np
import pandas as pd


def bootstrap_ci(x, stat=np.median, n_boot: int = 2000, alpha: float = 0.05, seed: int = 42):
    """Percentile bootstrap CI cho một thống kê của một mẫu."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    boots = np.apply_along_axis(stat, 1, x[idx])
    return stat(x), np.quantile(boots, alpha / 2), np.quantile(boots, 1 - alpha / 2)


def cluster_bootstrap(df: pd.DataFrame, cluster: str, func, n_boot: int = 1000,
                      alpha: float = 0.05, seed: int = 42):
    """Bootstrap theo cụm: rút lại cả CỤM (vd: công ty) có hoàn lại.

    Dùng khi nhiều dòng thuộc cùng một thực thể (một công ty đăng hàng trăm tin
    giống nhau) – bootstrap từng dòng sẽ cho CI hẹp một cách sai lệch.
    `func(df) -> float` tính thống kê trên một DataFrame.
    """
    rng = np.random.default_rng(seed)
    groups = {k: v.index.to_numpy() for k, v in df.groupby(cluster, observed=True)}
    keys = np.array(list(groups.keys()), dtype=object)
    est = func(df)
    boots = []
    for _ in range(n_boot):
        pick = rng.choice(len(keys), size=len(keys), replace=True)
        idx = np.concatenate([groups[keys[i]] for i in pick])
        boots.append(func(df.loc[idx]))
    boots = np.asarray(boots)
    return est, np.nanquantile(boots, alpha / 2), np.nanquantile(boots, 1 - alpha / 2)


def cohens_h(p1: float, p2: float) -> float:
    """Effect size cho chênh lệch hai tỉ lệ (0.2 nhỏ, 0.5 vừa, 0.8 lớn)."""
    return 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))


def fmt_ci(est, lo, hi, pct: bool = False, money: bool = False, digits: int = 1) -> str:
    if pct:
        return f"{est*100:.{digits}f}% (95% CI {lo*100:.{digits}f}–{hi*100:.{digits}f}%)"
    if money:
        return f"${est:,.0f} (95% CI ${lo:,.0f}–${hi:,.0f})"
    return f"{est:.{digits}f} (95% CI {lo:.{digits}f}–{hi:.{digits}f})"


# ---------------------------------------------------------------------------
# Bootstrap theo cụm, dạng vector hoá (nhanh hơn rất nhiều so với vòng lặp pandas)
# ---------------------------------------------------------------------------
def cluster_weights(cluster: pd.Series, n_boot: int = 1000, seed: int = 42):
    """Ma trận trọng số bootstrap theo cụm.

    Mỗi lần bootstrap rút lại K cụm có hoàn lại; một cụm được rút m lần thì mọi
    dòng của nó có trọng số m. Trả về (W_rows: n_boot × n_rows, codes).
    """
    codes, uniq = pd.factorize(cluster)
    rng = np.random.default_rng(seed)
    k = len(uniq)
    Wc = rng.multinomial(k, np.full(k, 1 / k), size=n_boot).astype(np.float32)  # n_boot × K
    return Wc, codes


def boot_rate_by_group(y: np.ndarray, group: np.ndarray, cluster: pd.Series,
                       n_boot: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Tỉ lệ (mean của biến 0/1 hoặc tỉ số) theo nhóm, CI bootstrap theo cụm."""
    Wc, codes = cluster_weights(cluster, n_boot, seed)
    k = Wc.shape[1]
    res = {}
    for g in pd.unique(group):
        m = group == g
        num = np.bincount(codes[m], weights=y[m], minlength=k)
        den = np.bincount(codes[m], minlength=k).astype(float)
        boots = (Wc @ num) / (Wc @ den)
        res[g] = (num.sum() / den.sum(), *np.nanquantile(boots, [0.025, 0.975]), int(m.sum()))
    return pd.DataFrame(res, index=["est", "lo", "hi", "n"]).T


def boot_rate_diff(y, group, a, b, cluster, n_boot=1000, seed=42):
    """Chênh lệch tỉ lệ nhóm a − nhóm b, CI bootstrap theo cụm."""
    Wc, codes = cluster_weights(cluster, n_boot, seed)
    k = Wc.shape[1]
    out = []
    for g in (a, b):
        m = group == g
        num = np.bincount(codes[m], weights=y[m], minlength=k)
        den = np.bincount(codes[m], minlength=k).astype(float)
        out.append(((Wc @ num) / (Wc @ den), num.sum() / den.sum()))
    boots = out[0][0] - out[1][0]
    return out[0][1] - out[1][1], *np.nanquantile(boots, [0.025, 0.975])


def weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    order = np.argsort(values)
    v, w = values[order], weights[order]
    cw = np.cumsum(w)
    return v[np.searchsorted(cw, 0.5 * cw[-1])]


def boot_median_cluster(values, cluster, n_boot=500, seed=42):
    """Median với CI bootstrap theo cụm (dùng median có trọng số)."""
    values = np.asarray(values, dtype=float)
    Wc, codes = cluster_weights(pd.Series(cluster), n_boot, seed)
    order = np.argsort(values)
    v, c = values[order], codes[order]
    boots = []
    for wc in Wc:
        w = wc[c]
        cw = np.cumsum(w)
        boots.append(v[np.searchsorted(cw, 0.5 * cw[-1])])
    return np.median(values), *np.quantile(boots, [0.025, 0.975])


def boot_median_ratio(v1, c1, v2, c2, n_boot=500, seed=42):
    """Tỉ số median(v1)/median(v2) – hai nhóm có thể chung cụm (cùng công ty).

    Dùng CHUNG một bộ trọng số cụm cho cả hai nhóm để giữ tương quan giữa chúng.
    """
    v1, v2 = np.asarray(v1, float), np.asarray(v2, float)
    allc = pd.Series(np.concatenate([np.asarray(c1, object), np.asarray(c2, object)]))
    Wc, codes = cluster_weights(allc, n_boot, seed)
    k1 = codes[:len(v1)]; k2 = codes[len(v1):]
    o1, o2 = np.argsort(v1), np.argsort(v2)
    s1, s2, k1, k2 = v1[o1], v2[o2], k1[o1], k2[o2]
    boots = []
    for wc in Wc:
        w1, w2 = wc[k1], wc[k2]
        if w1.sum() == 0 or w2.sum() == 0:
            continue
        cw1, cw2 = np.cumsum(w1), np.cumsum(w2)
        m1 = s1[np.searchsorted(cw1, 0.5 * cw1[-1])]
        m2 = s2[np.searchsorted(cw2, 0.5 * cw2[-1])]
        boots.append(m1 / m2)
    return np.median(v1) / np.median(v2), *np.quantile(boots, [0.025, 0.975])


# ---------------------------------------------------------------------------
# Hồi quy OLS với sai số chuẩn cluster-robust (CR1)
# ---------------------------------------------------------------------------
def ols_cluster(X: pd.DataFrame, y, cluster) -> pd.DataFrame:
    """OLS + sai số chuẩn theo cụm (cluster-robust, hiệu chỉnh mẫu nhỏ CR1).

    Dùng khi các dòng trong cùng một công ty không độc lập với nhau.
    X nên đã có cột 'const'. Trả về bảng coef, se, lo, hi (95%).
    """
    Xv = X.to_numpy(dtype=float)
    yv = np.asarray(y, dtype=float)
    n, p = Xv.shape
    XtX_inv = np.linalg.pinv(Xv.T @ Xv)
    beta = XtX_inv @ (Xv.T @ yv)
    u = yv - Xv @ beta
    codes, uniq = pd.factorize(pd.Series(cluster))
    G = len(uniq)
    S = np.zeros((G, p))
    np.add.at(S, codes, Xv * u[:, None])
    meat = S.T @ S
    corr = G / (G - 1) * (n - 1) / (n - p)
    V = corr * XtX_inv @ meat @ XtX_inv
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    out = pd.DataFrame({"coef": beta, "se": se}, index=X.columns)
    out["lo"] = out["coef"] - 1.96 * out["se"]
    out["hi"] = out["coef"] + 1.96 * out["se"]
    return out


def design_matrix(df: pd.DataFrame, focus: list, controls: list, ref: dict | None = None) -> pd.DataFrame:
    """Ma trận thiết kế: các biến quan tâm + dummy của biến kiểm soát (bỏ nhóm tham chiếu)."""
    ref = ref or {}
    parts = [pd.Series(1.0, index=df.index, name="const")]
    for col in focus + controls:
        s = df[col]
        if s.dtype.kind in "biuf" and col not in ref:
            parts.append(s.astype(float).rename(col))
        else:
            s = s.astype(str)
            base = ref.get(col, s.value_counts().index[0])
            d = pd.get_dummies(s, prefix=col, prefix_sep="=", dtype=float)
            parts.append(d.drop(columns=f"{col}={base}"))
    return pd.concat(parts, axis=1)
