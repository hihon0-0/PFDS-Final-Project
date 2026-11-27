# Thị trường tuyển dụng Mỹ qua 124 nghìn tin LinkedIn (04/2024)

Đồ án cuối kỳ môn **CSC17104 – Lập trình cho Khoa học Dữ liệu**, Khoa Công nghệ Thông tin, Trường ĐH Khoa học Tự nhiên – ĐHQG-HCM.

## Thành viên và phân công

| Thành viên | MSSV | Câu hỏi phụ trách | Phần việc chung |
|---|---|---|---|
| Đinh Võ Thủy Tiên | 24120148 | Q1, Q2 | Thu thập & EDA ban đầu (Notebook 01) |
| Huỳnh Huy Hoàng | 24120181 | Q3, Q4 | Kỹ nghệ dữ liệu: làm sạch & ghép bảng (nay nằm trong notebook 01), `src/data.py`, `src/viz.py` |
| Hoàng Hùng Quân | 23120338 | Q5, Q6 (ML) | Pipeline Học máy (Notebook 03), các hàm thống kê (nay nằm trong notebook 02) |

> Phần việc chung (thu thập dữ liệu, `src/`, notebook 01, README, slides…) cần ghi đúng người làm – giảng viên đối chiếu với lịch sử Git.

## Bộ dữ liệu

- **Tên:** LinkedIn Job Postings (2023 – 2024) – *A Snapshot Into the Current Job Market*
- **Nguồn:** Kaggle – <https://www.kaggle.com/datasets/arshkon/linkedin-job-postings>, tác giả tài khoản `arshkon`. Dữ liệu được cào bằng bộ cào mã nguồn mở <https://github.com/ArshKA/LinkedIn-Job-Scraper>; tài khoản `@zoeyyuzou` cào thêm ~100,000 tin. Phiên bản nhóm dùng có các file đề ngày 19/08/2024.
- **Giấy phép:** **CC BY-SA 4.0** (Creative Commons Attribution-ShareAlike 4.0) – ghi công tác giả Arsh Koneru (`arshkon`). Dữ liệu cào từ LinkedIn nên chỉ dùng cho mục đích học tập; dữ liệu gốc **không** được commit vào repo.
- **Nội dung:** 123,849 tin tuyển dụng ở Mỹ (31 cột) với tiêu đề, công ty, địa điểm, cấp bậc, loại hợp đồng, lương (29% tin có), lượt xem/ứng tuyển. Kèm 10 bảng phụ: công ty (quy mô, ngành, số nhân viên theo thời gian), nhóm chức năng, ngành, phúc lợi, lương. Gần như toàn bộ tin được đăng trong 05–20/04/2024.
- **Hiểu dữ liệu qua ví dụ thật:** [data/HIEU_DU_LIEU.md](data/HIEU_DU_LIEU.md). **Tra cứu từng file, từng cột:** [data/README.md](data/README.md).

### Các phân tích công khai đã có và điểm khác biệt
Các phân tích công khai trên cùng dataset mà nhóm tìm thấy: 2 notebook nhiều vote nhất ở tab **Code** của trang Kaggle (tra ngày 26/11/2026, tab có 69 notebook) và một số repo/trang khác:

