# Tài liệu học chi tiết — Đồ án NeuMF-F

Tài liệu viết từ bản tóm tắt `on_tap_kien_thuc.md` (Phần A). Mỗi khái niệm có 5 ý: **(a)** định nghĩa, **(b)** trực
giác, **(c)** công thức, **(d)** ví dụ tính tay, **(e)** liên hệ với đồ án. Số liệu của đồ án chỉ lấy từ bản tóm tắt; số
dùng để minh hoạ ghi rõ "ví dụ minh hoạ".

| Cấp | Nội dung |
|---|---|
| 1 | Khái niệm nền |
| 2 | Học máy cơ bản |
| 3 | Hệ khuyến nghị: từ cổ điển đến học sâu |
| 4 | Mô hình đề xuất NeuMF-F và đặc trưng |
| 5 | Dữ liệu, đánh giá, thống kê, quy trình |
| — | Kết quả chính và 20 câu hỏi hội đồng |

---

## Cấp 1 — Khái niệm nền

### 1.1 Hệ khuyến nghị (*recommender system*)

**(a) Định nghĩa.** Hệ khuyến nghị là chương trình nhìn vào những gì người dùng đã làm trong quá khứ (mua gì, xem gì) để
đoán họ sẽ thích gì tiếp theo, rồi đưa ra một danh sách ngắn các gợi ý.

**(b) Trực giác.** Giống người bán hàng quen ở cửa hàng thời trang: thấy bạn hay mua quần jean và áo thun đen, lần sau họ
mang ra đúng mấy mẫu jean mới và áo thun tối màu, chứ không bày cả kho ra cho bạn tự tìm.

**(c) Công thức.** Về bản chất, hệ khuyến nghị học một **hàm tính điểm**:

$$\hat{y}_{ui} = f(u, i)$$

- $u$: một khách hàng (*user*).
- $i$: một sản phẩm (*item*).
- $\hat{y}_{ui}$: điểm dự đoán — khách $u$ có khả năng mua sản phẩm $i$ đến đâu. Dấu mũ ^ nghĩa là "giá trị dự đoán".
- $f$: mô hình. Các cấp sau chính là các cách khác nhau để xây $f$.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** Một khách có 4 sản phẩm ứng viên, mô hình chấm điểm:

| Sản phẩm | Điểm $\hat{y}$ |
|---|---|
| Quần jean | 0,8 |
| Áo thun | 0,6 |
| Váy | 0,1 |
| Giày | 0,3 |

Xếp giảm dần: jean (0,8) → áo thun (0,6) → giày (0,3) → váy (0,1). Gợi ý 2 món: **jean, áo thun**.

**(e) Trong đồ án.** Bài toán là: với mỗi khách H&M, gợi ý sản phẩm thời trang khách có khả năng **mua lần đầu** trong 8
tuần tới. Mô hình đề xuất là **NeuMF-F**; đồ án so nó với 14 mô hình khác (tổng 15 mô hình), trên hai bộ dữ liệu H&M và
Amazon Beauty.

### 1.2 Phản hồi tường minh (*explicit feedback*)

**(a) Định nghĩa.** Người dùng **tự nói** họ thích đến đâu, thường bằng điểm số: 1–5 sao, thích/không thích.

**(b) Trực giác.** Bạn mua một chiếc áo rồi để lại đánh giá 2 sao "vải mỏng". Cửa hàng biết rõ bạn **không hài lòng**.

**(c) Công thức.** Dữ liệu là điểm $r_{ui}$ (*rating*) của khách $u$ cho sản phẩm $i$, ví dụ $r_{ui} \in \{1,2,3,4,5\}$.
Mô hình học cách đoán $\hat{r}_{ui}$ sát với $r_{ui}$.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** Khách chấm áo A 5 sao, mô hình đoán 4 → sai 1 sao. Chấm áo B 2 sao, mô hình
đoán 4 → sai 2 sao. Sai trung bình $(1 + 2)/2 = 1{,}5$ sao.

**(e) Trong đồ án.** Đồ án **không** dùng loại phản hồi này. H&M chỉ có giao dịch mua, không có điểm đánh giá. Với Amazon
Beauty, dữ liệu có điểm sao nhưng đồ án cũng **không dùng điểm sao** — mỗi lượt đánh giá chỉ được coi là một lần "có
tương tác" để hai bộ dữ liệu xử lý giống nhau.

### 1.3 Phản hồi ngầm (*implicit feedback*)

**(a) Định nghĩa.** Chỉ biết **hành vi** của người dùng (mua, xem, bấm), không biết họ thích đến đâu. Có hành vi → 1;
không có hành vi → chưa biết gì.

**(b) Trực giác.** Bạn mua chiếc áo đỏ → chắc có quan tâm. Nhưng bạn **không mua** chiếc áo xanh thì có hai khả năng: bạn
không thích, hoặc **bạn chưa bao giờ thấy nó**. Không phân biệt được. Vì vậy "không mua" **không có nghĩa là** "không
thích".

**(c) Công thức.**

$$y_{ui} = \begin{cases} 1 & \text{nếu khách } u \text{ đã mua sản phẩm } i \\ 0 & \text{nếu chưa (không rõ thích hay không)} \end{cases}$$

- $y_{ui}$: nhãn quan sát được (không có dấu mũ vì là dữ liệu thật, không phải dự đoán).

**(d) Ví dụ tính tay (ví dụ minh hoạ).** Khách mua áo A 3 lần, áo B 1 lần, chưa mua áo C:

| Sản phẩm | Số lần mua | $y_{ui}$ |
|---|---|---|
| Áo A | 3 | 1 |
| Áo B | 1 | 1 |
| Áo C | 0 | 0 |

Mua 3 lần hay 1 lần đều thành 1 — chỉ ghi nhận "đã mua".

**(e) Trong đồ án.** Đồ án dùng phản hồi ngầm: **mua = 1**. Vì "không mua" không chắc là "không thích", đồ án không đoán
điểm số mà làm bài toán **xếp hạng**, và phải tự tạo ví dụ "không mua" bằng **mẫu âm** (Cấp 3: mỗi cặp đã mua rút 8 món
chưa mua).

### 1.4 Bài toán Top-K

**(a) Định nghĩa.** Với mỗi khách, chấm điểm **mọi** sản phẩm ứng viên, xếp từ cao đến thấp, rồi chỉ đưa ra **K món đầu**.

**(b) Trực giác.** Trang chủ app chỉ có chỗ cho khoảng 10 ô "Gợi ý cho bạn". Quan trọng không phải điểm chính xác bao
nhiêu, mà là **món đúng có lọt vào 10 ô đó không, và nằm cao hay thấp**.

**(c) Công thức.**

$$\text{Top-}K(u) = \operatorname*{arg\,top\text{-}K}_{i \in C_u} \hat{y}_{ui}$$

- $C_u$: tập ứng viên (*candidate set*) của khách $u$ — các sản phẩm được phép gợi ý.
- $\hat{y}_{ui}$: điểm mô hình chấm cho từng món.
- $\operatorname{arg\,top\text{-}K}$: lấy ra **K sản phẩm** có điểm cao nhất (lấy sản phẩm, không lấy điểm).

**(d) Ví dụ tính tay (ví dụ minh hoạ).** Dùng lại bảng ở 1.1, K = 3: xếp jean (0,8), áo thun (0,6), giày (0,3), váy
(0,1) → Top-3 = {jean, áo thun, giày}. Nếu khách thật sự mua giày sau đó → món đúng nằm ở **hạng 3**.

**(e) Trong đồ án.** K chính là **10**; báo cáo trình bày thêm K = 15 và 20. Trên H&M, mỗi khách có khoảng **6.700 món
ứng viên**, và mô hình phải chấm **toàn bộ** số món này (gọi là Full Ranking — Cấp 5).

### 1.5 Ma trận tương tác và độ thưa (*interaction matrix, sparsity*)

**(a) Định nghĩa.** Bảng có hàng = khách, cột = sản phẩm, ô = 1 nếu khách đã mua món đó, ngược lại = 0. "Thưa" nghĩa là
gần như toàn bộ ô bằng 0.

**(b) Trực giác.** Một cửa hàng có hàng nghìn mẫu áo; mỗi người chỉ mua vài chục món. Nhìn bảng khách × sản phẩm sẽ thấy
gần như trống trơn, chỉ lác đác vài dấu 1. Nhiệm vụ của mô hình là **đoán những ô trống** nào thật ra khách sẽ mua.

**(c) Công thức.**

$$\text{Độ dày} = \frac{\text{số ô bằng 1}}{\text{số khách} \times \text{số sản phẩm}}, \qquad \text{Độ thưa} = 1 - \text{Độ dày}$$

- Tử số: số cặp (khách, sản phẩm) đã có giao dịch.
- Mẫu số: tổng số ô của bảng.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** 3 khách × 4 sản phẩm = 12 ô; có 3 ô bằng 1:

| | Áo A | Áo B | Quần C | Giày D |
|---|---|---|---|---|
| Khách 1 | 1 | 0 | 0 | 0 |
| Khách 2 | 0 | 1 | 1 | 0 |
| Khách 3 | 0 | 0 | 0 | 0 |

Độ dày = 3/12 = 25%. Dữ liệu thật thưa hơn rất nhiều.

**(e) Trong đồ án.** Mẫu kiểm định H&M sau khi lọc có **243.696 cặp** trên **7.994 khách × 6.749 sản phẩm**:

$$\frac{243.696}{7.994 \times 6.749} \approx 0{,}45\%$$

Tức **99,55% ô trống** — mô hình phải đoán gần như toàn bộ bảng từ một phần rất nhỏ dữ liệu. Đây là lý do cần thêm
**đặc trưng** (thuộc tính, mô tả, thời gian) ngoài lịch sử mua.

### 1.6 Cold start

**(a) Định nghĩa.** Tình huống khách hoặc sản phẩm **mới**, chưa có (hoặc có rất ít) lịch sử mua, nên mô hình không có gì
để học về họ.

**(b) Trực giác.** Khách lần đầu vào cửa hàng: người bán chưa biết gu, nên giới thiệu **món bán chạy**. Mẫu áo vừa ra
mắt: chưa ai mua, nhưng người bán vẫn biết "đây là áo thun, màu đen, chất cotton" → vẫn giới thiệu được cho người thích
áo thun đen.

**(c) Công thức.** Với mô hình chỉ dùng ID, vector của một sản phẩm được học từ các lần mua:

$$\mathbf{q}_i \leftarrow \text{học từ các cặp } (u, i) \text{ đã mua}$$

Nếu sản phẩm $i$ chưa có cặp nào, $\mathbf{q}_i$ không được cập nhật → gần như vô nghĩa. Mô hình có đặc trưng thêm phần
$W_I\,\mathbf{x}_i$ (Cấp 4), trong đó $\mathbf{x}_i$ là **thông tin mô tả** sản phẩm — có ngay cả khi chưa ai mua.

**(d) Ví dụ minh hoạ.** Áo mới ra mắt, 0 lượt mua. Mô hình chỉ dùng ID: vector ngẫu nhiên ban đầu → điểm ngẫu nhiên. Mô
hình có đặc trưng: biết thuộc tính "áo thun, đen" giống các áo khách đã mua → điểm cao hơn hợp lý.

**(e) Trong đồ án.**

- Demo: **khách mới** (chưa có trong dữ liệu đã học) nhận danh sách **Most Popular** — món bán chạy.
- Mô hình đề xuất **NeuMF-F** cộng đặc trưng vào vector ID để sản phẩm ít người mua vẫn được biểu diễn tốt.
- Đặc trưng thời gian có cờ **"chưa từng bán"** (Cấp 4) để mô hình nhận ra hàng mới.

### 1.7 Mô hình và tham số (*model, parameter*)

**(a) Định nghĩa.** **Mô hình** là công thức tính điểm. **Tham số** là các con số bên trong công thức mà máy **tự học**
từ dữ liệu (trọng số, vector embedding).

**(b) Trực giác.** Công thức nấu ăn là mô hình; lượng muối, đường cụ thể là tham số — nấu thử nhiều lần (huấn luyện) để
chỉnh cho vừa miệng (dữ liệu).

**(c) Công thức (ví dụ đơn giản).**

$$\hat{y} = w_1 x_1 + w_2 x_2 + b$$

- $x_1, x_2$: dữ liệu đầu vào (ví dụ: khách có hay mua áo thun không, sản phẩm có đang bán chạy không).
- $w_1, w_2$: **trọng số** — tham số, máy tự học.
- $b$: hệ số chệch (*bias*) — cũng là tham số.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** $w_1 = 2$, $w_2 = 1$, $b = -1$; khách hay mua áo thun ($x_1 = 1$), sản phẩm
đang bán chạy ($x_2 = 1$): $\hat{y} = 2 \cdot 1 + 1 \cdot 1 - 1 = 2$. Nếu sản phẩm không bán chạy ($x_2 = 0$):
$\hat{y} = 1$ → điểm thấp hơn.

**(e) Trong đồ án.** Tham số của NeuMF-F gồm: vector embedding ID của từng khách và sản phẩm, embedding 8 chiều cho mỗi
giá trị thuộc tính, các ma trận chiếu $W_U$, $W_I$, trọng số các lớp của tháp MLP. Tất cả học bằng Adam trong quá trình
huấn luyện (Cấp 2).

### 1.8 Siêu tham số (*hyperparameter*)

**(a) Định nghĩa.** Các con số **người làm chọn trước** khi huấn luyện; máy không tự học được chúng.

**(b) Trực giác.** Trong công thức nấu ăn: nhiệt độ lò, thời gian nướng — bạn phải đặt trước rồi mới nướng. Muốn biết
đặt bao nhiêu là tốt thì phải nướng thử vài mẻ rồi so.

**(c) Công thức.** Không có công thức chung; huấn luyện là tìm tham số tốt nhất **với siêu tham số cho trước**:

$$\Theta^* = \arg\min_{\Theta} L(\Theta \mid \lambda)$$

- $\Theta$: tham số (máy học).
- $\lambda$: siêu tham số (người chọn).
- $L$: hàm mất mát (Cấp 2).
- **Tinh chỉnh** = thử nhiều $\lambda$, mỗi lần huấn luyện ra $\Theta^*$, chấm trên tập xác thực, giữ $\lambda$ tốt nhất.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** Thử 3 tốc độ học, chấm trên tập xác thực:

| lr | Điểm xác thực |
|---|---|
| 0,01 | 0,020 |
| 0,001 | 0,035 |
| 0,0001 | 0,028 |

→ chọn lr = 0,001.

**(e) Trong đồ án.** Siêu tham số gồm: số chiều d, tốc độ học lr, số mẫu âm, dropout, weight decay, ρ, k của KNN… Cấu
hình chọn cho NeuMF-F: **d = 32, lr = 0,001, 8 mẫu âm, weight decay 1e-6, dropout 0, ρ = 0**. Mỗi mô hình thử **6 cấu
hình** (cùng ngân sách), tổng **76 cấu hình, 4,7 giờ**, chỉ trên tập xác thực của mẫu phát triển.

