"""Đọc, làm sạch và ghép các bảng của bộ dữ liệu LinkedIn Job Postings.

Mọi quyết định làm sạch được giải thích trong notebook 01; module này chỉ gom
code lại một chỗ để notebook 02 và 03 dùng lại đúng cùng một quy tắc.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# ---------------------------------------------------------------------------
# Hằng số
# ---------------------------------------------------------------------------
FULLTIME_HOURS = 2080                       # 40 giờ × 52 tuần (giống cách Kaggle quy đổi)
PAY_FACTORS = {"YEARLY": 1, "MONTHLY": 12, "BIWEEKLY": 26, "WEEKLY": 52, "HOURLY": FULLTIME_HOURS}
FED_MIN_WAGE = 7.25                          # lương tối thiểu liên bang Mỹ (USD/giờ)
SALARY_MIN = FED_MIN_WAGE * FULLTIME_HOURS   # 15,080 USD/năm
SALARY_MAX = 1_000_000

# Các bang BẮT BUỘC ghi khoảng lương trong tin tuyển dụng và luật đã có hiệu lực
# trước tháng 4/2024 (thời điểm thu thập dữ liệu). Nguồn: xem notebook 02, câu Q1.
TRANSPARENCY_STATES = {
    "CO": "2021-01-01",
    "CA": "2023-01-01",
    "WA": "2023-01-01",
    "NY": "2023-09-17",   # NYC áp dụng từ 2022-11-01, toàn bang từ 2023-09-17
    "HI": "2024-01-01",   # chỉ áp dụng cho công ty ≥ 50 nhân viên
}
# Các bang chỉ yêu cầu cung cấp lương KHI ỨNG VIÊN HỎI (không bắt buộc ghi trong tin)
ON_REQUEST_STATES = {"CT", "NV", "RI", "MD"}
# DC: luật bắt buộc ghi lương có hiệu lực 30/06/2024 → sau thời điểm thu thập, dùng cho robustness
LATE_STATES = {"DC", "IL", "MN"}

US_STATES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
    "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "Puerto Rico": "PR",
}
STATE_CODES = set(US_STATES.values())

# Vùng đô thị (metro area) không chứa tên bang → gán tay; vùng trải nhiều bang → None
METRO_TO_STATE = {
    "New York City Metropolitan Area": "NY", "San Francisco Bay Area": "CA",
    "Dallas-Fort Worth Metroplex": "TX", "Los Angeles Metropolitan Area": "CA",
    "Atlanta Metropolitan Area": "GA", "Greater Houston": "TX", "Greater Chicago Area": "IL",
    "Nashville Metropolitan Area": "TN", "Greater Boston": "MA", "Denver Metropolitan Area": "CO",
    "Greater Orlando": "FL", "Miami-Fort Lauderdale Area": "FL", "Greater Phoenix Area": "AZ",
    "Greater Minneapolis-St. Paul Area": "MN", "Raleigh-Durham-Chapel Hill Area": "NC",
    "Detroit Metropolitan Area": "MI", "Salt Lake City Metropolitan Area": "UT",
    "Greater Seattle Area": "WA", "San Diego Metropolitan Area": "CA",
    "Greater Philadelphia": "PA", "Greater Indianapolis": "IN", "Charlotte Metro": "NC",
    "Greater St. Louis": "MO", "Cincinnati Metropolitan Area": "OH",
    "Omaha Metropolitan Area": "NE", "Greater Tampa Bay Area": "FL", "Greater Sacramento": "CA",
    "Greater Pittsburgh Region": "PA", "Greater Cleveland": "OH", "Las Vegas Metropolitan Area": "NV",
    "Greater Milwaukee": "WI", "Greater Richmond Region": "VA", "Greater Hartford": "CT",
    "Greater Grand Rapids, Michigan Area": "MI", "Jacksonville Metropolitan Area": "FL",
    "Greater Memphis Area": "TN", "Greater Louisville": "KY", "Baltimore City County": "MD",
    # Vùng trải nhiều bang: không gán để tránh sai
    "Washington DC-Baltimore Area": None, "Kansas City Metropolitan Area": None,
}
_STATE_NAMES_LONGEST_FIRST = sorted(US_STATES, key=len, reverse=True)
_STATE_NAME_RE = re.compile(r"\b(" + "|".join(map(re.escape, _STATE_NAMES_LONGEST_FIRST)) + r")\b")

# Các cột bị loại ngay từ đầu (lý do: notebook 01, mục 3.2.1)
DROP_COLS = [
    "sponsored",          # hằng số = 0
    "compensation_type",  # chỉ có BASE_SALARY khi có lương → không thêm thông tin
    "work_type",          # trùng nghĩa với formatted_work_type
    "job_posting_url",    # định danh, suy ra từ job_id
    "application_url",    # URL, không dùng để phân tích
    "skills_desc",        # thiếu 98%
    "closed_time",        # thiếu 99%
    "zip_code", "fips",   # đã có bang từ cột location
]


# ---------------------------------------------------------------------------
# Hàm phụ
# ---------------------------------------------------------------------------
def report_rows(log: list, step: str, before: int, after: int) -> None:
    """Ghi lại số dòng trước/sau mỗi bước biến đổi."""
    log.append({"bước": step, "trước": before, "sau": after, "chênh lệch": after - before})


def parse_state(location: pd.Series) -> pd.Series:
    """Suy ra mã bang (2 chữ cái) từ cột location dạng tự do của LinkedIn.

    Thứ tự ưu tiên: ", XX" ở cuối → tên metro đã biết → tên bang đầy đủ.
    Tin chỉ ghi "United States" (tuyển toàn quốc) trả về NaN.
    """
    loc = location.fillna("").str.strip()
    code = loc.str.extract(r",\s*([A-Z]{2})$")[0]
    code = code.where(code.isin(STATE_CODES))

    metro = loc.map(lambda s: METRO_TO_STATE.get(s, "__none__"))
    is_metro = metro != "__none__"
    code = code.where(code.notna() | ~is_metro, metro.where(is_metro))

    need = code.isna() & ~is_metro
    by_name = loc[need].str.extract(_STATE_NAME_RE)[0].map(US_STATES)
    code.loc[need] = by_name
    return code


def repair_and_annualize_salary(df: pd.DataFrame, repair_units: bool = True,
                                lo: float = SALARY_MIN, hi: float = SALARY_MAX) -> pd.DataFrame:
    """Tính lương năm (USD) từ min/med/max_salary + pay_period, có sửa lỗi đơn vị.

    Trả về DataFrame với các cột: pay_period_fixed, salary_mid_raw, annual_salary,
    annual_min, annual_max, salary_status.
    """
    out = pd.DataFrame(index=df.index)
    mid = np.where(df["med_salary"].notna(), df["med_salary"],
                   (df["min_salary"] + df["max_salary"]) / 2)
    mid = pd.Series(mid, index=df.index)
    period = df["pay_period"].copy()

    status = pd.Series("not_disclosed", index=df.index, dtype=object)
    disclosed = df["pay_period"].notna()
    status[disclosed & (df["currency"] != "USD")] = "non_usd"

    if repair_units:
        to_hourly = (period == "YEARLY") & mid.between(10, 300, inclusive="left")
        to_yearly = (period == "HOURLY") & (mid >= 10_000)
        period = period.mask(to_hourly, "HOURLY").mask(to_yearly, "YEARLY")
        status[(to_hourly | to_yearly) & (status == "not_disclosed")] = "repaired"

    factor = period.map(PAY_FACTORS)
    annual = mid * factor
    usd = df["currency"] == "USD"
    ok = usd & annual.between(lo, hi)

    status[disclosed & usd & ~ok] = "out_of_range"
    status[disclosed & usd & ok & (status == "not_disclosed")] = "valid"

    out["pay_period_fixed"] = period
    out["salary_mid_raw"] = mid
    out["annual_salary"] = annual.where(ok)
    out["annual_min"] = (df["min_salary"] * factor).where(ok)
    out["annual_max"] = (df["max_salary"] * factor).where(ok)
    out["salary_status"] = status
    return out


# ---------------------------------------------------------------------------
# Đọc & làm sạch từng bảng
# ---------------------------------------------------------------------------
def load_postings_raw(raw_dir: Path = RAW_DIR, with_text: bool = False) -> pd.DataFrame:
    skip = set() if with_text else {"description", "skills_desc"}
    return pd.read_csv(raw_dir / "postings.csv", usecols=lambda c: c not in skip)


def clean_postings(raw: pd.DataFrame, log: list | None = None) -> pd.DataFrame:
    """Làm sạch bảng postings. Không xoá dòng nào – chỉ thêm/đổi cột.

    Các tin bị loại khỏi một phân tích cụ thể (vd: không có lương) được lọc ở
    từng câu hỏi để báo cáo số dòng rõ ràng tại chỗ.
    """
    log = [] if log is None else log
    n0 = len(raw)
    df = raw.drop(columns=[c for c in DROP_COLS if c in raw.columns]).copy()

    # Thời gian: epoch milliseconds → datetime
    for c in ["original_listed_time", "listed_time", "expiry"]:
        df[c] = pd.to_datetime(df[c], unit="ms")
    df["listed_date"] = df["listed_time"].dt.normalize()

    # Chuẩn hoá chuỗi
    df["title"] = df["title"].str.strip()
    df["company_name"] = df["company_name"].str.strip()

    # Biến phân loại
    df["remote_allowed"] = df["remote_allowed"].fillna(0).astype(int)
    df["experience_level"] = df["formatted_experience_level"].fillna("Unknown")
    df["work_type"] = df["formatted_work_type"]
    df = df.drop(columns=["formatted_experience_level", "formatted_work_type"])

    # Địa điểm
    df["state"] = parse_state(df["location"])
    df["is_nationwide"] = df["location"].eq("United States")
    df["transparency_state"] = df["state"].isin(TRANSPARENCY_STATES.keys())

    # Lương
    df["salary_disclosed"] = df["pay_period"].notna()
    df = df.join(repair_and_annualize_salary(df))

    # Ứng tuyển: applies không bao giờ = 0 trong dữ liệu → NaN thực chất là 0 lượt
    df["applies_filled"] = df["applies"].fillna(0)

    report_rows(log, "clean_postings (không xoá dòng)", n0, len(df))
    return df


def load_companies(raw_dir: Path = RAW_DIR, log: list | None = None) -> pd.DataFrame:
    """Bảng công ty 1 dòng/công ty: size bucket, số nhân viên mới nhất, ngành."""
    log = [] if log is None else log
    comp = pd.read_csv(raw_dir / "companies" / "companies.csv",
                       usecols=["company_id", "name", "company_size", "state", "country"])
    comp = comp.rename(columns={"name": "company_name_ref", "state": "hq_state", "country": "hq_country"})

    emp = pd.read_csv(raw_dir / "companies" / "employee_counts.csv")
    n_emp = len(emp)
    emp = (emp.sort_values("time_recorded").groupby("company_id", as_index=False).tail(1)
              .drop(columns="time_recorded"))
    report_rows(log, "employee_counts: giữ snapshot mới nhất / công ty", n_emp, len(emp))

    ind = pd.read_csv(raw_dir / "companies" / "company_industries.csv")
    ind = ind.rename(columns={"industry": "company_industry"})
    n_ind = len(ind)
    ind = ind.drop_duplicates("company_id", keep="first")   # 10 công ty có 2 ngành → giữ ngành đầu
    report_rows(log, "company_industries: 1 ngành / công ty", n_ind, len(ind))

    n_comp = len(comp)
    comp = (comp.merge(emp, on="company_id", how="left", validate="1:1")
                .merge(ind, on="company_id", how="left", validate="1:1"))
    report_rows(log, "companies ⨝ employee_counts ⨝ company_industries", n_comp, len(comp))
    return comp


def load_job_functions(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Dạng dài: (job_id, skill_abr, skill_name, rank) – rank 0 là nhóm đầu tiên."""
    js = pd.read_csv(raw_dir / "jobs" / "job_skills.csv")
    sk = pd.read_csv(raw_dir / "mappings" / "skills.csv")
    js = js.merge(sk, on="skill_abr", how="left", validate="m:1")
    js["rank"] = js.groupby("job_id").cumcount()
    return js


