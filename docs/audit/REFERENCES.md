# Tài liệu tham khảo đã đọc (Pha 3, loop 8 — 27/09/2026)

Mỗi mục: link · điều lấy được · áp dụng hay không, vì sao. "Đã đọc" = mở trang/bản full text trong lượt này;
chỗ chỉ đọc được một phần được ghi rõ.

## 1. Nguồn gốc & phương pháp đánh giá

### He et al. 2017 — Neural Collaborative Filtering (WWW)
- Link: https://arxiv.org/abs/1708.05031 (full text: https://ar5iv.labs.arxiv.org/html/1708.05031)
- Đọc full text. Điều lấy được:
  - NeuMF cho GMF và MLP **embedding riêng**, ghép lớp ẩn cuối rồi qua lớp output.
  - Pre-training: GMF, MLP huấn luyện bằng **Adam**; NeuMF fine-tune bằng **SGD thường**; lớp output khởi tạo
    `h ← [α·h_GMF, (1−α)·h_MLP]`, **α = 0,5**.
  - Negative sampling: mặc định 4; 1 là không đủ, tốt nhất khoảng **3–6**; > 7 bắt đầu giảm (Pinterest).
  - Predictive factors thử 8, 16, 32, 64; tháp MLP giảm một nửa mỗi tầng.
  - Đánh giá: leave-one-out tương tác mới nhất, xếp hạng giữa **100 item âm lấy mẫu**, HR@10, NDCG@10;
    validation = 1 tương tác chọn ngẫu nhiên mỗi user.
  - Pre-training giúp +2,2% (MovieLens) / +1,1% (Pinterest); với factor 8 trên MovieLens thì hơi kém hơn.
- Áp dụng: kiến trúc + pre-training (đã có, `src/models/neumf.py`), α = 0,5, negative 4, tháp [64,32,16,8].
  **Không áp dụng**: SGD cho fine-tune (đo trên dữ liệu của dự án: SGD lr 0,01 làm NeuMF-Scratch không hội tụ,
  loss ≈ entropy nhãn — xem chẩn đoán trước loop), đánh giá sampled-100 (dùng Full Ranking, xem Krichene & Rendle),
  validation ngẫu nhiên (dùng mốc thời gian chung, Q1).

### Code gốc NCF — github.com/hexiangnan/neural_collaborative_filtering
- Đọc README. Lệnh mẫu: GMF `--num_factors 8 --num_neg 4 --lr 0.001 --learner adam --epochs 20 --batch_size 256`;
  MLP `--layers [64,32,16,8] --reg_layers [0,0,0,0]`; NeuMF `--mf_pretrain ... --mlp_pretrain ...`.
  README: "for large predictive factors, pre-training NeuMF can yield better performance".
- Áp dụng: dải tham số khởi đầu (batch 256–512, 20 epoch, lr 1e-3). Cạm bẫy (theo Dacrema 2019, bên dưới): code gốc
  chọn số epoch theo tập test → dự án đã khoá test (loop 6).

### Microsoft Recommenders — examples/02_model_collaborative_filtering/ncf_deep_dive.ipynb
- Link: https://github.com/recommenders-team/recommenders/blob/main/examples/02_model_collaborative_filtering/ncf_deep_dive.ipynb
- **Chỉ đọc được một phần** (raw notebook, bản tóm tắt tự mâu thuẫn: vừa nói `python_chrono_split` 75/25 vừa nói
  leave-one-out + 100 negatives). Chắc chắn: MovieLens 100k, 100 epoch, batch 256, metric MAP/NDCG/Precision/Recall@10,
  mô tả GMF + MLP + pretraining.
- Áp dụng: chỉ làm đối chiếu cách báo cáo Precision/Recall@K; không dùng số liệu. Cần mở lại notebook trước khi trích
  trong báo cáo.

### Rendle et al. 2020 — NCF vs. Matrix Factorization Revisited (RecSys)
- Link: https://arxiv.org/abs/2005.09683 (full text ar5iv). Đọc full text.
- Điều lấy được: dùng lại đúng protocol NCF (leave-one-out, 100 negatives). MF tích vô hướng tune: d ∈ {16,…,192},
  λ ∈ {0,001; 0,003; 0,01}, negative m = 8 (ML) / 10 (Pinterest), lr 0,002 / 0,007, tới 256 epoch, SGD không batch.
  Kết quả d=192: MF HR@10 0,7294 / NDCG@10 0,4523 vs NeuMF 0,7093 / 0,4349 (MovieLens). Bài học: MLP khó học tích vô
  hướng; lớp trọng số học được sau GMF + λ>0 dễ làm embedding co về 0, trọng số phình → mất ổn định; MLP không dùng
  được cho truy hồi top-N thời gian thực.
- Áp dụng: **baseline MF phải được tune cùng ngân sách** (d, λ, negative, lr, epoch) — BPR-MF hiện chỉ d=32, 20 epoch,
  lr cố định → yếu. Báo cáo phải chấp nhận kết quả âm nếu NeuMF không vượt MF đã tune. Ứng viên B (late fusion
  MF + NeuMF) lấy cảm hứng từ đây.