### 1.9 Tập huấn luyện, xác thực, kiểm thử (*training, validation, test set*)

**(a) Định nghĩa.**

- **Tập huấn luyện**: dữ liệu để máy học tham số.
- **Tập xác thực**: dữ liệu để **chọn** siêu tham số và số epoch.
- **Tập kiểm thử**: dữ liệu để **kết luận cuối cùng**, chỉ được mở một lần.

**(b) Trực giác.** Ôn thi: sách giáo khoa là tập huấn luyện; đề thi thử là tập xác thực (làm thử để chỉnh cách học); đề
thi thật là tập kiểm thử. Nếu lén xem đề thi thật rồi luyện theo nó, điểm cao nhưng **không phản ánh năng lực thật**.

**(c) Công thức (phân chia theo thời gian).** Với mốc $\tau$:

$$\text{Huấn luyện} = \{(u,i,t) : t < \tau\}, \qquad \text{Kiểm thử} = \{(u,i,t) : \tau \le t < \tau + \Delta\}$$

- $(u, i, t)$: khách $u$ mua sản phẩm $i$ vào ngày $t$.
- $\tau$: mốc thời gian chia; $\Delta$: độ dài cửa sổ đánh giá.

**(d) Ví dụ minh hoạ.** Dữ liệu 01/01–31/12. Huấn luyện: 01/01–31/10. Xác thực: 01/11–30/11 (chọn cấu hình). Kiểm thử:
01/12–31/12 (chỉ chấm một lần ở cuối).

**(e) Trong đồ án.**

| | Xác thực | Kiểm thử |
|---|---|---|
| Mốc τ | 01/07/2020 | 29/07/2020 |
| Cửa sổ món đúng | 01/07–28/07/2020 (4 tuần) | 29/07–22/09/2020 (8 tuần) |
| Dùng cho | Chọn cấu hình (mẫu phát triển), chọn số epoch (mẫu kiểm định) | Kết luận (mẫu kiểm định), mở 1 lần |

Đồ án còn chặt hơn: có **hai mẫu khách khác hẳn nhau**. Mọi quyết định làm trên **mẫu phát triển**; kết luận chỉ lấy trên
**mẫu kiểm định**. Mỗi lần mở tập kiểm thử đều ghi nhật ký.

### Câu hỏi tự kiểm tra — Cấp 1

1. **Vì sao "không mua" không có nghĩa là "không thích"?** — Vì có thể khách chưa từng thấy sản phẩm đó; phản hồi ngầm
   chỉ biết hành vi, không biết cảm nhận.
2. **Bài toán Top-K quan tâm điều gì hơn điểm số chính xác?** — Món đúng có lọt vào K món đầu không và nằm ở hạng cao hay
   thấp.
3. **Độ dày của ma trận H&M (mẫu kiểm định) là bao nhiêu và nói lên gì?** — Khoảng 0,45%; dữ liệu cực thưa, cần thêm đặc
   trưng ngoài lịch sử mua.
4. **Tham số khác siêu tham số thế nào? Cho ví dụ trong đồ án.** — Tham số máy tự học (embedding, trọng số); siêu tham số
   người chọn trước (d = 32, lr = 0,001, 8 mẫu âm).
5. **Vì sao không được chọn cấu hình bằng tập kiểm thử?** — Như xem trước đề thi: điểm cao do chọn trúng cấu hình ăn may
   trên đúng tập đó, không phản ánh khả năng trên dữ liệu mới.

---

## Cấp 2 — Học máy cơ bản

### 2.1 Epoch

**(a) Định nghĩa.** Một **epoch** là một lượt mô hình đi qua **toàn bộ** dữ liệu huấn luyện đúng một lần.

**(b) Trực giác.** Ôn bộ 500 câu trắc nghiệm: làm hết 500 câu một lượt là 1 epoch. Làm lại từ đầu lần thứ hai là epoch
thứ 2. Mỗi lượt bạn nhớ thêm một chút.

**(c) Công thức.**

$$\text{Số lần cập nhật trong 1 epoch} = \left\lceil \frac{N}{B} \right\rceil$$

- $N$: số mẫu huấn luyện; $B$: kích thước batch (2.2); $\lceil\cdot\rceil$: làm tròn lên.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** $N = 10.000$ mẫu, $B = 512$: $10.000 / 512 = 19{,}53$ → làm tròn lên **20 lần
cập nhật** mỗi epoch. Huấn luyện 5 epoch = 100 lần cập nhật.

**(e) Trong đồ án.** Mạng nơ-ron huấn luyện **tối đa 20 epoch**; số epoch thật sự dùng do **dừng sớm** quyết định (2.10).
Ở đánh giá cuối, số epoch được chọn trên tập xác thực rồi **huấn luyện lại từ đầu** đúng số epoch đó.

### 2.2 Batch

**(a) Định nghĩa.** **Batch** là một gói nhỏ mẫu dữ liệu. Thay vì đưa cả triệu mẫu vào một lúc, mô hình xử lý từng gói:
dự đoán → đo lỗi → cập nhật trọng số.

**(b) Trực giác.** Chấm 500 bài kiểm tra: thay vì đọc hết rồi mới rút kinh nghiệm, cứ chấm xong 50 bài lại điều chỉnh
cách chấm một lần — nhanh và đỡ tốn trí nhớ.

**(c) Công thức.** Lỗi của một batch là trung bình lỗi các mẫu trong batch:

$$L_{\text{batch}} = \frac{1}{B}\sum_{k=1}^{B} \ell_k$$

- $B$: số mẫu trong batch; $\ell_k$: lỗi của mẫu thứ $k$.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** Batch 4 mẫu có lỗi 0,1; 0,3; 0,2; 0,4 → $L_{\text{batch}} = 1{,}0 / 4 = 0{,}25$.

**(e) Trong đồ án.** Kích thước batch là **512**. Batch vừa đủ để RAM chịu được, vẫn đủ lớn để mỗi lần cập nhật ổn định.

### 2.3 Iteration (bước cập nhật)

**(a) Định nghĩa.** Một **iteration** = xử lý một batch và cập nhật trọng số một lần.

**(b) Trực giác.** Mỗi lần chấm xong 50 bài rồi chỉnh cách chấm là một iteration.

**(c) Công thức.** $\text{Số iteration / epoch} = N / B$; $\text{Tổng iteration} = \text{số epoch} \times N / B$.

**(d) Ví dụ minh hoạ.** $N = 5.120$, $B = 512$ → 10 iteration/epoch; 3 epoch → 30 iteration.

**(e) Trong đồ án.** Với batch 512, số iteration mỗi epoch tỉ lệ với số cặp huấn luyện × (1 + 8 mẫu âm) — mỗi cặp đã mua
kéo theo 8 cặp "chưa mua" (Cấp 3).

### 2.4 Hàm mất mát (*loss function*)

**(a) Định nghĩa.** Con số đo **mô hình sai bao nhiêu**. Huấn luyện chính là chỉnh tham số để con số này nhỏ đi.

**(b) Trực giác.** Như điểm trừ khi làm sai bài: sai càng xa đáp án càng bị trừ nhiều.

**(c) Công thức (dạng chung).**

$$L(\Theta) = \frac{1}{N}\sum_{k=1}^{N} \ell\big(y_k, \hat{y}_k(\Theta)\big)$$

- $y_k$: nhãn thật; $\hat{y}_k$: dự đoán; $\ell$: lỗi của một mẫu; $\Theta$: tham số.

**(d) Ví dụ minh hoạ.** Lỗi bình phương: thật 1, đoán 0,8 → $(1 - 0{,}8)^2 = 0{,}04$; thật 0, đoán 0,6 →
$0{,}36$. Trung bình $= 0{,}2$.

**(e) Trong đồ án.** Mạng nơ-ron dùng **BCE** (*binary cross-entropy*, Cấp 3); BPR-MF dùng **hàm mất mát BPR** (Cấp 3).

### 2.5 Gradient descent (hạ gradient)

**(a) Định nghĩa.** Cách cập nhật tham số: tính **đạo hàm** (gradient) của loss theo từng tham số rồi bước một bước theo
hướng **ngược** gradient để loss giảm.

**(b) Trực giác.** Đứng trên đồi trong sương mù, muốn xuống thung lũng: sờ chân xem chỗ nào dốc xuống rồi bước một bước
về phía đó, lặp lại.

**(c) Công thức.**

$$\theta \leftarrow \theta - \eta \cdot \frac{\partial L}{\partial \theta}$$

- $\theta$: một tham số; $\eta$: tốc độ học (2.7); $\partial L / \partial \theta$: độ dốc của loss theo $\theta$.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** $L(\theta) = (\theta - 3)^2$, bắt đầu $\theta = 0$, $\eta = 0{,}1$. Đạo hàm
$= 2(\theta - 3) = -6$ → $\theta = 0 - 0{,}1 \times (-6) = 0{,}6$. Lần sau đạo hàm $= -4{,}8$ → $\theta = 1{,}08$. Dần
tiến về 3 (điểm loss nhỏ nhất).

**(e) Trong đồ án.** Mọi mô hình có học (GMF, MLP, NeuMF, các bản -F, BPR-MF) đều cập nhật theo nguyên tắc này; mạng nơ-ron
dùng biến thể **Adam**.

### 2.6 Adam

**(a) Định nghĩa.** Thuật toán tối ưu, một biến thể của gradient descent: **tự điều chỉnh độ dài bước cho từng tham số**
dựa trên lịch sử gradient.

**(b) Trực giác.** Xuống đồi thông minh hơn: chỗ nào lúc nào cũng dốc một hướng thì bước dài (có "đà"); chỗ gập ghềnh
thì bước ngắn lại.

**(c) Công thức (rút gọn).**

$$m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t,\quad v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2,\quad \theta \leftarrow \theta - \eta\frac{m_t}{\sqrt{v_t}+\epsilon}$$

- $g_t$: gradient ở bước $t$; $m_t$: trung bình trượt của gradient ("đà"); $v_t$: trung bình trượt của bình phương
  gradient (độ gập ghềnh); $\beta_1, \beta_2$: hệ số nhớ; $\epsilon$: số rất nhỏ tránh chia 0.

**(d) Ví dụ minh hoạ.** Một tham số gradient luôn ≈ 2 → $m_t ≈ 2$, $\sqrt{v_t} ≈ 2$ → bước ≈ $\eta$. Tham số khác gradient
khi +2 khi −2 → $m_t ≈ 0$ → gần như không bước. Adam tự hãm tham số "lưỡng lự".

**(e) Trong đồ án.** Mạng nơ-ron dùng **Adam** với lr = **0,001**.

### 2.7 Tốc độ học (*learning rate*, lr)

**(a) Định nghĩa.** Độ lớn mỗi bước cập nhật tham số ($\eta$ trong 2.5).

**(b) Trực giác.** Bước quá dài thì nhảy qua đáy thung lũng sang sườn bên kia; bước quá ngắn thì đi mãi chưa tới.

**(c) Công thức.** Chính là $\eta$ trong $\theta \leftarrow \theta - \eta\,\partial L/\partial\theta$.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** Dùng $L = (\theta-3)^2$, $\theta = 0$: với $\eta = 1{,}0$: $\theta = 0 + 6 = 6$
(vượt qua 3, xa hơn cả lúc đầu); với $\eta = 0{,}1$: $\theta = 0{,}6$ (tiến dần); với $\eta = 0{,}001$: $\theta = 0{,}006$
(quá chậm).

**(e) Trong đồ án.** NeuMF-F chọn lr = **0,001**; BPR-MF chọn lr = **0,03**. Cả hai được chọn bằng tinh chỉnh trên tập
xác thực.

### 2.8 Weight decay và regularization

**(a) Định nghĩa.** Cộng thêm vào loss một khoản **phạt trọng số lớn**, để mô hình không dựa quá mạnh vào vài tham số.

**(b) Trực giác.** Nhắc học sinh "đừng thuộc lòng đáp án, hiểu đại khái thôi" — tránh học vẹt.

**(c) Công thức.**

$$L_{\text{tổng}} = L + \lambda\lVert\Theta\rVert^2$$

- $\lVert\Theta\rVert^2$: tổng bình phương mọi tham số; $\lambda$: mức phạt.

**(d) Ví dụ minh hoạ.** Hai tham số 3 và 4: $\lVert\Theta\rVert^2 = 9 + 16 = 25$; $\lambda = 0{,}01$ → phạt thêm 0,25.

**(e) Trong đồ án.** NeuMF-F: weight decay **1e-6** (rất nhẹ). BPR-MF: $\lambda$ = **0,001**.

### 2.9 Overfitting và underfitting

**(a) Định nghĩa.** **Overfitting** (quá khớp): mô hình học thuộc dữ liệu huấn luyện, kém trên dữ liệu mới.
**Underfitting** (chưa khớp): học chưa đủ, kém trên cả hai.

**(b) Trực giác.** Học thuộc đáp án đề cương → gặp câu hỏi đổi số là bí (overfitting). Chưa ôn gì → câu nào cũng bí
(underfitting).

**(c) Công thức (dấu hiệu).** Theo dõi hai đường: loss huấn luyện $L_{\text{train}}$ và điểm xác thực. Overfitting khi
$L_{\text{train}}$ vẫn giảm nhưng điểm xác thực **bắt đầu giảm**.

**(d) Ví dụ minh hoạ.** Epoch 1–5: điểm xác thực 0,02 → 0,033 (đang học). Epoch 6–9: 0,032 → 0,029 dù loss huấn luyện vẫn
giảm → bắt đầu quá khớp.

**(e) Trong đồ án.** Chặn quá khớp bằng **dừng sớm**, **dropout**, **weight decay**; và quan trọng nhất là **không bao giờ
chọn gì trên tập kiểm thử**.

### 2.10 Dừng sớm (*early stopping*)

**(a) Định nghĩa.** Sau mỗi epoch, chấm mô hình trên tập xác thực; nếu điểm **không tăng** thêm trong $P$ epoch liên tiếp
(*patience*) thì dừng, và giữ **epoch có điểm cao nhất**.

**(b) Trực giác.** Tập chạy: đã 5 buổi liền không cải thiện thời gian → dừng tăng cường độ, lấy thành tích tốt nhất.

**(c) Công thức.**

$$e^* = \arg\max_{e} \text{NDCG@10}_{\text{xác thực}}(e), \qquad \text{dừng khi } e - e^* \ge P$$

- $e$: số epoch; $e^*$: epoch tốt nhất; $P$: patience.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** NDCG theo epoch: 0,020 / 0,026 / 0,031 / **0,033** / 0,032 / 0,032 / 0,031 /
0,030 / 0,029. Tốt nhất ở epoch 4; với $P = 5$, sau epoch 9 (= 4 + 5) vẫn chưa vượt 0,033 → **dừng ở epoch 9**, chọn
**epoch 4**.