def load_job_industries(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    ji = pd.read_csv(raw_dir / "jobs" / "job_industries.csv")
    mp = pd.read_csv(raw_dir / "mappings" / "industries.csv")
    ji = ji.merge(mp, on="industry_id", how="left", validate="m:1")
    ji["rank"] = ji.groupby("job_id").cumcount()
    return ji


def employee_bucket(n: pd.Series) -> pd.Series:
    bins = [-np.inf, 49, 249, 999, 9_999, np.inf]
    labels = ["1–49", "50–249", "250–999", "1k–9.9k", "10k+"]
    return pd.cut(n, bins=bins, labels=labels)


def build_analytic_table(raw_dir: Path = RAW_DIR, log: list | None = None) -> pd.DataFrame:
    """postings đã làm sạch + thông tin công ty + nhóm chức năng/ngành chính."""
    log = [] if log is None else log
    df = clean_postings(load_postings_raw(raw_dir), log)

    comp = load_companies(raw_dir, log)
    n = len(df)
    df = df.merge(comp, on="company_id", how="left", validate="m:1")
    report_rows(log, "postings ⨝ companies (left, m:1)", n, len(df))

    jf = load_job_functions(raw_dir)
    prim_f = (jf[jf["rank"] == 0][["job_id", "skill_abr", "skill_name"]]
              .rename(columns={"skill_abr": "function_abr", "skill_name": "job_function"}))
    nfun = jf.groupby("job_id").size().rename("n_functions").reset_index()
    n = len(df)
    df = (df.merge(prim_f, on="job_id", how="left", validate="1:1")
            .merge(nfun, on="job_id", how="left", validate="1:1"))
    report_rows(log, "⨝ nhóm chức năng chính (job_skills)", n, len(df))

    ji = load_job_industries(raw_dir)
    prim_i = (ji[ji["rank"] == 0][["job_id", "industry_name"]]
              .rename(columns={"industry_name": "job_industry"}))
    n = len(df)
    df = df.merge(prim_i, on="job_id", how="left", validate="1:1")
    report_rows(log, "⨝ ngành chính của tin (job_industries)", n, len(df))

    df["employee_bucket"] = employee_bucket(df["employee_count"])
    df["job_function"] = df["job_function"].fillna("Unknown")
    df["job_industry"] = df["job_industry"].fillna("Unknown")
    return df


def cluster_id(df: pd.DataFrame) -> pd.Series:
    """Mã cụm = công ty (company_id; nếu thiếu thì dùng tên công ty)."""
    cid = df["company_id"].astype("Int64").astype(str)
    return cid.where(df["company_id"].notna(), "name:" + df["company_name"].fillna("unknown"))