### Ferrari Dacrema et al. 2019 — Are We Really Making Much Progress? (RecSys)
- Link: https://arxiv.org/abs/1907.06902 (full text ar5iv); repo MaurizioFD/RecSys2019_DeepLearning_Evaluation.
- Đọc full text (qua tóm tắt có trích dẫn). Điều lấy được: NCF tái lập được nhưng **code gốc chọn epoch theo tập test**;
  trên Pinterest ItemKNN, RP3β vượt NeuMF; trên MovieLens1M SLIM vượt NeuMF; baseline trong bài gốc tune sơ sài.
- Áp dụng: khoá tập test + chọn trên validation (đã làm), tune baseline đủ, thêm baseline mạnh. ItemKNN hiện là
  ma trận dày O(items²) — với 10.345 item vượt ngưỡng an toàn `ITEMKNN_MAX_ITEMS=5000` (`src/baselines/classical.py`)
  → không chạy; ghi là hạn chế thay vì bỏ qua âm thầm.

### Krichene & Rendle 2020 — On Sampled Metrics for Item Recommendation (KDD)
- Link: https://research.google/pubs/on-sampled-metrics-for-item-recommendation/ ;
  https://dl.acm.org/doi/10.1145/3394486.3403226. Đọc trang abstract + tóm tắt.
- Điều lấy được: metric lấy mẫu **không nhất quán** với bản đầy đủ, có thể đảo "A tốt hơn B"; mẫu càng nhỏ các metric
  càng tiến về AUC; khuyến nghị "sampling should be avoided".
- Áp dụng: Full Ranking là protocol chính (R6); sampled-99 chỉ đối chiếu.

### Rendle et al. 2022 — Revisiting the Performance of iALS on Item Recommendation Benchmarks (RecSys)
- Link: https://arxiv.org/abs/2110.14037 (full text ar5iv). Đọc full text.
- Điều lấy được: iALS tune đúng cạnh tranh với mô hình neural; **embedding dimension thường bị chọn quá nhỏ**; λ và
  trọng số unobserved α₀ phải tune cùng nhau; regularization theo tần suất (ν=1) giúp khi d lớn; khởi đầu d=128 rồi
  nhân đôi, theo dõi các thành phần loss.
- Áp dụng: thêm baseline iALS (thư viện `implicit`, người dùng cho phép) với lưới d, λ, α; cùng ngân sách tuning.

## 2. Kiến trúc lai MF + DNN thuần CF

### Xue et al. 2017 — Deep Matrix Factorization (DMF, IJCAI)
- Link: https://www.ijcai.org/proceedings/2017/447 (PDF không trích được chữ → **chỉ đọc abstract**).
- Điều lấy được: đầu vào là hàng/cột ma trận user–item (rating tường minh + implicit), kiến trúc hai tháp học không
  gian chung, loss BCE chuẩn hoá theo rating.
- Áp dụng: là nhánh representation của DeepCF (ứng viên C). H&M chỉ có implicit → dùng vector 0/1 (hoặc số lần mua,
  chỉ từ train). Cần đọc full text trước khi mô tả chi tiết trong báo cáo.

### Deng et al. 2019 — DeepCF (AAAI); repo familyld/DeepCF
- Link: https://arxiv.org/abs/1901.04704 (full text ar5iv); https://github.com/familyld/DeepCF. Đọc full text + README.
- Điều lấy được: CFNet = CFNet-rl (tháp kiểu DMF, đầu vào là hàng ma trận tương tác) + CFNet-ml (MLP kiểu NeuMF),
  ghép và qua lớp FC; BCE, negative lấy mẫu đều, có pre-training; vượt NeuMF 0,6–16,6% (lợi hơn trên dữ liệu thưa);
  README: lớp [512, 64] (hoặc user [1024, 64]), lr 0,01 không pretrain, 0,0001 khi pretrain, SGD mặc định.
- Áp dụng: ứng viên C. Vector đầu vào phải xây **chỉ từ train**. Bộ nhớ: ma trận 7.519 × 10.345 (float32 ≈ 0,31 GB)
  vừa GPU 4 GB; Full Ranking: tính trước vector item của nhánh rl một lần, nhánh ml như NeuMF. Cần đo thật (Pha 3b).

### RecBole — NeuMF
- Link: https://recbole.io/docs/user_guide/model/general/neumf.html. Đọc trang.
- Mặc định: mf_embedding_size 64, mlp_embedding_size 64, mlp_hidden_size [128,64], dropout 0,1, use_pretrain False;
  lưới gợi ý: lr {1e-2, 5e-3, 1e-3, 5e-4, 1e-4}, dropout {0–0,5}, hidden {[64,32,16], [32,16,8]}.
- Áp dụng: làm lưới tham chiếu cho ứng viên A (tune NeuMF) cùng ngân sách với baseline.

## 3. Chỉ để hiểu dữ liệu (KHÔNG so số, KHÔNG dùng đặc trưng)
- Cuộc thi Kaggle H&M: https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations — dự đoán
  12 món mua trong 7 ngày sau khi dữ liệu train kết thúc, MAP@12, lời giải dùng metadata + ranker. Khác hoàn toàn
  protocol ở đây (item pool, metric, dùng metadata) → không đặt số cạnh nhau.