**(e) Trong đồ án.** Chấm **NDCG@10** trên tập xác thực, **patience = 5**, tối đa 20 epoch. Ở đánh giá cuối, số epoch tốt
nhất chọn trên xác thực của mẫu kiểm định rồi huấn luyện lại từ đầu với đúng số đó.

### 2.11 Dropout

**(a) Định nghĩa.** Trong lúc huấn luyện, **tắt ngẫu nhiên** một tỉ lệ nơ-ron ở mỗi bước; khi chấm thì bật hết.

**(b) Trực giác.** Đội bóng tập luyện mà mỗi buổi ngẫu nhiên vài người nghỉ → ai cũng phải biết đá nhiều vị trí, không
dựa vào một ngôi sao.

**(c) Công thức.** Với tỉ lệ $p$: $\tilde{h}_j = \dfrac{m_j}{1-p}\,h_j$, $m_j \sim \text{Bernoulli}(1-p)$.

- $h_j$: đầu ra nơ-ron $j$; $m_j$: 1 (giữ) hoặc 0 (tắt); chia $(1-p)$ để tổng không bị nhỏ đi.

**(d) Ví dụ minh hoạ.** $p = 0{,}5$, đầu ra [2, 4, 6, 8], mặt nạ [1, 0, 1, 0] → [4, 0, 12, 0].

**(e) Trong đồ án.** NeuMF-F chọn **dropout = 0** (tinh chỉnh thấy không cần); NeuMF chỉ dùng ID chọn **dropout 0,2**.

### 2.12 Seed

**(a) Định nghĩa.** Con số khởi đầu cho bộ sinh số ngẫu nhiên. **Cùng seed → cùng dãy số ngẫu nhiên → chạy lại ra đúng
kết quả.**

**(b) Trực giác.** Xáo bài theo một "công thức xáo" đánh số 42: ai xáo theo công thức 42 cũng ra cùng thứ tự bài.

**(c) Công thức.** Không có công thức; seed quyết định mọi bước ngẫu nhiên: khởi tạo trọng số, rút mẫu âm, thứ tự batch,
dropout.

**(d) Ví dụ minh hoạ.** Seed 1 khởi tạo trọng số [0,1; −0,3], seed 2 khởi tạo [0,4; 0,2] → hai lần huấn luyện cho kết quả
hơi khác nhau, dù cùng dữ liệu và cấu hình.

**(e) Trong đồ án.** Chạy **5 seed: 42, 2024, 2025, 2026, 3407** để biết kết quả có ổn định không. Tinh chỉnh dùng seed 42;
phân tích bóc tách và demo cũng dùng seed 42.

### 2.13 Trung bình ± độ lệch chuẩn, và vì sao có "± 0"

**(a) Định nghĩa.** Báo kết quả qua nhiều seed dưới dạng **trung bình ± độ lệch chuẩn**: trung bình cho biết mức chung,
độ lệch chuẩn cho biết kết quả **dao động** giữa các lần chạy bao nhiêu.

**(b) Trực giác.** Đo thời gian chạy 100 m 5 lần: trung bình 13,0 giây ± 0,2 → khá ổn định. Một chiếc đồng hồ đo 5 lần
cùng một vật cố định → ± 0, vì không có gì thay đổi.

**(c) Công thức.**

$$\bar{x} = \frac{1}{n}\sum_{s=1}^{n} x_s, \qquad \text{sd} = \sqrt{\frac{1}{n-1}\sum_{s=1}^{n}(x_s - \bar{x})^2}$$

- $x_s$: kết quả ở seed $s$; $n$: số seed (= 5).

**(d) Ví dụ tính tay (ví dụ minh hoạ).** NDCG 5 seed: 0,040; 0,042; 0,038; 0,041; 0,039 → $\bar{x} = 0{,}040$. Độ lệch:
0; 0,002; −0,002; 0,001; −0,001 → bình phương cộng lại 0,00001 → chia 4 → $0{,}0000025$ → căn ≈ **0,0016**.
Nếu 5 seed đều 0,031 → mọi độ lệch bằng 0 → **sd = 0**.

**(e) Trong đồ án.** Các mô hình **không có bước ngẫu nhiên** — Most Popular, MostPopular-Recent, Content, UserKNN,
ItemKNN, Hybrid-CBCF — cho **đúng một kết quả** ở mọi seed, nên ghi **± 0,00000**. Đây **không phải thiếu số liệu**. Các
mô hình có khởi tạo ngẫu nhiên và mẫu âm (mạng nơ-ron, BPR-MF, Random) mới dao động, ví dụ NeuMF-F trên H&M có trung bình
0,04003.

### 2.14 Lớp tuyến tính (*linear layer*)

**(a) Định nghĩa.** Phép biến một vector $n$ chiều thành vector $m$ chiều bằng nhân ma trận cộng vector.

**(b) Trực giác.** Như công thức tính điểm tổng kết: mỗi môn nhân một hệ số rồi cộng lại — nhưng làm cùng lúc cho nhiều
"điểm tổng kết" khác nhau.

**(c) Công thức.** $\mathbf{h} = W\mathbf{x} + \mathbf{b}$ — $\mathbf{x}$: đầu vào ($n$ chiều); $W$: ma trận $m \times n$;
$\mathbf{b}$: hệ số chệch ($m$ chiều); $\mathbf{h}$: đầu ra.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** $W = \begin{bmatrix}1 & 2\\ 0 & -1\end{bmatrix}$, $\mathbf{x} = [3, 1]$,
$\mathbf{b} = [0, 1]$ → $\mathbf{h} = [1\cdot3 + 2\cdot1,\ 0\cdot3 - 1\cdot1] + [0, 1] = [5, 0]$.

**(e) Trong đồ án.** Có ở khắp nơi: tháp MLP (64 → 32 → 16 → 8), ma trận chiếu đặc trưng $W_I$, $W_U$ (đưa vector đặc
trưng 157 chiều về 32 chiều), lớp đầu ra của NeuMF-F.

### 2.15 Hàm kích hoạt ReLU

**(a) Định nghĩa.** $\text{ReLU}(z) = \max(0, z)$: giữ số dương, biến số âm thành 0.

**(b) Trực giác.** Như van một chiều: chỉ cho dòng chảy dương đi qua. Nhờ "gập" như vậy, mạng mới học được quan hệ phức
tạp, không chỉ đường thẳng.

**(c) Công thức.** $\text{ReLU}(z) = \max(0, z)$. Không có ReLU, nhiều lớp tuyến tính chồng lên nhau vẫn chỉ tương đương
**một** lớp tuyến tính.

**(d) Ví dụ tính tay.** ReLU([−2; 0,5; 3; −0,1]) = [0; 0,5; 3; 0].

**(e) Trong đồ án.** Dùng giữa các lớp của tháp MLP trong MLP, NeuMF, MLP-F, NeuMF-F — tạo phần **tương tác phi tuyến**.

### 2.16 Sigmoid

**(a) Định nghĩa.** Hàm ép số thực bất kỳ về khoảng (0, 1), dùng như **xác suất** "khách sẽ mua".

**(b) Trực giác.** Như thanh đo độ tự tin: điểm rất âm → gần 0% ("chắc không mua"); điểm rất dương → gần 100%.

**(c) Công thức.** $\sigma(z) = \dfrac{1}{1 + e^{-z}}$; $\sigma(0) = 0{,}5$.

**(d) Ví dụ tính tay.** $\sigma(0) = 1/(1+1) = 0{,}5$; $\sigma(2) = 1/(1 + 0{,}135) ≈ 0{,}88$;
$\sigma(-2) ≈ 0{,}12$.

**(e) Trong đồ án.** Đầu ra NeuMF-F là $\hat{y} = \sigma(\cdot)$ khi huấn luyện với BCE. Nhưng khi **xếp hạng** thì dùng
logit (2.17).

### 2.17 Logit

**(a) Định nghĩa.** Giá trị $z$ **trước** khi qua sigmoid.

**(b) Trực giác.** Hai thí sinh đều được làm tròn thành điểm 10 thì không xếp được ai hơn; nhìn điểm gốc 9,96 và 9,98 thì
xếp được.

**(c) Công thức.** $\hat{y} = \sigma(z)$; vì $\sigma$ tăng đơn điệu nên **xếp theo $z$ cho cùng thứ tự với xếp theo
$\sigma(z)$** về lý thuyết.

**(d) Ví dụ minh hoạ.** $z = 20$ và $z = 25$: trên máy tính số thực 32 bit, $\sigma(20)$ và $\sigma(25)$ đều làm tròn
thành **1,0** → hai món bằng điểm giả. Xếp theo $z$: 25 > 20, phân biệt được.

**(e) Trong đồ án.** Đồ án **xếp hạng theo logit** vì sigmoid ở độ chính xác float32 bão hoà thành 1,0, tạo ra nhiều món
bằng điểm giả và làm sai thứ hạng.

### Câu hỏi tự kiểm tra — Cấp 2

1. **1 epoch là gì? Batch 512 nghĩa là gì?** — 1 lượt qua toàn bộ dữ liệu huấn luyện; mỗi lần cập nhật dùng 512 mẫu.
2. **Dừng sớm với patience = 5 hoạt động thế nào?** — Chấm NDCG@10 xác thực sau mỗi epoch; 5 epoch liền không vượt điểm
   tốt nhất thì dừng, lấy epoch tốt nhất.
3. **Vì sao Most Popular có "± 0"?** — Không có bước ngẫu nhiên, 5 seed cho cùng một kết quả.
4. **Vì sao xếp hạng theo logit chứ không theo sigmoid?** — Sigmoid float32 bão hoà thành 1,0 khiến nhiều món bằng điểm
   giả; logit vẫn phân biệt được.
5. **Kể ba cách đồ án chống quá khớp.** — Dừng sớm, dropout/weight decay, và không chọn gì trên tập kiểm thử.

---

## Cấp 3 — Hệ khuyến nghị: từ cổ điển đến học sâu

### 3.1 Random và Most Popular

**(a) Định nghĩa.** **Random**: chấm điểm ngẫu nhiên — mức tệ nhất có thể (*cận dưới*). **Most Popular**: điểm của một
sản phẩm = số lượt nó được mua; mọi khách nhận **cùng một danh sách**.

**(b) Trực giác.** Random như nhắm mắt chỉ vào kệ hàng. Most Popular như kệ "Bán chạy nhất" đặt ở cửa — không cá nhân hoá
nhưng thường khá hiệu quả.

**(c) Công thức.** Most Popular: $\hat{y}_{ui} = \lvert\{v : y_{vi} = 1\}\rvert$ — số khách $v$ đã mua $i$ (không phụ
thuộc $u$).

**(d) Ví dụ minh hoạ.** Áo A có 50 lượt mua, quần B 30, váy C 10 → mọi khách nhận thứ tự A, B, C (trừ món đã mua).

**(e) Trong đồ án.** Random là cận dưới (NDCG@10 = **0,00098** trên H&M). Most Popular đạt **0,02184** — gấp hơn 20 lần
ngẫu nhiên, cho thấy độ phổ biến là tín hiệu mạnh. Độ phủ top-10 của Most Popular chỉ **0,3%** vì ai cũng nhận cùng danh
sách. Khách mới trong demo nhận danh sách này.

### 3.2 MostPopular-Recent

**(a) Định nghĩa.** Như Most Popular nhưng chỉ đếm lượt mua trong **W ngày gần nhất** trước mốc dự đoán.

**(b) Trực giác.** Thời trang đổi theo mùa: áo khoác bán chạy mùa đông năm ngoái không còn hợp mùa hè. Kệ "Đang hot tuần
này" hữu ích hơn "Bán chạy mọi thời đại".

**(c) Công thức.** $\hat{y}_{ui} = \text{số giao dịch của } i \text{ trong } [\tau - W, \tau)$.

**(d) Ví dụ minh hoạ.** Áo A: 100 lượt cả năm nhưng 2 lượt tháng qua; áo B: 20 lượt cả năm, 15 lượt tháng qua. Most
Popular xếp A trước; MostPopular-Recent (W = 30 ngày) xếp B trước.

**(e) Trong đồ án.** Chọn **W = 28 ngày**. Trên H&M đạt **0,02760**, cao hơn Most Popular (0,02184) — đúng với đặc trưng
mùa vụ của thời trang. Ý tưởng "độ mới" này cũng có trong đặc trưng thời gian của NeuMF-F.

### 3.3 Content (dựa trên nội dung)

**(a) Định nghĩa.** Mỗi sản phẩm có một **vector nội dung** (từ thuộc tính và mô tả). Hồ sơ của khách là trung bình vector
các món đã mua; gợi ý món có vector **giống hồ sơ** nhất.

**(b) Trực giác.** Bạn mua toàn áo thun cotton màu đen → hồ sơ của bạn "nghiêng về áo thun đen" → gợi ý thêm áo thun tối
màu.

**(c) Công thức.**

$$\mathbf{c}_u = \frac{\sum_{j \in H_u} w_j\,\mathbf{v}_j}{\sum_{j} w_j}, \quad w_j = 0{,}5^{\Delta t_j / T_{1/2}}, \qquad \hat{y}_{ui} = \cos(\mathbf{c}_u, \mathbf{v}_i)$$

- $H_u$: các món khách đã mua; $\mathbf{v}_j$: vector nội dung món $j$; $\Delta t_j$: số ngày từ lúc mua đến mốc;
  $T_{1/2}$: chu kỳ bán rã; $w_j$: trọng số — món mua càng lâu càng nhẹ.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** $T_{1/2} = 30$ ngày. Món mua cách 0 ngày: $w = 1$; cách 30 ngày: $w = 0{,}5$;
cách 60 ngày: $w = 0{,}25$.

**(e) Trong đồ án.** Chọn **chu kỳ bán rã 30 ngày**. Content rất yếu trên H&M (**0,00506**) — chỉ hơn Random — vì gu thời
trang không chỉ là "giống món đã mua" (mua áo rồi thường mua quần, không mua thêm áo y hệt). Content là một thành phần của
Hybrid-CBCF.

### 3.4 Độ tương đồng cosine và hệ số co

**(a) Định nghĩa.** **Cosine** đo hai vector **cùng hướng** đến đâu: 1 = giống hệt hướng, 0 = không liên quan. **Hệ số co**
$h$ cộng vào mẫu số để giảm điểm các cặp có quá ít dữ liệu chung.

**(b) Trực giác.** Hai sản phẩm được mua bởi gần như cùng một nhóm khách → rất giống nhau. Nhưng hai món chỉ trùng nhau
đúng 1 người mua thì có thể chỉ là trùng hợp → co điểm lại.

**(c) Công thức.**

$$\cos(\mathbf{a},\mathbf{b}) = \frac{\mathbf{a}\cdot\mathbf{b}}{\lVert\mathbf{a}\rVert\,\lVert\mathbf{b}\rVert + h}$$

