# Thị trường tuyển dụng Mỹ qua 124 nghìn tin LinkedIn (04/2024)

Đồ án cuối kỳ môn **CSC17104 - Lập trình cho Khoa học Dữ liệu**, Khoa Công nghệ Thông tin, Trường ĐH Khoa học Tự nhiên - ĐHQG-HCM.

## Thành viên và phân công

| Thành viên | MSSV | Câu hỏi phụ trách | Phần việc chung |
|---|---|---|---|
| *Đinh Võ Thủy Tiên* | *24120148* | Q1, Q2 | Thu thập & EDA ban đầu (Notebook 01) |
| Huỳnh Huy Hoàng | 24120181 | Q3, Q4 | Kỹ nghệ dữ liệu (src/data.py, viz.py) |
| Hoàng Hùng Quân | 23120338 | Q5, Q6 (ML) | Pipeline Học máy (Notebook 03), src/stats.py |

> Phần việc chung (thu thập dữ liệu, `src/`, notebook 01, README, slides…) cần ghi đúng người làm - giảng viên đối chiếu với lịch sử Git.

## Bộ dữ liệu

- **Tên:** LinkedIn Job Postings (2023 - 2024) - *A Snapshot Into the Current Job Market*
- **Nguồn:** Kaggle - <https://www.kaggle.com/datasets/arshkon/linkedin-job-postings>, tác giả tài khoản `arshkon`. Dữ liệu được cào bằng bộ cào mã nguồn mở <https://github.com/ArshKA/LinkedIn-Job-Scraper>; tài khoản `@zoeyyuzou` cào thêm ~100,000 tin. Phiên bản nhóm dùng có các file đề ngày 19/08/2024.
- **Giấy phép:** **CC BY-SA 4.0** (Creative Commons Attribution-ShareAlike 4.0) - ghi công tác giả Arsh Koneru (`arshkon`). Dữ liệu cào từ LinkedIn nên chỉ dùng cho mục đích học tập; dữ liệu gốc **không** được commit vào repo."
- **Nội dung:** 123,849 tin tuyển dụng ở Mỹ (31 cột) với tiêu đề, công ty, địa điểm, cấp bậc, loại hợp đồng, lương (29% tin có), lượt xem/ứng tuyển. Kèm 10 bảng phụ: công ty (quy mô, ngành, số nhân viên theo thời gian), nhóm chức năng, ngành, phúc lợi, lương. Gần như toàn bộ tin được đăng trong 05-20/04/2024.

### Các phân tích công khai đã có và điểm khác biệt
Các phân tích công khai trên cùng dataset mà nhóm tìm thấy: 2 notebook nhiều vote nhất ở tab **Code** của trang Kaggle (tra ngày 26/11/2026, tab có 69 notebook) và một số repo/trang khác:

| Phân tích | Nội dung chính |
|---|---|
| [Decoding the Job Market: An In-depth Exploration](https://www.kaggle.com/code/pratul007/decoding-the-job-market-an-in-depth-exploration) - Kaggle, pratul007 (93 vote) | EDA mô tả rộng: ghép các bảng theo `job_id`/`company_id`, điền giá trị thiếu bằng "Not Specified" hoặc 0; đếm tin theo loại việc, công ty, bang, phúc lợi; lương theo chức danh, cấp bậc, ngành; tương quan views-applies; TF-IDF + KMeans trên mô tả |
| [LinkedIn Job Postings 2023 Data Analysis](https://www.kaggle.com/code/enricofindley/linkedin-job-postings-2023-data-analysis) - Kaggle, enricofindley (84 vote) | Ghép và làm sạch các bảng (gộp `benefits`, `job_skills` theo `job_id`, ghép bảng công ty); EDA cơ bản: word cloud tiêu đề, phân bố quy mô công ty, loại việc, tin được tài trợ |
| [GunashreeC/Job-Recommendation-System](https://github.com/GunashreeC/Job-Recommendation-System) | Hệ thống gợi ý việc làm, NLP trên mô tả, SHAP |
| [sherinrose2019k-ops/LinkedIn-Job-Postings-Analysis](https://github.com/sherinrose2019k-ops/LinkedIn-Job-Postings-Analysis) | EDA: kỹ năng phổ biến, vai trò dữ liệu, xu hướng remote, word cloud |
| [AndhikaWB/linkedin-job-postings-analysis](https://github.com/AndhikaWB/linkedin-job-postings-analysis) | Dashboard Spark/Streamlit: số tin và lương tháng theo bang |
| [aimdata-labs: LinkedIn postings](https://aimdata-labs.github.io/linkedin_postings) | Lương theo ngành và nhóm công việc |

**Điểm khác biệt của nhóm:** các phân tích trên chủ yếu *mô tả* (đếm, trung bình theo nhóm). Câu hỏi của nhóm tập trung vào việc **tách hiệu ứng khỏi confounder**: so sánh trong cùng công ty (Q1), kiểm soát thành phần công việc (Q2, Q4 - phát hiện nghịch lý Simpson), định lượng bất định bằng bootstrap theo cụm công ty, và kiểm tra độ vững với các quy tắc làm sạch khác nhau. Nhóm cũng tự xây dựng quy tắc **sửa lỗi đơn vị lương** thay vì dùng thẳng `normalized_salary` (cột này có giá trị tới 535 triệu USD/năm). Mô hình Q6 được thiết kế **chống rò rỉ dữ liệu** (không dùng mô tả, chia theo công ty). Nhóm không tái sử dụng code của các phân tích trên.

## Câu hỏi nghiên cứu

| # | Câu hỏi | Tiêu chí |
|---|---|---|
| Q1 | Các bang bắt buộc ghi lương trong tin (CA, CO, WA, NY, HI) có tỉ lệ công bố lương cao hơn bao nhiêu, khi so sánh trong cùng công ty, cùng chức năng và quy mô? Luật "chỉ khi được hỏi" có khác không? | D1 D3 D4 D5 D6 |
| Q2 | Tin remote trả cao hơn tin tại chỗ bao nhiêu %, và còn bao nhiêu sau khi kiểm soát cấp bậc, chức năng, hợp đồng, đơn vị lương, bang, quy mô, ngành? | D3 D4 D5 D6 |
| Q3 | Trong mỗi nhóm chức năng, lương Mid-Senior gấp bao nhiêu lần Entry? Thứ hạng có ổn định không? | D1 D2 D3 D5 D6 |
| Q4 | Với công việc tương đương, công ty ≥ 10,000 nhân viên trả cao hơn công ty nhỏ bao nhiêu %? Kết luận thô có bị đảo chiều? | D1 D3 D4 D5 D6 |
| Q5 | Cho phép remote và công khai lương gắn với tỉ lệ ứng tuyển/lượt xem cao hơn bao nhiêu điểm %? | D3 D4 D5 D6 |
| Q6 (ML) | Ước lượng lương năm của một tin từ thông tin có lúc đăng tin được chính xác đến đâu, và yếu tố nào quyết định? | Ridge vs. HistGradientBoosting vs. 2 baseline, chia theo công ty |

## Phát hiện chính

1. **Luật bắt buộc ghi lương gần như nhân đôi tỉ lệ công bố:** 49.7% so với 22.5% (+27.2 điểm %). Trong cùng công ty vẫn +16.6 điểm %; luật "chỉ khi được hỏi" chỉ +4.3 điểm %.
2. **Remote không bị trả thấp hơn:** thô +47%, nhưng với công việc tương đương còn khoảng **+11%** (ổn định ở mọi phương án, kể cả so sánh trong cùng công ty).
3. **⭐ Nghịch lý Simpson về quy mô công ty:** thô thì tập đoàn ≥ 10k nhân viên trả *thấp hơn* 7.6%; so cùng loại việc thì trả *cao hơn* 5.7% (đến +13% nếu bỏ công ty staffing). Ngành IT không có chênh lệch theo quy mô.
4. **Lương khởi điểm cao ≠ tăng nhanh:** Mid-Senior ≈ 1.95× Entry; IT (×1.58) và Engineering (×1.52) thoải hơn thị trường, Consulting/Marketing dốc nhất.
5. **Remote thu hút ứng viên mạnh hơn công khai lương** (+6.0 so với +1.0 điểm % applies/views). **Mô hình Ridge ước lượng lương với MdAPE 19%** (MAE $25k, giảm 44% so với baseline); tiêu đề là yếu tố quan trọng nhất.

## Cấu trúc thư mục

```
linkedin-jobs/
├── README.md
├── environment.yml
├── LLM_USAGE.md
├── data/
│   ├── raw/          # CSV gốc từ Kaggle (không commit)
│   └── processed/    # postings_clean.parquet do notebook 01 tạo (không commit)
├── src/
│   ├── data.py       # đọc, làm sạch, sửa đơn vị lương, suy ra bang, ghép bảng
│   ├── stats.py      # bootstrap theo cụm, OLS cluster-robust, effect size
│   └── viz.py        # style biểu đồ thống nhất
├── notebooks/
│   ├── 01_collection_exploration.ipynb   # 3.1 + 3.2 + 3.3
│   ├── 02_analysis.ipynb                 # Q1-Q5
│   └── 03_ml_question.ipynb              # Q6 + tổng kết 3.5
└── slides.pdf        # TODO
```

## Cách chạy

```bash
# 1. Tạo môi trường
conda env create -f environment.yml
conda activate csc17104-linkedin

# 2. Tải dữ liệu (cần tài khoản Kaggle) và giải nén vào data/raw/
#    Cách 1: tải archive.zip từ trang Kaggle rồi:
unzip archive.zip -d data/raw/
#    Cách 2: dùng Kaggle CLI (cần ~/.kaggle/kaggle.json)
kaggle datasets download -d arshkon/linkedin-job-postings -p data/raw --unzip

#    Sau bước này phải có: data/raw/postings.csv, data/raw/companies/, data/raw/jobs/, data/raw/mappings/

# 3. Chạy notebook theo thứ tự (01 tạo data/processed/ cho 02 và 03)
jupyter nbconvert --to notebook --execute --inplace notebooks/01_collection_exploration.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/02_analysis.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/03_ml_question.ipynb
```

Thời gian chạy tham khảo (CPU 2 nhân, RAM 8 GB): notebook 01 ≈ 1 phút, 02 ≈ 1 phút, 03 ≈ 4 phút (grid search).

## Nguồn tham khảo về luật minh bạch lương (Q1)
- Seyfarth Shaw - *Pay Transparency Wage Range Disclosure Compendium* (2024): <https://www.seyfarth.com/dir_docs/documents/reports/2024-Pay-Transparency-Wage-Range-Disclosure-Compendium.pdf>
- NBC News - *More states are requiring companies to list salary ranges on job ads* (ngày hiệu lực DC 30/06/2024, MD 01/10/2024, IL và MN 01/01/2025): <https://www.nbcboston.com/news/business/money-report/more-states-are-requiring-companies-to-list-salary-ranges-on-job-ads-heres-where/3392804/>
- OysterLink - *States requiring salary range in job postings* (CA 01/01/2023; HI 01/01/2024 với công ty ≥ 50 NV; NY 17/09/2023): <https://oysterlink.com/spotlight/which-states-require-salary-range-in-jobs>
- Mondaq - tổng hợp luật theo bang (NYC 01/11/2022): <https://webiis08.mondaq.com/unitedstates/employee-rights-labour-relations/1596354/attention-employers-whats-the-state-of-pay-transparency-in-your-state-find-out-in-our-roundup-of-state-and-local-pay-transparency-laws>
- LegalTemplates - *Comply with pay transparency laws* (Colorado 01/01/2021): <https://legaltemplates.net/resources/business/comply-with-pay-transparency-laws>
