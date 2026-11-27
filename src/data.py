"""Phần dùng chung cho nhiều notebook: đường dẫn, định nghĩa luật minh bạch lương,
bảng nhóm chức năng của tin và mã công ty.

Chỉ những gì được từ 2 notebook trở lên sử dụng mới đặt ở đây. Code chỉ dùng trong
một notebook (làm sạch dữ liệu ở notebook 01, hàm thống kê ở notebook 02) được viết
thẳng trong notebook đó.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

# Đường dẫn – notebook 01, 02, 03
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# ---------------------------------------------------------------------------
# Luật minh bạch lương theo bang (thời điểm dữ liệu: 04/2024; nguồn: README)
# notebook 01 tạo cột `transparency_state`; notebook 02 dùng cho câu Q1
# ---------------------------------------------------------------------------
# Bang BẮT BUỘC ghi khoảng lương trong tin tuyển dụng, kèm ngày luật có hiệu lực
TRANSPARENCY_STATES = {
    "CO": "2021-01-01",
    "CA": "2023-01-01",
    "WA": "2023-01-01",
    "NY": "2023-09-17",   # NYC áp dụng từ 2022-11-01, toàn bang từ 2023-09-17
    "HI": "2024-01-01",   # chỉ áp dụng cho công ty ≥ 50 nhân viên
}
# Bang chỉ yêu cầu cung cấp lương KHI ỨNG VIÊN HỎI (không bắt buộc ghi trong tin)
ON_REQUEST_STATES = {"CT", "NV", "RI", "MD"}
# Bang có luật nhưng hiệu lực SAU thời điểm thu thập (DC 30/06/2024; IL, MN 01/01/2025) → dùng cho robustness
LATE_STATES = {"DC", "IL", "MN"}


# ---------------------------------------------------------------------------
# Hàm dùng chung
# ---------------------------------------------------------------------------
def load_job_functions(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """Nhóm chức năng của từng tin, dạng dài: (job_id, skill_abr, skill_name, rank).

    Một tin có 1–3 nhóm; rank 0 là nhóm đầu tiên ("chức năng chính").
    Dùng ở notebook 01 (ghép bảng), 02 (câu Q3) và 03 (đặc trưng cho mô hình).
    """
    js = pd.read_csv(raw_dir / "jobs" / "job_skills.csv")
    sk = pd.read_csv(raw_dir / "mappings" / "skills.csv")
    js = js.merge(sk, on="skill_abr", how="left", validate="m:1")
    js["rank"] = js.groupby("job_id").cumcount()
    return js


def cluster_id(df: pd.DataFrame) -> pd.Series:
    """Mã công ty của mỗi tin: company_id, nếu thiếu thì dùng tên công ty.

    Dùng ở notebook 02 (so sánh trong cùng công ty) và 03 (chia train/test theo công ty).
    """
    cid = df["company_id"].astype("Int64").astype(str)
    return cid.where(df["company_id"].notna(), "name:" + df["company_name"].fillna("unknown"))