- $\mathbf{a}\cdot\mathbf{b}$: tích vô hướng (với vector 0/1 = số khách chung); $\lVert\cdot\rVert$: độ dài vector; $h$:
  hệ số co.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** Áo A được khách {1, 2, 3} mua, áo B được {2, 3, 4} mua. Tích vô hướng = 2 (khách
2, 3); độ dài mỗi vector = √3. Với $h = 0$: cos = 2/3 ≈ **0,67**. Với $h = 50$: cos = 2/(3 + 50) ≈ **0,04** — co mạnh vì
chỉ có 3 người mua.

**(e) Trong đồ án.** ItemKNN chọn **h = 50**, UserKNN **h = 0**. Cosine cũng dùng trong Content (so hồ sơ khách với sản
phẩm).

### 3.5 ItemKNN và UserKNN (lọc cộng tác láng giềng)

**(a) Định nghĩa.** **ItemKNN**: "món hay được mua cùng món bạn đã mua". **UserKNN**: "người giống bạn đã mua gì". Chỉ giữ
**k láng giềng** giống nhất.

**(b) Trực giác.** ItemKNN: "khách mua quần jean này cũng mua thắt lưng kia". UserKNN: tìm những người có giỏ hàng giống
bạn, xem họ mua gì mà bạn chưa mua.

**(c) Công thức (ItemKNN).**

$$\hat{y}_{ui} = \sum_{j \in H_u \cap N_k(i)} \text{sim}(i, j)$$

- $H_u$: món khách $u$ đã mua; $N_k(i)$: $k$ món giống $i$ nhất; $\text{sim}$: cosine có hệ số co.

UserKNN đối xứng: $\hat{y}_{ui} = \sum_{v \in N_k(u),\, y_{vi}=1} \text{sim}(u, v)$.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** Khách đã mua jean và áo thun. Thắt lưng giống jean 0,6, giống áo thun 0,1 → điểm
0,7. Váy giống jean 0,05, giống áo thun 0,2 → 0,25. Gợi ý thắt lưng trước.

**(e) Trong đồ án.** ItemKNN: **k = 100, h = 50**, NDCG@10 = **0,02860** (H&M). UserKNN: **k = 200, h = 0**, **0,03114**
— mạnh nhất trong nhóm truyền thống đơn lẻ. Demo: thẻ "Sản phẩm tương tự" là láng giềng ItemKNN; "Khách có gu giống" là
láng giềng UserKNN. Độ phủ top-10: ItemKNN **20,4%**, UserKNN **5,7%**.

### 3.6 Embedding (vector nhúng)

**(a) Định nghĩa.** Một **bảng tra**: mỗi ID (khách, sản phẩm, hoặc giá trị thuộc tính) ứng với một vector $d$ số thực,
**do mô hình tự học**.

**(b) Trực giác.** Như toạ độ trên bản đồ "gu thời trang": người thích đồ thể thao nằm gần áo thể thao; mô hình tự vẽ bản
đồ này từ lịch sử mua.

**(c) Công thức.** $\mathbf{e}_i = E[i,:]$ — hàng thứ $i$ của ma trận $E$ kích thước (số ID) × $d$.

**(d) Ví dụ minh hoạ ($d$ = 4).**

| ID | Vector |
|---|---|
| 0 (quần jean) | [0,8; −0,1; 0,3; 0,0] |
| 1 (áo thun) | [0,2; 0,9; −0,4; 0,1] |

Ban đầu ngẫu nhiên; huấn luyện đẩy vector khách lại gần vector các món khách mua.

**(e) Trong đồ án.** Embedding ID của khách và sản phẩm có **d = 32** (NeuMF-F); mỗi giá trị thuộc tính có embedding **8
chiều**. Embedding là "nguyên liệu" của mọi mô hình MF và mạng nơ-ron.

### 3.7 Nhân tử hoá ma trận (MF)

**(a) Định nghĩa.** Mỗi khách và mỗi sản phẩm có một vector ẩn; điểm = **tích vô hướng** của hai vector.

**(b) Trực giác.** Mỗi chiều như một "gu" ẩn (thích đồ tối màu, thích đồ thể thao…). Khách thích gu nào, sản phẩm mang gu
đó → điểm cao. Không ai đặt tên các chiều; mô hình tự tìm.

**(c) Công thức.** $\hat{y}_{ui} = \mathbf{p}_u^\top\mathbf{q}_i = \sum_{k=1}^{d} p_{uk}\,q_{ik}$ — $\mathbf{p}_u$: vector
khách; $\mathbf{q}_i$: vector sản phẩm; $d$: số chiều.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** $\mathbf{p}_u = [1, 0{,}5]$ (rất thích đồ tối, hơi thích thể thao);
$\mathbf{q}_{\text{áo đen}} = [0{,}9, 0{,}1]$ → $0{,}9 + 0{,}05 = 0{,}95$; $\mathbf{q}_{\text{áo trắng thể thao}} = [0, 0{,}8]$
→ $0{,}4$. Gợi ý áo đen trước.

**(e) Trong đồ án.** MF là nhánh "nhân tử hoá ma trận" trong tên đề tài; xuất hiện dưới dạng **BPR-MF** và nhánh **GMF**.

### 3.8 BPR-MF

**(a) Định nghĩa.** MF được huấn luyện để **xếp đúng thứ tự**: món khách đã mua phải có điểm **cao hơn** món chưa mua
(Rendle et al., 2009).

**(b) Trực giác.** Không cần biết chính xác khách thích áo A bao nhiêu, chỉ cần biết "thích A hơn B". Hợp với phản hồi
ngầm.

**(c) Công thức.**

$$L_{\text{BPR}} = -\sum_{(u,i,j)} \ln\sigma(\hat{y}_{ui} - \hat{y}_{uj}) + \lambda\lVert\Theta\rVert^2$$

- $(u, i, j)$: bộ ba khách, món đã mua $i$, món chưa mua $j$; $\sigma$: sigmoid; $\lambda$: mức phạt.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** $\hat{y}_{ui} = 2$, $\hat{y}_{uj} = 0$: $\sigma(2) ≈ 0{,}88$ → $-\ln 0{,}88 ≈
0{,}13$ (xếp đúng, phạt nhẹ). Đảo lại $\hat{y}_{ui} = 0$, $\hat{y}_{uj} = 2$: $\sigma(-2) ≈ 0{,}12$ → $-\ln 0{,}12 ≈ 2{,}13$
(phạt nặng).

**(e) Trong đồ án.** Chọn **d = 128, lr = 0,03, λ = 0,001, 20 epoch**. H&M: **0,02661** — kém NeuMF-F rõ. Hybrid-CBCF cũng
dùng tiêu chí kiểu BPR để học trọng số kết hợp.

### 3.9 GMF (*Generalized Matrix Factorization*)

**(a) Định nghĩa.** Nhân **từng phần tử** vector khách và sản phẩm, rồi qua một lớp tuyến tính để ra điểm.

**(b) Trực giác.** MF cộng mọi chiều "gu" với trọng số bằng nhau; GMF cho phép chiều "màu sắc" quan trọng hơn chiều "chất
liệu" nếu dữ liệu cho thấy vậy.

**(c) Công thức.** $\phi^G = \mathbf{p}_u \odot \mathbf{q}_i$, $\hat{y} = \sigma(\mathbf{h}^\top\phi^G)$ — $\odot$: nhân
từng phần tử; $\mathbf{h}$: trọng số học được cho từng chiều. Nếu $\mathbf{h}$ toàn 1 thì GMF = MF.

**(d) Ví dụ tính tay.** [1, 2, 3] ⊙ [4, 0, −1] = [4, 0, −3]. Với $\mathbf{h} = [1,1,1]$: tổng = 1 (= tích vô hướng). Với
$\mathbf{h} = [0{,}5; 1; 2]$: $2 + 0 - 6 = -4$.

**(e) Trong đồ án.** GMF chỉ dùng ID: **0,02695** (H&M). GMF-F (thêm đặc trưng): **0,03902** — ngang NeuMF-F. GMF là nhánh
tuyến tính của NeuMF.

### 3.10 MLP (*Multi-Layer Perceptron*)

**(a) Định nghĩa.** **Nối** vector khách và sản phẩm thành một vector dài, đưa qua **tháp** nhiều lớp tuyến tính + ReLU
nhỏ dần.

**(b) Trực giác.** GMF chỉ bắt được kiểu "cùng gu thì hợp"; MLP học được quan hệ phức tạp hơn, ví dụ "khách trẻ thích đồ
thể thao, **nhưng** chỉ khi đang mùa hè".

**(c) Công thức.** $\mathbf{z}_0 = [\mathbf{p}_u;\mathbf{q}_i]$, $\mathbf{z}_\ell = \text{ReLU}(W_\ell\mathbf{z}_{\ell-1} +
\mathbf{b}_\ell)$, $\phi^M = \mathbf{z}_L$ — $[\cdot;\cdot]$: nối vector; $\ell$: chỉ số lớp.

**(d) Ví dụ minh hoạ.** $\mathbf{p}_u$ 32 chiều nối $\mathbf{q}_i$ 32 chiều → 64 chiều → lớp 1 ra 32 → lớp 2 ra 16 → lớp
3 ra 8.

**(e) Trong đồ án.** Tháp **64 → 32 → 16 → 8** (với d = 32). MLP chỉ dùng ID: **0,02373**; MLP-F: **0,03480**. MLP là
nhánh phi tuyến của NeuMF.

### 3.11 NeuMF

**(a) Định nghĩa.** Chạy **song song** GMF và MLP, **nối** đầu ra hai nhánh, qua một lớp tuyến tính → điểm (He et al.,
2017).

**(b) Trực giác.** Hai chuyên gia: một người giỏi "khớp gu đơn giản" (GMF), một người giỏi "suy luận phức tạp" (MLP); ghép
ý kiến hai người thành một quyết định.

**(c) Công thức.**

$$\hat{y}_{ui} = \sigma\big(\mathbf{h}^\top[\phi^G;\phi^M]\big)$$

- $\phi^G$: đầu ra GMF (32 chiều khi d = 32); $\phi^M$: đầu ra tháp MLP (8 chiều); $\mathbf{h}$: trọng số lớp cuối.

**(d) Ví dụ minh hoạ.** $\phi^G = [0{,}5; -0{,}2]$, $\phi^M = [1{,}0]$, $\mathbf{h} = [1; 1; 2]$ → logit $= 0{,}5 - 0{,}2 +
2 = 2{,}3$ → $\sigma(2{,}3) ≈ 0{,}91$.

**(e) Trong đồ án.** NeuMF chỉ dùng ID (cấu hình: d = 64, 4 mẫu âm, dropout 0,2): **0,02783** trên H&M. Đây là **hợp nhất
sớm** (Cấp 4). Mô hình đề xuất NeuMF-F giữ đúng khung này và thêm đặc trưng → **+43,8%** trên H&M.

### 3.12 Hàm mất mát BCE (*binary cross-entropy*)

**(a) Định nghĩa.** Loss cho bài toán có/không: phạt mạnh khi mô hình **tự tin mà sai**.

**(b) Trực giác.** Khách đã mua mà mô hình nói "chỉ 10% khả năng mua" → sai nặng, phạt nhiều. Nói "90%" → gần đúng, phạt
ít.

**(c) Công thức.**

$$L = -\big[y\ln\sigma(z) + (1-y)\ln(1-\sigma(z))\big]$$

- $y$: 1 (đã mua) hoặc 0 (mẫu âm); $z$: logit; $\sigma(z)$: xác suất dự đoán.

**(d) Ví dụ tính tay.** $y = 1$: $\sigma(z) = 0{,}9$ → $L = -\ln 0{,}9 ≈ 0{,}105$; $\sigma(z) = 0{,}1$ → $L = -\ln 0{,}1 ≈
2{,}30$. $y = 0$, $\sigma(z) = 0{,}2$ → $L = -\ln 0{,}8 ≈ 0{,}22$.

**(e) Trong đồ án.** Mọi mạng nơ-ron (GMF, MLP, NeuMF và bản -F) dùng BCE, cài bằng `nn.BCEWithLogitsLoss` (nhận thẳng
logit, ổn định số học hơn tự tính sigmoid).

### 3.13 Mẫu âm (*negative sampling*)

**(a) Định nghĩa.** Vì chỉ có ví dụ "đã mua" (y = 1), ta **tự rút** một số món khách chưa mua làm ví dụ y = 0.

**(b) Trực giác.** Dạy trẻ nhận biết con mèo: không chỉ cho xem ảnh mèo, mà còn cho xem vài ảnh chó, chim và nói "không
phải mèo".

**(c) Công thức.** Với mỗi cặp dương $(u, i, t)$: rút $n$ món $j_1, \dots, j_n$ từ $\{j : y_{uj} = 0,\ j \text{ đã ra mắt
tại } t\}$, gán $y = 0$. Tỉ lệ dương : âm = $1 : n$.

**(d) Ví dụ minh hoạ.** Khách mua áo A ngày 10/05; $n = 3$ → rút 3 món khách chưa mua và đã có bán trước 10/05, ví dụ
quần B, váy C, giày D → 4 mẫu huấn luyện: (A, 1), (B, 0), (C, 0), (D, 0).

**(e) Trong đồ án.** **8 mẫu âm** mỗi cặp dương (tỉ lệ 1 : 8), chỉ trong các món **đã ra mắt** tại ngày mua (để không lộ
tương lai), trừ món khách đã mua, và **rút lại mới mỗi epoch**. Rút ngẫu nhiên nên kết quả mạng nơ-ron thay đổi theo seed.

### 3.14 Cấu hình đã chọn của NeuMF-F

**(a) Định nghĩa.** Bộ siêu tham số tốt nhất trên tập xác thực của mẫu phát triển.

**(b) Trực giác.** Sau khi nướng thử 6 mẻ, chọn được nhiệt độ và thời gian cho bánh ngon nhất.

**(c) Tổng hợp.**

| Siêu tham số | Giá trị |
|---|---|
| Số chiều embedding d | 32 |
| Tốc độ học lr | 0,001 (Adam) |
| Mẫu âm mỗi cặp dương | 8 |
| Weight decay | 1e-6 |
| Dropout | 0 |
| Bỏ ID ngẫu nhiên ρ | 0 |
| Batch / epoch tối đa / patience | 512 / 20 / 5 |

**(d) Ví dụ minh hoạ.** Thử d ∈ {16, 32, 64}: d = 32 cho NDCG xác thực cao nhất → chọn 32.

**(e) Trong đồ án.** Mỗi mô hình thử **6 cấu hình** (cùng ngân sách) → tổng **76 cấu hình, 4,7 giờ**. Amazon Beauty dùng lại
**nguyên** cấu hình chọn trên H&M.

### Câu hỏi tự kiểm tra — Cấp 3

1. **GMF khác MF ở đâu?** — GMF nhân từng phần tử rồi qua lớp tuyến tính có trọng số học được; MF cộng đều (tích vô hướng).
2. **Vì sao MostPopular-Recent hơn Most Popular trên H&M?** — Thời trang theo mùa; đếm 28 ngày gần nhất phản ánh xu hướng
   hiện tại (0,02760 so với 0,02184).