| Phân tích | Nội dung chính |
|---|---|
| [Decoding the Job Market: An In-depth Exploration](https://www.kaggle.com/code/pratul007/decoding-the-job-market-an-in-depth-exploration) – Kaggle, pratul007 (93 vote) | EDA mô tả rộng: ghép các bảng theo `job_id`/`company_id`, điền giá trị thiếu bằng "Not Specified" hoặc 0; đếm tin theo loại việc, công ty, bang, phúc lợi; lương theo chức danh, cấp bậc, ngành; tương quan views–applies; TF-IDF + KMeans trên mô tả |
| [LinkedIn Job Postings 2023 Data Analysis](https://www.kaggle.com/code/enricofindley/linkedin-job-postings-2023-data-analysis) – Kaggle, enricofindley (84 vote) | Ghép và làm sạch các bảng (gộp `benefits`, `job_skills` theo `job_id`, ghép bảng công ty); EDA cơ bản: word cloud tiêu đề, phân bố quy mô công ty, loại việc, tin được tài trợ |
| [GunashreeC/Job-Recommendation-System](https://github.com/GunashreeC/Job-Recommendation-System) | Hệ thống gợi ý việc làm, NLP trên mô tả, SHAP |
| [sherinrose2019k-ops/LinkedIn-Job-Postings-Analysis](https://github.com/sherinrose2019k-ops/LinkedIn-Job-Postings-Analysis) | EDA: kỹ năng phổ biến, vai trò dữ liệu, xu hướng remote, word cloud |
| [AndhikaWB/linkedin-job-postings-analysis](https://github.com/AndhikaWB/linkedin-job-postings-analysis) | Dashboard Spark/Streamlit: số tin và lương tháng theo bang |
| [aimdata-labs: LinkedIn postings](https://aimdata-labs.github.io/linkedin_postings) | Lương theo ngành và nhóm công việc |

**Điểm khác biệt của nhóm:** các phân tích trên chủ yếu *mô tả* (đếm, trung bình theo nhóm). Câu hỏi của nhóm tập trung vào việc **tách hiệu ứng khỏi confounder**: so sánh trong cùng công ty (Q1, Q2), so sánh công việc tương đương bằng cách chia nhóm con (Q2, Q4 – phát hiện nghịch lý Simpson), định lượng bất định bằng bootstrap và kiểm định thống kê, và kiểm tra độ vững với các quy tắc làm sạch khác nhau. Nhóm cũng tự xây dựng quy tắc **sửa lỗi đơn vị lương** thay vì dùng thẳng `normalized_salary` (cột này có giá trị tới 535 triệu USD/năm). Mô hình Q6 được thiết kế **chống rò rỉ dữ liệu** (không dùng mô tả, chia theo công ty). Nhóm không tái sử dụng code của các phân tích trên.

## Câu hỏi nghiên cứu

| # | Câu hỏi | Tiêu chí |
|---|---|---|
| Q1 | Các bang bắt buộc ghi lương trong tin (CA, CO, WA, NY, HI) có tỉ lệ công bố lương cao hơn bao nhiêu, khi so sánh trong cùng công ty, cùng chức năng và quy mô? Luật "chỉ khi được hỏi" có khác không? | D1 D3 D4 D5 D6 |
| Q2 | Tin remote trả cao hơn tin tại chỗ bao nhiêu %, và còn bao nhiêu khi so sánh công việc tương đương (cùng cấp bậc, chức năng, đơn vị lương) và trong cùng công ty? | D3 D4 D5 D6 |
| Q3 | Trong mỗi nhóm chức năng, lương Mid-Senior gấp bao nhiêu lần Entry? Thứ hạng có ổn định không? | D1 D2 D3 D5 D6 |
| Q4 | Với công việc tương đương, công ty ≥ 10,000 nhân viên trả cao hơn công ty nhỏ bao nhiêu %? Kết luận thô có bị đảo chiều? | D1 D3 D4 D5 D6 |
| Q5 | Cho phép remote và công khai lương gắn với tỉ lệ ứng tuyển/lượt xem cao hơn bao nhiêu điểm %? | D3 D4 D5 D6 |
| Q6 (ML) | Ước lượng lương năm của một tin từ thông tin có lúc đăng tin được chính xác đến đâu, và yếu tố nào quyết định? | Ridge vs. HistGradientBoosting vs. 2 baseline, chia theo công ty |

## Phát hiện chính

1. **Luật bắt buộc ghi lương gần như nhân đôi tỉ lệ công bố:** 49.7% so với 22.5% (+27.2 điểm %). Trong cùng công ty vẫn +17.5 điểm %; luật "chỉ khi được hỏi" chỉ +4.3 điểm %.
2. **Remote không bị trả thấp hơn:** thô +47%, nhưng với công việc tương đương còn khoảng **+13%** (+11 đến +14% ở mọi phương án, trong cùng công ty +12.6%).
3. **⭐ Nghịch lý Simpson về quy mô công ty:** thô thì tập đoàn ≥ 10k nhân viên trả *thấp hơn* 5.5%; so cùng loại việc thì trả *cao hơn* 9.8% (đến +19% nếu bỏ công ty staffing). Ngành IT không có chênh lệch theo quy mô.
4. **Lương khởi điểm cao ≠ tăng nhanh:** Mid-Senior ≈ 1.95× Entry; IT (×1.58) và Engineering (×1.52) thoải hơn thị trường, Consulting/Marketing dốc nhất.
5. **Remote thu hút ứng viên mạnh hơn công khai lương** (+5.7 so với +1.0 điểm % applies/views). **Mô hình Ridge ước lượng lương với MdAPE 19%** (MAE $25k, giảm 44% so với baseline); tiêu đề là yếu tố quan trọng nhất.

## Cấu trúc thư mục

```
linkedin-jobs/
├── README.md
├── requirements.txt  # danh sách thư viện (cài bằng venv + pip)
├── environment.yml   # cho ai dùng conda – cài đúng requirements.txt
├── LLM_USAGE.md
├── data/
│   ├── raw/          # CSV gốc từ Kaggle (không commit)
│   └── processed/    # postings_clean.parquet do notebook 01 tạo (không commit)
├── src/              # chỉ chứa code được ≥ 2 notebook dùng lại
│   ├── data.py       # đường dẫn, danh sách bang có luật lương, đọc nhóm chức năng, mã công ty
│   └── viz.py        # style + bảng màu biểu đồ thống nhất cho cả 3 notebook
├── notebooks/
│   ├── 01_collection_exploration.ipynb   # 3.1 + 3.2 + 3.3; chứa code làm sạch & ghép bảng
│   ├── 02_analysis.ipynb                 # Q1–Q5; chứa các hàm thống kê (bootstrap, so sánh trong nhóm con)
│   └── 03_ml_question.ipynb              # Q6 + tổng kết 3.5
└── slides.pdf        # TODO
```

## Cách chạy

Cần **Python ≥ 3.11** (kiểm tra bằng `python --version`). Mọi lệnh chạy từ thư mục gốc của project.

### 1. Tạo môi trường ảo (venv) và cài thư viện

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
> Nếu PowerShell báo lỗi "running scripts is disabled", chạy một lần: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, hoặc dùng Command Prompt với lệnh `.venv\Scripts\activate.bat`.

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Sau khi kích hoạt, đầu dòng lệnh có chữ `(.venv)`. Thư mục `.venv/` không được commit. Dùng **VS Code** thì chọn interpreter/kernel `.venv` khi mở notebook.

> Ai dùng conda có thể thay bước này bằng `conda env create -f environment.yml` rồi `conda activate csc17104-linkedin` – file đó cài đúng các thư viện trong `requirements.txt`.

### 2. Tải dữ liệu vào `data/raw/`

Tải `archive.zip` từ trang Kaggle (cần đăng nhập) rồi giải nén vào `data/raw/`:
```powershell
# Windows (PowerShell)
Expand-Archive archive.zip -DestinationPath data/raw
```
```bash
# macOS / Linux
unzip archive.zip -d data/raw/
```
Hoặc dùng Kaggle CLI (cần file API token `kaggle.json`): `pip install kaggle` rồi `kaggle datasets download -d arshkon/linkedin-job-postings -p data/raw --unzip`.

Sau bước này phải có: `data/raw/postings.csv`, `data/raw/companies/`, `data/raw/jobs/`, `data/raw/mappings/`.

### 3. Chạy notebook theo thứ tự

Notebook 01 tạo `data/processed/postings_clean.parquet` cho notebook 02 và 03. Có thể mở từng notebook trong VS Code / JupyterLab (`jupyter lab`) và chạy hết, hoặc chạy từ dòng lệnh (khi venv đang bật):
```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/01_collection_exploration.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/02_analysis.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/03_ml_question.ipynb
```

Thời gian chạy tham khảo (Windows, CPU 16 nhân): notebook 01 ≈ 1 phút, 02 ≈ 8–11 phút (nhiều vòng bootstrap), 03 ≈ 8 phút (grid search).

## Nguồn tham khảo về luật minh bạch lương (Q1)
- Seyfarth Shaw – *Pay Transparency Wage Range Disclosure Compendium* (2024): <https://www.seyfarth.com/dir_docs/documents/reports/2024-Pay-Transparency-Wage-Range-Disclosure-Compendium.pdf>
- NBC News – *More states are requiring companies to list salary ranges on job ads* (ngày hiệu lực DC 30/06/2024, MD 01/10/2024, IL và MN 01/01/2025): <https://www.nbcboston.com/news/business/money-report/more-states-are-requiring-companies-to-list-salary-ranges-on-job-ads-heres-where/3392804/>
- OysterLink – *States requiring salary range in job postings* (CA 01/01/2023; HI 01/01/2024 với công ty ≥ 50 NV; NY 17/09/2023): <https://oysterlink.com/spotlight/which-states-require-salary-range-in-jobs>
- Mondaq – tổng hợp luật theo bang (NYC 01/11/2022): <https://webiis08.mondaq.com/unitedstates/employee-rights-labour-relations/1596354/attention-employers-whats-the-state-of-pay-transparency-in-your-state-find-out-in-our-roundup-of-state-and-local-pay-transparency-laws>
- LegalTemplates – *Comply with pay transparency laws* (Colorado 01/01/2021): <https://legaltemplates.net/resources/business/comply-with-pay-transparency-laws>