3. **Hệ số co dùng để làm gì?** — Hạ độ tương đồng của cặp có quá ít khách chung, tránh tương đồng "ăn may".
4. **Mẫu âm của đồ án rút thế nào và vì sao chỉ trong món đã ra mắt?** — 8 món chưa mua mỗi cặp dương, rút lại mỗi epoch;
   chỉ món đã có bán tại ngày đó để không dùng thông tin tương lai.
5. **BCE phạt nặng khi nào?** — Khi mô hình tự tin mà sai, ví dụ món đã mua nhưng xác suất dự đoán chỉ 0,1 (L ≈ 2,30).

---

## Cấp 4 — Mô hình đề xuất NeuMF-F và đặc trưng

### 4.1 Công thức NeuMF-F

**(a) Định nghĩa.** NeuMF-F giữ nguyên khung NeuMF (GMF + MLP, hợp nhất sớm), nhưng vector của khách và sản phẩm **không
chỉ là embedding ID** mà còn **cộng thêm đặc trưng** đã chiếu về cùng số chiều.

**(b) Trực giác.** NeuMF chỉ nhớ "mã khách 123 hay mua mã sản phẩm 456". NeuMF-F còn biết "456 là áo thun đen, mô tả
'cotton, form rộng', đang bán chạy tuần này" — nên đoán tốt hơn cả với món ít người mua.

**(c) Công thức.**

$$\mathbf{p}_u = \mathbf{e}^{\text{ID}}_u + W_U\,\mathbf{x}_u(t), \qquad \mathbf{q}_i = m_i\,\mathbf{e}^{\text{ID}}_i + W_I\,\mathbf{x}_i(t)$$

- $\mathbf{e}^{\text{ID}}_u$, $\mathbf{e}^{\text{ID}}_i$: embedding ID (d = 32 chiều).
- $\mathbf{x}_u(t)$, $\mathbf{x}_i(t)$: vector đặc trưng của khách, sản phẩm **tại ngày $t$** (4.3, 4.4).
- $W_U$, $W_I$: ma trận chiếu học được, đưa đặc trưng về 32 chiều; mỗi nhánh GMF, MLP có ma trận riêng.
- $m_i$: công tắc bỏ ID ngẫu nhiên (4.2).
- Sau đó $\mathbf{p}_u$, $\mathbf{q}_i$ đi qua GMF và MLP y như NeuMF (Cấp 3.11).

**(d) Ví dụ tính tay (ví dụ minh hoạ, d = 2).** $\mathbf{e}^{\text{ID}}_i = [0{,}1; 0{,}0]$ (sản phẩm ít người mua, vector
ID gần 0). $\mathbf{x}_i = [1; 0; 1]$, $W_I = \begin{bmatrix}0{,}5 & 0 & 0{,}3\\ 0 & 0{,}2 & 0{,}4\end{bmatrix}$ →
$W_I\mathbf{x}_i = [0{,}8; 0{,}4]$ → $\mathbf{q}_i = [0{,}9; 0{,}4]$. Phần đặc trưng "gánh" biểu diễn khi ID còn yếu.

**(e) Trong đồ án.** Đây là **mô hình đề xuất**. Vì sao **cộng** chứ không thay ID: sản phẩm mua nhiều thì embedding ID học
tốt; sản phẩm ít người mua thì phần đặc trưng bù vào. Kết quả: NeuMF-F hơn NeuMF chỉ dùng ID **+43,8%** (H&M) và **+65,7%**
(Amazon), đều có ý nghĩa thống kê.

### 4.2 Bỏ ID ngẫu nhiên (ρ)

**(a) Định nghĩa.** Khi huấn luyện, **ngẫu nhiên giấu** embedding ID của sản phẩm với xác suất ρ, buộc mô hình dự đoán chỉ
bằng đặc trưng (ý tưởng từ DropoutNet).

**(b) Trực giác.** Thỉnh thoảng che tên sản phẩm, chỉ cho xem mô tả, để người bán học cách đoán dựa vào mô tả — hữu ích
khi gặp hàng mới chưa có tiếng.

**(c) Công thức.** $m_i \sim \text{Bernoulli}(1-\rho)$ khi huấn luyện; $m_i = 1$ khi chấm. $\rho$ là siêu tham số.

**(d) Ví dụ minh hoạ.** ρ = 0,25: trong 4 lần gặp một sản phẩm, trung bình 1 lần ID bị giấu ($m_i = 0$, $\mathbf{q}_i$ chỉ
còn $W_I\mathbf{x}_i$).

**(e) Trong đồ án.** Lưới thử ρ ∈ {0; 0,25; 0,5}. **NeuMF-F chọn ρ = 0** (không giấu), **GMF-F chọn ρ = 0,25**.

### 4.3 Vector đặc trưng sản phẩm $\mathbf{x}_i$ — vì sao 157 và 109 chiều

**(a) Định nghĩa.** Vector mô tả một sản phẩm, ghép từ **ba phần**: thuộc tính danh mục, văn bản, thời gian.

**(b) Trực giác.** Như "hồ sơ" sản phẩm: nó là loại gì, màu gì (thuộc tính); mô tả nói gì (văn bản); đang bán chạy hay đã
cũ (thời gian).

**(c) Công thức.**

$$d_I = \underbrace{n_{\text{thuộc tính}} \times 8}_{\text{thuộc tính}} + \underbrace{64}_{\text{văn bản}} + \underbrace{5}_{\text{thời gian}}$$

| Phần | Cách tạo | H&M | Amazon Beauty |
|---|---|---|---|
| Thuộc tính danh mục | Mỗi thuộc tính một embedding **8 chiều**, nối lại | 11 × 8 = **88** | 5 × 8 = **40** |
| Văn bản | TF-IDF → SVD → chuẩn hoá L2 | **64** | **64** |
| Thời gian tại t | Bán trong 7, 28, 91 ngày trước t; tuổi sản phẩm; cờ "chưa từng bán" | **5** | **5** |
| **Tổng $d_I$** | | **157** | **109** |

- **Thuộc tính (88 / 40):** mỗi thuộc tính là chữ/mã (ví dụ màu "Đen"), mô hình không tính trực tiếp được trên chữ, nên mỗi
  thuộc tính có một bảng embedding riêng; mỗi giá trị ↔ vector 8 số học được. 11 thuộc tính → 11 vector 8 chiều → nối lại
  88 chiều.
  - 11 thuộc tính H&M: loại sản phẩm, nhóm sản phẩm, hoạ tiết, nhóm màu, độ đậm màu, màu chủ đạo, bộ phận, mã chỉ mục, nhóm
    chỉ mục, khu, nhóm may mặc.
  - 5 thuộc tính Amazon: thương hiệu, danh mục cấp 1, 2, 3, nhóm giá (8 nhóm, 0 = không có giá).
- **Văn bản (64):** xem 4.6–4.8.
- **Thời gian (5):** 3 số bán trong 7/28/91 ngày + tuổi sản phẩm + cờ "chưa từng bán" = 5. Số đếm mã hoá
  $\log(1 + x)/10$; cờ là 0/1. Amazon dùng **số đánh giá** thay doanh số.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** Một áo bán 20 lượt trong 7 ngày qua: $\log(1 + 20)/10 = \log 21 / 10 ≈ 3{,}04/10
= 0{,}304$. Áo bán 200 lượt: $\log 201/10 ≈ 0{,}530$ — gấp 10 lần lượt bán nhưng chỉ ~1,7 lần giá trị, nhờ log nén các số
lớn.

**(e) Trong đồ án.** 157 (H&M) và 109 (Amazon) khác nhau **chỉ ở phần thuộc tính** (11 so với 5 thuộc tính). Vector này được
**chiếu** bởi $W_I$ về 32 chiều rồi cộng vào embedding ID. Mọi đặc trưng tại ngày $t$ **chỉ dùng dữ liệu trước $t$**.

### 4.4 Vector đặc trưng khách $\mathbf{x}_u$

**(a) Định nghĩa.** Vector mô tả khách: thông tin tĩnh và đặc trưng thời gian.

**(b) Trực giác.** Khách 25 tuổi, là hội viên, nhận tin thường xuyên, vừa mua tuần trước, đã mua 40 món — tất cả giúp đoán
gu và mức độ tích cực mua sắm.

**(c) Công thức.**

$$d_U^{\text{H\&M}} = 5 \times 8 + 2 = 42, \qquad d_U^{\text{Amazon}} = 2$$

- 5 thuộc tính H&M: nhóm tuổi, trạng thái hội viên, tần suất nhận tin, FN, Active — mỗi cái embedding 8 chiều.
- 2 đặc trưng thời gian: số ngày từ lần mua gần nhất, số cặp đã mua.

**(d) Ví dụ minh hoạ.** Khách mua lần gần nhất cách 9 ngày: $\log(1+9)/10 ≈ 0{,}23$; đã mua 99 cặp: $\log 100/10 ≈ 0{,}46$.

**(e) Trong đồ án.** Amazon **không có thông tin khách**, nên nhánh khách chỉ còn 2 chiều thời gian. Trên H&M, bỏ thông tin
khách làm NDCG@10 giảm **10,3%** (ablation, Cấp 5).

### 4.5 Đặc trưng theo thời điểm (không lộ tương lai)

**(a) Định nghĩa.** Đặc trưng thời gian luôn tính **tại một ngày cụ thể** và chỉ dùng dữ liệu **trước** ngày đó.

**(b) Trực giác.** Hôm nay dự đoán thì chỉ được biết doanh số tính đến hôm qua — không được "nhìn trộm" doanh số tuần sau.

**(c) Công thức.** $x_i(t) = g\big(\{\text{giao dịch của } i \text{ có ngày} < t\}\big)$. Khi huấn luyện, mỗi cặp dương mang
ngày mua đầu của nó làm $t$; khi chấm, $t = \tau$ (mốc).

**(d) Ví dụ minh hoạ.** Cặp mua ngày 10/05: doanh số 7 ngày = giao dịch 03/05–09/05. Nếu lỡ tính cả 10/05–16/05 thì mô hình
"biết trước" món đó sắp hot → điểm đẹp giả.

**(e) Trong đồ án.** Có **test tự động** kiểm tra điều này. Đặc trưng thời gian là nhóm **quan trọng nhất**: bỏ đi làm
NDCG@10 giảm **42,3%** trên H&M và **31,6%** trên Amazon.

### 4.6 TF-IDF

**(a) Định nghĩa.** Biến một đoạn văn thành vector, mỗi chiều là một từ (hoặc cụm 2 từ). Trọng số cao khi từ xuất hiện
**nhiều trong đoạn này** nhưng **hiếm trong các đoạn khác**.

**(b) Trực giác.** Từ "the", "and" xuất hiện ở mọi mô tả → vô ích. Từ "denim", "push-up" chỉ có ở một số sản phẩm → nói lên
rất nhiều về sản phẩm.

**(c) Công thức.**

$$\text{tfidf}(w, d) = \text{tf}(w, d) \times \text{idf}(w), \qquad \text{idf}(w) \approx \log\frac{N}{\text{df}(w)}$$

- $\text{tf}(w, d)$: số lần từ $w$ xuất hiện trong mô tả $d$; $N$: tổng số mô tả; $\text{df}(w)$: số mô tả chứa $w$.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** $N = 1.000$ mô tả. "denim" có trong 10 mô tả: idf $= \log(1.000/10) = \log 100 ≈
4{,}6$. "shirt" có trong 500: idf $= \log 2 ≈ 0{,}69$. Một mô tả có "denim" 2 lần → tf-idf ≈ 9,2; có "shirt" 2 lần → ≈ 1,4.

**(e) Trong đồ án.** Dùng tên + mô tả sản phẩm; từ đơn và cặp từ; bỏ từ dừng; tối đa **30.000 từ**; mỗi từ phải có ở **≥ 3
sản phẩm**.

### 4.7 SVD cắt cụt (*truncated SVD*)

**(a) Định nghĩa.** Nén vector rất dài và thưa (30.000 chiều, gần như toàn 0) xuống ít chiều, giữ lại phần thông tin lớn
nhất (cùng ý tưởng với LSA).

**(b) Trực giác.** Các từ hay đi cùng nhau ("jeans", "denim", "skinny") được gộp vào cùng một "chủ đề". Thay vì 30.000 ô cho
30.000 từ, chỉ cần 64 ô cho 64 chủ đề.

**(c) Công thức.** $X \approx U_k\Sigma_k V_k^\top$; vector mới của mô tả $= U_k\Sigma_k$ (mỗi hàng $k$ chiều).

- $X$: ma trận TF-IDF (sản phẩm × từ); $k$: số chiều giữ lại; $\Sigma_k$: $k$ giá trị kỳ dị lớn nhất (độ quan trọng của
  từng "chủ đề").

**(d) Ví dụ minh hoạ.** Ba từ "jeans", "denim", "skinny" luôn đi cùng nhau → SVD gộp thành **một** chiều "đồ jean". Mô tả có
2 trong 3 từ này vẫn có giá trị cao ở chiều đó.

**(e) Trong đồ án.** Giữ **k = 64** chiều. Tính **một lần** trên toàn danh mục, **không dùng dữ liệu mua** và không học
trong huấn luyện (khác embedding thuộc tính là thứ học được).

### 4.8 Chuẩn hoá L2

**(a) Định nghĩa.** Chia vector cho độ dài của nó để mọi vector có độ dài bằng 1.

**(b) Trực giác.** Mô tả dài 200 từ và mô tả ngắn 20 từ về cùng một kiểu áo phải được coi là giống nhau — chỉ quan tâm
**hướng**, không quan tâm độ dài.

**(c) Công thức.** $\hat{\mathbf{v}} = \mathbf{v} / \lVert\mathbf{v}\rVert_2$, $\lVert\mathbf{v}\rVert_2 =
\sqrt{\sum_k v_k^2}$.

**(d) Ví dụ tính tay.** $\mathbf{v} = [3, 4]$ → độ dài 5 → $\hat{\mathbf{v}} = [0{,}6; 0{,}8]$.

**(e) Trong đồ án.** Áp dụng cho vector văn bản 64 chiều sau SVD. Khi gộp theo mẫu thiết kế, vector văn bản là trung bình
các biến thể màu rồi chuẩn hoá L2 lại.

### 4.9 Hợp nhất sớm và hợp nhất muộn (*early / late fusion*)

**(a) Định nghĩa.**

| | Hợp nhất sớm | Hợp nhất muộn |
|---|---|---|
| Cách làm | Nối biểu diễn hai nhánh, **một** mô hình học **chung** | Hai mô hình học **riêng**, cuối cùng trộn **điểm** |
| Mô hình | NeuMF, NeuMF-F | LateFusion-F |

**(b) Trực giác.** Hợp nhất sớm: hai chuyên gia **ngồi chung bàn**, bàn bạc rồi ra một kết luận. Hợp nhất muộn: hai chuyên
gia **làm riêng**, mỗi người chấm điểm, rồi lấy điểm trung bình có trọng số.

**(c) Công thức (hợp nhất muộn).**

$$s_{\text{LF}} = w\cdot\text{minmax}(s_{\text{GMF-F}}) + (1-w)\cdot\text{minmax}(s_{\text{MLP-F}}), \quad w = 0{,}4$$

- $s_{\text{GMF-F}}$, $s_{\text{MLP-F}}$: điểm của hai mô hình huấn luyện riêng; $w$: trọng số của GMF-F; minmax: 4.10.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** Một món sau min–max: GMF-F = 0,5, MLP-F = 1,0 → $s = 0{,}4 \times 0{,}5 + 0{,}6
\times 1{,}0 = 0{,}8$.

**(e) Trong đồ án.** Theo luận án của GVHD, NeuMF/NeuMF-F là hợp nhất sớm; LateFusion-F là hợp nhất muộn của **đúng hai
nhánh** GMF-F và MLP-F. Kết quả: **LateFusion-F cao nhất trên cả hai bộ** (H&M 0,04093; Amazon 0,03747). Trên H&M
LateFusion-F **ngang** NeuMF-F (chênh 2,2%, dưới ngưỡng 5%); trên Amazon LateFusion-F **tốt hơn** có ý nghĩa (NeuMF-F thấp
hơn 12,5%). Đổi lại, LateFusion-F tốn gấp đôi thời gian huấn luyện: **30,1 phút** so với **15,2 phút** mỗi seed (H&M).

### 4.10 Chuẩn hoá min–max

**(a) Định nghĩa.** Đưa một dãy điểm về khoảng [0, 1]: nhỏ nhất thành 0, lớn nhất thành 1.

**(b) Trực giác.** Hai giám khảo chấm thang khác nhau (một người chấm 1–10, người kia 50–100); muốn cộng điểm thì phải đổi
về cùng thang trước.

**(c) Công thức.** $\text{minmax}(s) = \dfrac{s - \min}{\max - \min}$, tính **trên tập ứng viên của từng khách**.

**(d) Ví dụ tính tay.** Điểm GMF-F của 3 món: [2, 5, 8] → min 2, max 8 → [0; 0,5; 1].

**(e) Trong đồ án.** Dùng trong LateFusion-F và Hybrid-CBCF, vì logit của các mô hình khác nhau nằm ở thang khác nhau.

### 4.11 Hybrid-CBCF — mô hình lai truyền thống

**(a) Định nghĩa.** Mô hình lai **không dùng học sâu**: kết hợp điểm của ba mô hình truyền thống Content, UserKNN, ItemKNN.

**(b) Trực giác.** Ba người tư vấn: một người nhìn sản phẩm giống (Content), một người nhìn khách giống (UserKNN), một người
nhìn món hay mua cùng (ItemKNN) — gộp ý kiến theo trọng số.

**(c) Công thức.**

$$s_{\text{Hybrid}} = w_C\,\text{minmax}(s_C) + w_U\,\text{minmax}(s_{UK}) + w_I\,\text{minmax}(s_{IK})$$

- Trọng số học bằng hồi quy logistic trên **hiệu** đặc trưng (món đúng − món sai), 50 món sai cho mỗi món đúng — tức tiêu
  chí BPR với hàm điểm tuyến tính.

**(d) Ví dụ tính tay (dùng trọng số thật).** Một món có điểm min–max: Content 0,5; UserKNN 0,8; ItemKNN 0,4 →
$0{,}12 \times 0{,}5 + 0{,}60 \times 0{,}8 + 0{,}28 \times 0{,}4 = 0{,}06 + 0{,}48 + 0{,}112 = 0{,}652$.

**(e) Trong đồ án.** Bổ sung theo góp ý của GVHD (theo chương 3 luận án của cô) để có một **mô hình lai truyền thống** đối
chiếu với mô hình lai học sâu. Đã thử bỏ phiếu (trung bình, max, min) và tổng có trọng số; chọn tổng có trọng số với
**Content 0,12; UserKNN 0,60; ItemKNN 0,28**. Tất định → chấm 1 lần dùng cho cả 5 seed. Kết quả: **0,03183** (H&M),
**0,02659** (Amazon); NeuMF-F hơn nó **+25,8%** và **+23,0%**.

### Câu hỏi tự kiểm tra — Cấp 4

1. **NeuMF-F khác NeuMF ở công thức nào?** — $\mathbf{q}_i = m_i\mathbf{e}^{\text{ID}}_i + W_I\mathbf{x}_i(t)$ (tương tự
   cho khách): cộng đặc trưng đã chiếu vào embedding ID.
2. **Vì sao $d_I$ = 157 trên H&M, 109 trên Amazon?** — 11 × 8 + 64 + 5 = 157; 5 × 8 + 64 + 5 = 109; chỉ khác số thuộc tính.
3. **TF-IDF và SVD làm gì?** — TF-IDF biến mô tả thành vector từ có trọng số; SVD nén 30.000 chiều xuống 64 chiều "chủ đề".
4. **Hợp nhất sớm và muộn khác nhau thế nào? LateFusion-F trộn điểm ra sao?** — Học chung một mô hình vs học riêng rồi trộn
   điểm; $0{,}4\cdot\text{minmax}(\text{GMF-F}) + 0{,}6\cdot\text{minmax}(\text{MLP-F})$.
5. **Vì sao Amazon chỉ có 2 chiều đặc trưng khách?** — Dữ liệu Amazon không có thông tin khách, chỉ còn 2 đặc trưng thời gian.

---

## Cấp 5 — Dữ liệu, đánh giá, thống kê, quy trình

### 5.1 Lấy mẫu theo khách hàng

**(a) Định nghĩa.** Thay vì dùng toàn bộ dữ liệu, chọn ra một nhóm khách và giữ **trọn lịch sử** của họ.

**(b) Trực giác.** Muốn tìm hiểu thói quen mua sắm, theo dõi trọn vẹn 2 năm của 20.000 người tốt hơn là xem lẻ tẻ vài giao
dịch của hàng triệu người.

**(c) Công thức.** Băm mã khách vào 100.000 nhóm: $\text{nhóm}(u) = \text{hash}(u) \bmod 100.000$; chia dãy nhóm thành các
**khối** liên tiếp, mỗi khối ~500.000 giao dịch. Hàm băm khoá cố định → chạy lại ra đúng cùng mẫu.

**(d) Ví dụ minh hoạ.** Khách có nhóm 1.200 thuộc khối 0 (nhóm 0–1.596); khách có nhóm 3.500 thuộc khối 2. Một khách chỉ
thuộc một khối → hai khối **không chung khách**.

**(e) Trong đồ án.** Dữ liệu gốc H&M: **31.788.324 giao dịch**, 105.542 sản phẩm (theo màu), 1.371.980 khách (20/09/2018 →
22/09/2020). Lấy mẫu vì Full Ranking trên toàn bộ cần hàng chục tỷ cặp mỗi mô hình, vượt **RAM 16 GB**. Hai mẫu: **mẫu phát
triển** (khối 0) để chọn cấu hình, **mẫu kiểm định** (khối 2) để kết luận. Lấy theo dòng sẽ cắt vụn lịch sử từng khách nên
không dùng.

### 5.2 Gộp theo mẫu thiết kế và gộp cặp

**(a) Định nghĩa.** Mọi màu của một kiểu sản phẩm được coi là **một sản phẩm**; nhiều giao dịch của cùng khách với cùng sản
phẩm được gộp thành **một cặp**, giữ **ngày mua đầu**.

**(b) Trực giác.** Mua áo kiểu X màu đen rồi màu trắng = vẫn là thích kiểu X; gợi ý kiểu X màu khác cho khách đó không có
nhiều giá trị.

**(c) Công thức.** `product_code` = `article_id // 1000` (ba chữ số cuối là mã màu). Cặp $(u, i)$ với
$t_{ui} = \min(\text{ngày mua})$.

**(d) Ví dụ tính tay.** `article_id` 0706016001 và 0706016002 → cùng `product_code` 706016 → một sản phẩm.

**(e) Trong đồ án.** Gộp màu làm số sản phẩm của mẫu phát triển giảm từ 55.971 xuống 27.370 trước khi lọc k-core.

### 5.3 Lọc k-core

**(a) Định nghĩa.** Bỏ khách có ít hơn $k$ lượt mua và sản phẩm có ít hơn $k$ khách mua, **lặp lại** đến khi không bỏ thêm
được.

**(b) Trực giác.** Khách chỉ mua 1 món hay sản phẩm chỉ 1 người mua thì mô hình không học được gì đáng tin; lại làm phình
danh sách ứng viên.

**(c) Công thức.** Lặp: bỏ $\{u : \deg(u) < k\}$ và $\{i : \deg(i) < k\}$ cho tới khi mọi khách và sản phẩm còn lại đều có
$\deg \ge k$ ($\deg$ = số cặp).

**(d) Ví dụ minh hoạ (k = 2).** Khách A mua {áo 1, áo 2}; khách B mua {áo 2}. Lượt 1: bỏ B (1 món) → áo 2 còn 1 người mua
(A) → lượt 2: bỏ áo 2 → A còn 1 món → lượt 3: bỏ A. Vì vậy phải **lặp**.

**(e) Trong đồ án.** H&M **k = 10** (k = 5 cần quá nhiều RAM khi Full Ranking); Amazon **k = 5**. Chỉ lọc trên dữ liệu
**trước mốc kiểm thử**. Mẫu kiểm định còn **7.994 khách, 6.749 sản phẩm, 243.696 cặp**. Hệ quả cần nói thẳng: dữ liệu thiên
về khách mua nhiều. File kết quả ghi kèm **MD5** để mọi mô hình đọc đúng cùng một dữ liệu.

### 5.4 Chia theo thời gian, món đúng và tập ứng viên

**(a) Định nghĩa.** Chọn một **mốc τ**: mọi dữ liệu trước τ để huấn luyện; món khách **mua lần đầu** trong cửa sổ sau τ là
**món đúng**. **Tập ứng viên** là các món được phép gợi ý.

**(b) Trực giác.** Giống thực tế: hôm nay (τ) dùng lịch sử để đoán khách sẽ mua gì trong 8 tuần tới.

**(c) Công thức.**

$$T_u = \{i \in C_u : \tau \le t_{ui} < \tau + \Delta\}, \qquad C_u = \{i : i \text{ có người mua trước } \tau\} \setminus H_u$$

- $T_u$: món đúng của khách $u$; $C_u$: tập ứng viên; $H_u$: món $u$ đã mua trước τ; $\Delta$: độ dài cửa sổ.

**(d) Ví dụ minh hoạ.** τ = 01/06. Khách đã mua áo A tháng 3; tháng 6 mua quần B và lại mua áo A. Món đúng chỉ có **quần B**
(áo A đã mua trước τ, không tính).

**(e) Trong đồ án.**

| | Xác thực | Kiểm thử |
|---|---|---|
| Mốc τ | 01/07/2020 | 29/07/2020 |
| Cửa sổ món đúng | 01/07–28/07/2020 (4 tuần) | 29/07–22/09/2020 (8 tuần) |

Mỗi khách H&M có khoảng **6.700 món ứng viên**; đồ án dự đoán món **mới đối với khách**.

### 5.5 Vì sao không dùng leave-one-out — và rò rỉ dữ liệu

**(a) Định nghĩa.** **Leave-one-out**: với mỗi khách, giấu món mua **cuối cùng** làm đáp án, còn lại để huấn luyện. **Rò rỉ
dữ liệu** (*data leakage*): mô hình vô tình thấy thông tin tương lai/đáp án khi học.

**(b) Trực giác.** Mỗi khách có "ngày hôm nay" khác nhau. Khách A mua món cuối năm 2019, khách B mua món cuối năm 2020. Khi
học, mô hình thấy giao dịch 2020 của B — tức "tương lai" so với đáp án của A → biết trước xu hướng → điểm đẹp giả.

**(c) Công thức (đo rò rỉ).** Tỉ lệ cặp huấn luyện có ngày **sau** ngày mua món kiểm thử của chính khách đó:
$\dfrac{\lvert\{(u,j,t) \in \text{train} : t > t^{\text{test}}_u\}\rvert}{\lvert\text{train}\rvert}$.

**(d) Ví dụ minh hoạ.** Khách mua 10 món; món kiểm thử ngày 01/05; có 1 món huấn luyện mua ngày 03/05 (cùng đơn sau) → 10%
dữ liệu huấn luyện của khách này nằm "sau" đáp án.

**(e) Trong đồ án.** Đo trên dữ liệu: **11,2%** cặp huấn luyện xảy ra sau món kiểm thử của chính khách đó (Meng et al.,
2020 đã chỉ ra vấn đề này) → loại leave-one-out, dùng **mốc thời gian chung**. Chặn rò rỉ bằng: k-core trước τ, đặc trưng
tính trước ngày $t$, mẫu âm trong món đã ra mắt, **test tự động** kiểm tra.

### 5.6 Amazon Beauty — dữ liệu đối chứng

**(a) Định nghĩa.** Bộ dữ liệu thứ hai, chạy lại **đúng quy trình** để kiểm tra kết luận có còn đúng ngoài H&M không.

**(b) Trực giác.** Một phương pháp nấu ăn ngon ở bếp nhà mình thì nấu thử ở bếp khác xem có còn ngon không.

**(c) Thiết lập.** Amazon review 2014 (McAuley et al., 2015), Beauty 5-core: 198.502 đánh giá, 22.363 khách, 12.101 sản
phẩm. Chia theo thời gian: xác thực 01/10–31/12/2013, kiểm thử 01/01–23/07/2014. k-core = 5 → **10.681 khách, 6.069 sản
phẩm, 94.009 cặp**; **2.644 khách** được đánh giá.

**(d) Ví dụ minh hoạ.** Một lượt đánh giá 5 sao và một lượt 1 sao đều thành "có tương tác = 1" (phản hồi ngầm).

**(e) Trong đồ án.** **Không tinh chỉnh lại**: dùng nguyên cấu hình chọn trên H&M, chỉ chọn số epoch trên xác thực Amazon —
tránh "chỉnh cho đẹp" trên dữ liệu mới. Kết luận chính (đặc trưng giúp nhiều, LateFusion-F đứng đầu) vẫn giữ.

### 5.7 Các độ đo xếp hạng

**(a) Định nghĩa.** Đo chất lượng danh sách Top-K của từng khách rồi **lấy trung bình theo khách**.

**(b) Trực giác.** HR: "có trúng ít nhất một món không?". Precision: "trong 10 món gợi ý, bao nhiêu món trúng?". Recall:
"trong các món khách mua, bắt được bao nhiêu?". NDCG: "trúng **và** xếp ở trên cao chưa?".

**(c) Công thức.** $T_u$: món đúng; $\text{hits}_u$: số món đúng trong top-K; $r_i$: hạng (từ 1).

| Độ đo | Công thức |
|---|---|
| HR@K | $\mathbb{1}[\text{hits}_u \ge 1]$ |
| Precision@K | $\text{hits}_u / K$ |
| Recall@K | $\text{hits}_u / \lvert T_u\rvert$ |
| **NDCG@K** | $\dfrac{\text{DCG}}{\text{IDCG}} = \dfrac{\sum_{i\in T_u, r_i\le K} 1/\log_2(r_i+1)}{\sum_{j=1}^{\min(\lvert T_u\rvert,K)} 1/\log_2(j+1)}$ |

- **DCG**: món đúng ở hạng $r$ được $1/\log_2(r+1)$ điểm — càng xuống thấp càng ít.
- **IDCG**: DCG lý tưởng (mọi món đúng xếp trên cùng) → NDCG nằm trong [0, 1].

**(d) Ví dụ tính tay — khách KH0261 của đồ án.** 2 món đúng, NeuMF-F xếp ở hạng **3** và **6**:

- DCG = $1/\log_2 4 + 1/\log_2 7 = 0{,}500 + 0{,}356 = 0{,}856$
- IDCG = $1/\log_2 2 + 1/\log_2 3 = 1 + 0{,}631 = 1{,}631$
- **NDCG@10 ≈ 0,525**; HR@10 = 1; Recall@10 = 2/2 = 1; Precision@10 = 2/10 = 0,2.
- NeuMF xếp món gần nhất ở hạng **164** → ngoài top-10 → NDCG@10 = 0.

Thêm: món đúng duy nhất ở hạng 1 → NDCG = 1; ở hạng 10 → $1/\log_2 11 ≈ 0{,}289$; ở hạng 11 → 0.

**(e) Trong đồ án.** **NDCG@10 là độ đo chính** (thưởng việc xếp món đúng lên cao). NDCG@10 trung bình chỉ ~0,04 vì đa số
khách không có món đúng nào lọt top-10 trong ~6.700 ứng viên — nhưng vẫn gấp ~40 lần Random (0,00098).

### 5.8 Độ phủ (*coverage*)

**(a) Định nghĩa.** Tỉ lệ sản phẩm trong danh mục **từng được gợi ý** cho ít nhất một khách.

**(b) Trực giác.** Gợi ý ai cũng cùng 10 món bán chạy thì hàng nghìn món khác không bao giờ được giới thiệu — tệ cho cửa
hàng.

**(c) Công thức.** $\text{Coverage@10} = \dfrac{\lvert\bigcup_u \text{Top-10}(u)\rvert}{\text{số sản phẩm ứng viên}}$.

**(d) Ví dụ minh hoạ.** 100 sản phẩm; danh sách top-10 của mọi khách gộp lại có 25 món khác nhau → độ phủ 25%.

**(e) Trong đồ án (H&M, seed 42).** Most Popular **0,3%**; UserKNN **5,7%**; Hybrid-CBCF **10,8%**; NeuMF-F **13,3%**;
ItemKNN **20,4%**. Chỉ mô tả, không dùng để kết luận chính.

### 5.9 Full Ranking và Sampled Ranking

**(a) Định nghĩa.** **Full Ranking**: chấm **mọi** món ứng viên rồi xếp hạng. **Sampled Ranking**: chỉ trộn món đúng với
~100 món ngẫu nhiên rồi xếp hạng trong nhóm nhỏ đó.

**(b) Trực giác.** Thi chọn người giỏi nhất trong cả trường (Full) khác hẳn thi trong một nhóm 100 người bốc ngẫu nhiên
(Sampled) — đứng đầu nhóm nhỏ dễ hơn nhiều.

**(c) Công thức.** Full: hạng $r_i = 1 + \lvert\{j \in C_u : \hat{y}_{uj} > \hat{y}_{ui}\}\rvert$. Sampled: thay $C_u$ bằng
$\{i\} \cup S$, $\lvert S\rvert \approx 100$.

**(d) Ví dụ minh hoạ.** Món đúng có hạng 300 trong 6.700 món (ngoài top-10). Trong nhóm 101 món ngẫu nhiên, nó có thể xếp
hạng 5 → "trúng" top-10 → điểm phóng đại.

**(e) Trong đồ án.** Dùng **Full Ranking** (~6.700 món/khách H&M), vì Sampled Ranking có thể **đảo thứ hạng** giữa các mô
hình (Krichene & Rendle, 2020). Đây cũng là lý do phải lấy mẫu khách (5.1) — Full Ranking rất tốn tài nguyên.

### 5.10 Quy trình chống thiên lệch

**(a) Định nghĩa.** Các bước giúp kết luận **không bị ảnh hưởng** bởi việc chọn lọc có lợi cho mô hình đề xuất.

**(b) Trực giác.** Như thi cử nghiêm túc: ra đề trước, niêm phong đề, chấm theo đáp án viết sẵn, ghi biên bản mỗi lần mở
đề.

**(c) Sáu bước.**

1. **Đăng ký trước** (`audit/PREREG_v2.md`): mô hình, lưới tham số, seed, độ đo, **10 cặp so sánh**, tiêu chí "tốt hơn" —
   commit **trước** khi mở tập kiểm thử.
2. **Tinh chỉnh** chỉ trên xác thực của mẫu phát triển: 6 cấu hình/mô hình, tổng 76 cấu hình, 4,7 giờ.
3. **Đánh giá cuối**: mỗi seed, mạng nơ-ron chọn số epoch trên xác thực của mẫu kiểm định → huấn luyện lại từ đầu trên mọi
   cặp trước τ → chấm kiểm thử.
4. **Khoá kiểm thử**: script từ chối chạy nếu kế hoạch chưa commit hoặc mã đang sửa dở; mỗi lần mở tập kiểm thử ghi nhật ký.
5. **So sánh công bằng**: cùng file dữ liệu (kiểm MD5), cùng tập ứng viên, cùng ngân sách tinh chỉnh.
6. **Không gõ tay số**: số trong báo cáo sinh tự động từ file kết quả.

**(d) Ví dụ minh hoạ.** Nếu không đăng ký trước, có thể thử 20 cách so sánh rồi chỉ báo 3 cách NeuMF-F thắng — kết luận
méo. Đăng ký trước chặn việc này.

**(e) Trong đồ án.** Nhờ quy trình này, đồ án **báo cả kết quả bất lợi**: trên Amazon, LateFusion-F tốt hơn NeuMF-F có ý
nghĩa — báo cáo ghi đúng như vậy.

### 5.11 Chênh lệch tương đối

**(a) Định nghĩa.** Mô hình A hơn B bao nhiêu **phần trăm** so với B.

**(b) Trực giác.** Hơn 0,01 điểm có thể là nhiều hay ít tuỳ mức nền; phần trăm giúp so sánh công bằng.

**(c) Công thức.** $\text{rel} = \dfrac{A - B}{B}$.

**(d) Ví dụ tính tay.** NeuMF-F (0,04003) vs NeuMF (0,02783): $(0{,}04003 - 0{,}02783)/0{,}02783 = 0{,}01220/0{,}02783 ≈
0{,}438$ → **+43,8%**.

**(e) Trong đồ án.** Là một trong ba điều kiện của tiêu chí "tốt hơn": phải **≥ 5%**. NeuMF-F vs GMF-F chỉ +2,6% → không
đạt ngưỡng → "ngang nhau".

### 5.12 Ghép cặp theo khách và kiểm định Wilcoxon signed-rank

**(a) Định nghĩa.** So hai mô hình **trên cùng từng khách**: tính hiệu $d_u$ cho mỗi khách, rồi kiểm định xem các hiệu này
có lệch hẳn về một phía không. Kết quả là **p-value**.

**(b) Trực giác.** Hai thuốc thử trên **cùng** bệnh nhân (trước/sau) chính xác hơn thử trên hai nhóm khác nhau. p-value nhỏ
nghĩa là "nếu hai mô hình thật ra ngang nhau thì rất khó thấy chênh lệch lớn như vậy".

**(c) Công thức.** $d_u = \text{NDCG@10}_A(u) - \text{NDCG@10}_B(u)$ (mỗi bên trung bình 5 seed). Wilcoxon: bỏ $d_u = 0$,
xếp hạng $\lvert d_u\rvert$ từ nhỏ đến lớn, tính $W^+$ = tổng hạng các khách A hơn, $W^-$ = tổng hạng khách B hơn; $W^+$
và $W^-$ càng chênh nhau thì p càng nhỏ. Không giả định phân phối chuẩn.

**(d) Ví dụ tính tay (ví dụ minh hoạ).** 5 khách: $d$ = 0,3; 0; −0,1; 0,5; 0,2. Bỏ 0 → |d| = 0,3; 0,1; 0,5; 0,2 → hạng 3;
1; 4; 2. $W^+$ = 3 + 4 + 2 = 9 (khách dương); $W^-$ = 1. Lệch hẳn về A.

**(e) Trong đồ án.** Dùng Wilcoxon vì NDCG từng khách **lệch rất mạnh** (đa số bằng 0), không theo phân phối chuẩn. Cài bằng
`scipy.stats.wilcoxon`.

### 5.13 Khoảng tin cậy bootstrap 95%

**(a) Định nghĩa.** Ước lượng khoảng mà **hiệu trung bình thật** có khả năng nằm trong, bằng cách lấy mẫu lại dữ liệu nhiều
lần.

**(b) Trực giác.** Nếu chọn ngẫu nhiên một nhóm khách khác (cùng cỡ) thì kết quả có còn nghiêng về A không? Lặp 10.000 lần
để biết.

**(c) Công thức.** Lặp $b = 1..B$: rút có hoàn lại $n$ khách, tính $\bar{d}^{(b)}$. Khoảng tin cậy = [phân vị 2,5%; phân
vị 97,5%] của $\{\bar{d}^{(b)}\}$. Khoảng **không chứa 0** → chênh lệch nhất quán về một phía.

**(d) Ví dụ minh hoạ.** 10.000 lần lấy mẫu lại cho các trung bình từ 0,008 đến 0,016; 2,5% nhỏ nhất dưới 0,009, 2,5% lớn
nhất trên 0,015 → CI = [0,009; 0,015], không chứa 0.

**(e) Trong đồ án.** **10.000 lần lấy mẫu lại**, seed 0. Ablation chỉ báo khoảng tin cậy (không kiểm định): "bỏ thuộc tính"
và "bỏ văn bản" có khoảng **chứa 0** → ghi "chưa khẳng định".

### 5.14 So sánh bội và hiệu chỉnh Holm

**(a) Định nghĩa.** Khi làm **nhiều** phép kiểm định, xác suất có ít nhất một kết luận "có ý nghĩa" **sai** tăng lên. Holm
hiệu chỉnh p-value để kiểm soát điều này.

**(b) Trực giác.** Tung xúc xắc một lần ra mặt 6 là hiếm; tung 10 lần thì gần như chắc có ít nhất một mặt 6. Làm 10 phép
kiểm định thì dễ "trúng" một kết quả ăn may.

**(c) Công thức.** Với $m$ phép kiểm định, xếp p tăng dần $p_{(1)} \le \dots \le p_{(m)}$:

$$p^{\text{Holm}}_{(k)} = \max_{j \le k}\ \min\big(1,\ (m - j + 1)\,p_{(j)}\big)$$

Kết luận có ý nghĩa khi $p^{\text{Holm}} < \alpha = 0{,}05$. Không hiệu chỉnh, với 10 phép mỗi phép α = 5%, khả năng có ít
nhất một kết luận sai lên tới khoảng 40%.

**(d) Ví dụ tính tay.** $m = 10$: p nhỏ nhất 0,003 → × 10 = **0,03** < 0,05 → có ý nghĩa. p = 0,02 đứng thứ 3 → × 8 =
**0,16** → **không** còn ý nghĩa (dù 0,02 < 0,05 nếu xét riêng).

**(e) Trong đồ án.** **Họ 10 so sánh** đăng ký trước, hiệu chỉnh Holm trên cả họ. Hybrid-CBCF có **họ bổ sung riêng** (2 so
sánh) hiệu chỉnh Holm riêng.

### 5.15 Tiêu chí "A tốt hơn B"

**(a) Định nghĩa.** Chỉ kết luận "tốt hơn" khi **đồng thời** thoả ba điều kiện:

1. p sau Holm < 0,05 (có ý nghĩa thống kê);
2. khoảng bootstrap 95% **không chứa 0** (nhất quán về một phía);
3. chênh lệch tương đối **≥ 5%** (đủ lớn để có ý nghĩa thực tế).

Thiếu một điều kiện → "không khác biệt có ý nghĩa" (demo ghi "ngang nhau").

**(b) Trực giác.** Một học sinh hơn bạn 0,1 điểm trung bình, dù chắc chắn về thống kê, cũng chưa đáng gọi là "giỏi hơn" —
cần chênh đủ nhiều.

**(c) Công thức.** $\text{tốt hơn} \iff p_{\text{Holm}} < 0{,}05 \land 0 \notin \text{CI}_{95\%} \land \lvert\text{rel}\rvert
\ge 5\%$.

**(d) Ví dụ minh hoạ.** Chênh +2,6%, p_Holm = 0,01, CI không chứa 0 → vẫn **"ngang nhau"** vì 2,6% < 5%.

**(e) Trong đồ án.** Trên H&M: NeuMF-F **tốt hơn 7/9** đối thủ; **ngang** GMF-F (+2,6%) và LateFusion-F (−2,2%). Trên
Amazon: LateFusion-F **tốt hơn** NeuMF-F (NeuMF-F thấp hơn 12,5%).

### 5.16 Phân tích bóc tách (*ablation study*)

**(a) Định nghĩa.** Tắt lần lượt **từng thành phần** của mô hình, giữ nguyên phần còn lại, đo kết quả giảm bao nhiêu → biết
thành phần nào quan trọng.

**(b) Trực giác.** Muốn biết nguyên liệu nào làm món ăn ngon: lần lượt bỏ từng thứ rồi nếm.

**(c) Công thức.** $\Delta = \dfrac{\text{NDCG}_{\text{bỏ X}} - \text{NDCG}_{\text{đầy đủ}}}{\text{NDCG}_{\text{đầy đủ}}}$.

**(d) Ví dụ minh hoạ.** Đầy đủ 0,040; bỏ thời gian còn 0,023 → $\Delta = (0{,}023 - 0{,}040)/0{,}040 ≈ -42\%$.

**(e) Trong đồ án.** 4 biến thể, **chỉ seed 42**, chỉ mô tả:

| Bỏ nhóm | H&M | Amazon |
|---|---|---|
| Đặc trưng thời gian | **−42,3%** (quan trọng nhất) | **−31,6%** |
| Thông tin khách | −10,3% | +1,3% (chưa khẳng định; Amazon chỉ có đặc trưng thời gian của khách) |
| Thuộc tính sản phẩm | −3,7% (chưa khẳng định) | −14,4% |
| Văn bản | −2,7% (chưa khẳng định) | −9,8% (chưa khẳng định) |

Hợp lý với thời trang: hàng mới và hàng đang bán chạy đổi theo mùa, nên tín hiệu thời gian mạnh nhất.

### 5.17 Hệ thống và demo

**(a) Định nghĩa.** Chuỗi script đi từ dữ liệu gốc tới báo cáo, và một ứng dụng web minh hoạ.

**(b) Trực giác.** Như dây chuyền nhà máy: mỗi trạm làm một việc, sản phẩm trạm trước là nguyên liệu trạm sau.

**(c) Luồng.**

```
1_sample.py → 3_features.py → 2_prepare.py → 4_tune.py → 5_final.py (+ 6_bosung.py) → 7_report.py → 8_check_report.py
 lấy mẫu      đặc trưng        k-core, MD5    tinh chỉnh  đánh giá cuối 5 seed          bảng, hình,     đối chiếu
                                                                                       macro LaTeX     câu chữ báo cáo
```

**(d) Ví dụ minh hoạ.** Bấm một khách trên demo → trình duyệt gọi API → máy chủ chấm ~6.700 món bằng mô hình đã huấn luyện →
trả 10 món kèm ảnh, tên.

**(e) Trong đồ án.** Chạy qua `python run.py <lệnh>`. Demo: backend **FastAPI** nạp checkpoint seed 42, **chỉ suy diễn,
không huấn luyện**; frontend HTML/CSS/JavaScript. Trung vị gợi ý top-10: **16,1 ms** (H&M), **11,3 ms** (Amazon) trên CPU.
Khách mới nhận Most Popular. Số trên trang Kết quả đọc thẳng từ file kết quả nên trùng báo cáo.

### Câu hỏi tự kiểm tra — Cấp 5

1. **Vì sao chia theo thời gian mà không dùng leave-one-out?** — Leave-one-out để lọt tương lai: 11,2% cặp huấn luyện xảy ra
   sau món kiểm thử của chính khách đó.
2. **Tính NDCG@10 khi món đúng duy nhất ở hạng 1, 10, 11.** — 1; ≈ 0,289; 0.
3. **Vì sao dùng Full Ranking?** — Sampled Ranking phóng đại điểm và có thể đảo thứ hạng mô hình.
4. **Holm làm gì? Ví dụ.** — Hiệu chỉnh p khi làm nhiều phép kiểm định; p = 0,02 đứng thứ 3 trong 10 → × 8 = 0,16 → mất ý
   nghĩa.
5. **Vì sao NeuMF-F hơn GMF-F 2,6% vẫn là "ngang nhau"?** — Không đạt ngưỡng chênh lệch tương đối 5%.

---

## Kết quả chính

### NDCG@10 trung bình 5 seed

| Mô hình | H&M | Amazon Beauty |
|---|---|---|
| LateFusion-F | **0,04093** (hạng 1) | **0,03747** (hạng 1) |
| NeuMF-F (đề xuất) | 0,04003 (hạng 2) | 0,03277 (hạng 3) |
| GMF-F | 0,03902 | 0,03298 |
| MLP-F | 0,03480 | 0,03065 |
| Hybrid-CBCF (bổ sung) | 0,03183 | 0,02659 |
| UserKNN | 0,03114 | 0,02506 |
| ItemKNN | 0,02860 | 0,02333 |
| NeuMF | 0,02783 | 0,01978 |
| MostPopular-Recent | 0,02760 | 0,01401 |
| GMF | 0,02695 | 0,01627 |
| BPR-MF | 0,02661 | 0,01144 |
| MLP | 0,02373 | 0,01271 |
| Most Popular | 0,02184 | 0,00872 |
| Content | 0,00506 | 0,00945 |
| Random | 0,00098 | 0,00101 |

### Đọc bảng thế nào

1. **Đặc trưng là đóng góp chính.** Bốn mô hình có đặc trưng (LateFusion-F, NeuMF-F, GMF-F, MLP-F) đứng đầu cả hai bộ.
   NeuMF-F hơn NeuMF chỉ dùng ID **+43,8%** (H&M), **+65,7%** (Amazon), đều có ý nghĩa.
2. **Hợp nhất hai nhánh có lợi nhưng không phải cách nào cũng thắng.** LateFusion-F (hợp nhất muộn) cao nhất cả hai bộ. Trên
   H&M, NeuMF-F **ngang** GMF-F (+2,6%) và LateFusion-F (−2,2%); trên Amazon, LateFusion-F **tốt hơn** NeuMF-F có ý nghĩa.
3. **Học sâu có đặc trưng thắng lai truyền thống.** NeuMF-F hơn Hybrid-CBCF **+25,8%** (H&M), **+23,0%** (Amazon).
4. **NeuMF-F tốt hơn có ý nghĩa 7/9 đối thủ** trong họ so sánh trên H&M.
5. **Không gọi NeuMF-F là mô hình tốt nhất.**

### Vì sao NeuMF-F không đứng đầu mà đồ án vẫn có giá trị

- Câu hỏi nghiên cứu là **"thêm đặc trưng vào khung MF + DNN có giúp không, giúp bao nhiêu"** — câu trả lời rõ ràng: có,
  +43,8% / +65,7%, có ý nghĩa thống kê, đúng trên cả hai bộ dữ liệu.
- Kết quả "hợp nhất muộn ≥ hợp nhất sớm" là **phát hiện trung thực** nhờ quy trình đăng ký trước — đồ án không chỉnh kế hoạch
  để mô hình đề xuất thắng.
- NeuMF-F vẫn có ưu điểm thực tế: **một** mô hình, thời gian huấn luyện **15,2 phút** so với **30,1 phút** của LateFusion-F
  (H&M, mỗi seed), và trên H&M không thua có ý nghĩa.

---

## 20 câu hỏi hội đồng có thể hỏi

**1. Đề tài giải quyết bài toán gì?**
Với mỗi khách H&M, gợi ý 10 sản phẩm thời trang khách có khả năng mua lần đầu trong 8 tuần tới, chỉ dựa trên lịch sử mua
(phản hồi ngầm). Mô hình đề xuất NeuMF-F kết hợp nhân tử hoá ma trận (GMF) và mạng nơ-ron sâu (MLP), có thêm đặc trưng
khách và sản phẩm. Kết luận được kiểm chứng thêm trên Amazon Beauty.

**2. NeuMF-F khác NeuMF gốc ở điểm nào?**
NeuMF gốc chỉ dùng embedding ID. NeuMF-F cộng thêm đặc trưng đã chiếu: $\mathbf{q}_i = m_i\mathbf{e}^{\text{ID}}_i +
W_I\mathbf{x}_i(t)$, tương tự cho khách. Đặc trưng gồm thuộc tính, mô tả văn bản và thời gian. Nhờ đó NeuMF-F hơn NeuMF
+43,8% trên H&M và +65,7% trên Amazon, đều có ý nghĩa.

**3. Vì sao vector sản phẩm 157 chiều trên H&M và 109 chiều trên Amazon?**
$d_I$ = số thuộc tính × 8 + 64 + 5. H&M có 11 thuộc tính → 88 + 64 + 5 = 157; Amazon có 5 thuộc tính → 40 + 64 + 5 = 109.
Mỗi thuộc tính dùng embedding 8 chiều; văn bản 64 chiều sau TF-IDF và SVD; 5 đặc trưng thời gian. Hai bộ chỉ khác nhau ở
số thuộc tính.

**4. Epoch, batch, dừng sớm trong đồ án được đặt thế nào?**
Một epoch là một lượt qua toàn bộ dữ liệu huấn luyện; mỗi batch 512 mẫu; tối đa 20 epoch. Sau mỗi epoch chấm NDCG@10 trên
tập xác thực; 5 epoch liền không cải thiện thì dừng và lấy epoch tốt nhất. Ở đánh giá cuối, mô hình được huấn luyện lại từ
đầu với đúng số epoch đã chọn.

**5. Bảng kết quả có nhiều ô "± 0,00000", có phải thiếu số liệu?**
Không. Đó là độ lệch chuẩn qua 5 seed bằng 0. Các mô hình Most Popular, MostPopular-Recent, Content, UserKNN, ItemKNN,
Hybrid-CBCF không có bước ngẫu nhiên nên cho cùng một kết quả ở mọi seed. Chỉ mạng nơ-ron, BPR-MF và Random mới dao động
theo seed.

**6. Vì sao không dùng leave-one-out như bài báo NCF?**
Leave-one-out cho mỗi khách một "hôm nay" khác nhau nên để lọt thông tin tương lai: trên dữ liệu, 11,2% cặp huấn luyện xảy
ra sau món kiểm thử của chính khách đó. Đồ án dùng một mốc thời gian chung (29/07/2020), giống cách hệ thống thật dự đoán
tương lai. Đây cũng là khuyến nghị của Meng et al. (2020).

**7. Vì sao dùng Full Ranking mà không lấy mẫu 100 món như nhiều bài báo?**
Sampled Ranking phóng đại điểm và có thể đảo thứ hạng giữa các mô hình (Krichene & Rendle, 2020). Full Ranking chấm toàn
bộ ~6.700 món ứng viên mỗi khách nên phản ánh đúng thực tế. Đổi lại tốn tài nguyên, nên phải lấy mẫu khách và lọc 10-core
cho vừa RAM 16 GB.

**8. NDCG@10 tính thế nào? Cho ví dụ.**
NDCG = DCG / IDCG; món đúng ở hạng $r$ được $1/\log_2(r+1)$. Khách KH0261 có 2 món đúng, NeuMF-F xếp hạng 3 và 6: DCG =
0,5 + 0,356 = 0,856; IDCG = 1 + 0,631 = 1,631; NDCG ≈ 0,525. NeuMF xếp món gần nhất ở hạng 164 nên NDCG@10 = 0.

**9. NDCG@10 chỉ khoảng 0,04 có phải quá thấp?**
Không thể so với số của bài báo vì khác dữ liệu, cách chia và giao thức. Đây là trung bình trên 3.165 khách của tập kiểm thử H&M, chọn trong
~6.700 ứng viên; phần lớn khách không có món đúng nào lọt top-10. Random chỉ đạt 0,00098, Most Popular 0,02184; NeuMF-F
0,04003 gấp ~40 lần ngẫu nhiên.

**10. Kiểm định thống kê làm thế nào?**
Với mỗi khách lấy NDCG@10 trung bình 5 seed, tính hiệu giữa hai mô hình. Dùng Wilcoxon signed-rank ghép cặp theo khách và
khoảng tin cậy bootstrap 95% (10.000 lần). Họ 10 so sánh đăng ký trước, hiệu chỉnh Holm, α = 0,05.

**11. Tiêu chí "tốt hơn" là gì?**
Đồng thời: p sau Holm < 0,05, khoảng tin cậy bootstrap không chứa 0, và chênh lệch tương đối ≥ 5%. Thiếu một điều kiện thì
ghi "không khác biệt có ý nghĩa". Vì vậy NeuMF-F hơn GMF-F 2,6% vẫn là "ngang nhau".

**12. Vì sao cần hiệu chỉnh Holm?**
Làm 10 phép kiểm định, mỗi phép α = 5%, thì khả năng có ít nhất một kết luận sai lên khoảng 40%. Holm nhân p nhỏ nhất với
10, kế tiếp với 9…, giữ tính đơn điệu. Ví dụ p = 0,02 đứng thứ 3 thành 0,16 và mất ý nghĩa.

**13. Hợp nhất sớm và hợp nhất muộn khác nhau thế nào?**
Hợp nhất sớm nối biểu diễn hai nhánh rồi một mô hình học chung — NeuMF-F. Hợp nhất muộn huấn luyện GMF-F và MLP-F riêng rồi
trộn điểm: $0{,}4\cdot\text{minmax}(\text{GMF-F}) + 0{,}6\cdot\text{minmax}(\text{MLP-F})$ — LateFusion-F. Cách phân loại
theo luận án của GVHD.

**14. Vì sao mô hình đề xuất không đứng đầu? Đồ án còn giá trị không?**
LateFusion-F cao nhất trên cả hai bộ; trên H&M NeuMF-F ngang nó (−2,2%), trên Amazon thua có ý nghĩa (−12,5%). Đồ án vẫn
chứng minh rõ đặc trưng là đóng góp chính (+43,8% / +65,7% so với NeuMF), và báo kết quả trung thực theo kế hoạch đăng ký
trước. NeuMF-F là một mô hình, huấn luyện 15,2 phút so với 30,1 phút của LateFusion-F.

**15. Làm sao đảm bảo không "chỉnh cho đẹp" trên tập kiểm thử?**
Kế hoạch đăng ký trước và commit trước khi mở tập kiểm thử. Mọi quyết định làm trên mẫu phát triển; kết luận chỉ trên mẫu
kiểm định — khách khác hẳn. Script khoá kiểm thử từ chối chạy nếu kế hoạch chưa commit, và mỗi lần mở tập kiểm thử đều ghi
nhật ký.

**16. Vì sao lọc 10-core? Có hạn chế gì?**
Khách và sản phẩm quá ít dữ liệu không học được gì đáng tin, lại làm phình tập ứng viên; k = 5 cần quá nhiều RAM khi Full
Ranking. Hạn chế: dữ liệu thiên về khách mua nhiều. Việc lọc chỉ dùng dữ liệu trước mốc kiểm thử nên không lộ tương lai.

**17. Nhóm đặc trưng nào quan trọng nhất?**
Theo ablation (seed 42): bỏ đặc trưng thời gian làm NDCG@10 giảm 42,3% trên H&M và 31,6% trên Amazon — mạnh nhất. Bỏ thông
tin khách giảm 10,3% (H&M). Bỏ thuộc tính hay văn bản giảm ít và khoảng tin cậy chứa 0 trên H&M nên chưa khẳng định. Hợp lý
vì thời trang thay đổi theo mùa và xu hướng.

**18. Vì sao không tinh chỉnh lại trên Amazon?**
Để Amazon là phép kiểm chứng thật sự: dùng nguyên cấu hình chọn trên H&M, chỉ chọn số epoch trên tập xác thực Amazon. Nếu
tinh chỉnh lại thì có thể "chỉnh cho hợp" dữ liệu mới. Kết luận chính vẫn giữ: đặc trưng giúp nhiều, LateFusion-F đứng đầu.

**19. Hybrid-CBCF là gì, vì sao thêm vào?**
Mô hình lai truyền thống theo chương 3 luận án của GVHD: kết hợp Content, UserKNN, ItemKNN bằng tổng có trọng số (0,12;
0,60; 0,28) học theo tiêu chí BPR. Thêm vào để đối chiếu mô hình lai học sâu với mô hình lai truyền thống. NeuMF-F hơn nó
+25,8% (H&M) và +23,0% (Amazon).

**20. Demo hoạt động thế nào? Khách mới thì sao?**
Backend FastAPI nạp mô hình đã huấn luyện (seed 42), chỉ suy diễn: chấm ~6.700 món cho một khách, trung vị 16,1 ms (H&M) và
11,3 ms (Amazon) trên CPU. Frontend HTML/CSS/JS hiện gợi ý của NeuMF-F cạnh một mô hình đối chứng. Khách chưa có trong dữ
liệu đã học nhận danh sách Most Popular.
