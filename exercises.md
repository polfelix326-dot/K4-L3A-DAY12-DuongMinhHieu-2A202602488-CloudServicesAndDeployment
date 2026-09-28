# Phiếu Phản Ánh — K4 Level 3A, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng `*Câu trả lời của bạn*` bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Dương Minh Hiệu  Mã học viên: 2A202602488

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Khi deploy lên Render, nếu `agent_api_key` có mặc định `"changeme"`, app vẫn
> khởi động thành công dù quên set biến môi trường trên dashboard. Service hiện
> "healthy", `/health` trả 200 — trông bình thường. Nhưng bất kỳ ai cũng có thể
> gọi `/ask` với `X-API-Key: changeme` và tốn tiền API của bạn. Bạn chỉ phát
> hiện ra khi hóa đơn đến hoặc log hiển thị request bất thường — có thể đã
> mất vài ngày. Với fail-fast, app báo lỗi ngay tại lúc khởi động, bạn nhìn
> log Docker/Render và biết ngay trong vài giây rằng thiếu biến môi trường,
> sửa xong trước khi service tiếp nhận traffic.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

```json
{"event": "ask_completed", "level": "info", "timestamp": "2026-09-28T13:20:53.619613+00:00", "user_id": "log-test", "tokens_in": 2, "tokens_out": 36, "cost_usd": 2.19e-05}
```

Hai việc làm được với dòng log JSON mà `print("đã trả lời xong")` không làm được:

1. **Truy vấn có cấu trúc**: Có thể lọc tất cả request của user `log-test`,
   hoặc tìm request nào `cost_usd > 0.01` để phát hiện lạm dụng — log text
   phẳng không có trường để truy vấn.
2. **Tích hợp pipeline giám sát**: Log JSON gửi trực tiếp vào Grafana,
   Datadog để đồ thị real-time mà không cần parse thêm.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 446 MB |
| Multi-stage | 271 MB |

Giải thích: phần dung lượng chênh lệch ~175 MB là do bản 1 stage chứa toàn bộ
trình biên dịch, pip, python headers và build tools vẫn còn trong image cuối
cùng. Multi-stage chỉ copy kết quả đã cài đặt từ builder stage sang, loại
bỏ sạch sẽ trình biên dịch và cache pip.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

Khi thay đổi `app/main.py`, build multi-stage cho kết quả:
- `COPY requirements.txt` → **CACHED**
- `RUN pip install` → **CACHED**
- `COPY app ./app` → **REBUILD** (layer thay đổi)
- `COPY utils ./utils` → **REBUILD**
- `RUN useradd...` → **REBUILD**

Nếu đặt `COPY . .` lên trước `RUN pip install`, thì bất kỳ thay đổi nào trong
source code cũng khiến Docker invalidates layer `COPY . .`, kéo theo
`RUN pip install` phải chạy lại — lãng phí thời gian cài đặt thư viện mỗi
lần sửa một dòng comment.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

1. App có lỗ hổng injection (ví dụ: f-string chưa sanitize trong log prompt).
2. Kẻ tấn công gửi input độc hại qua `/ask`.
3. App thực thi lệnh shell từ input đó, chạy với quyền **root** bên trong container.
4. Container chia sẻ kernel với host → kẻ tấn công có thể `mount --bind` hoặc
   truy cập `/proc` để escape ra host.
5. Trên host, tiến trình chạy với uid 0 (root) → truy cập toàn bộ hệ thống
   file, SSH keys, biến môi trường, mạng nội bộ.

Lệnh `USER appuser` (uid 10001) cắt chuỗi ở bước 3: container không chạy
với root, nên ngay cả khi code bị exploit, kẻ tấn công chỉ có quyền hạn hạn
chế của user `appuser`, không thể escape ra host.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

Tối đa **20 request** trong 2 giây liên tiếp.

Giải thích: User gửi 10 request ở giây 55-59 (cuối phút M), rồi gửi thêm 10
request ở giây 0-4 (đầu phút M+1). Vì cửa sổ phút đồng hồ reset tại giây 00,
tổng cộng là 20 request trong khoảng ~9 giây (có thể nén trong 2 giây nếu gửi
10 ở giây 59 và 10 ở giây 0). Sliding window ngăn được điều này vì nó trượt
liên tục: nếu gửi 10 request ở giây 59, cửa sổ 60 giây từ giây 0 vẫn đang
gồm 10 request đó nên chỉ còn chỗ cho 0 request mới.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

- **Rate limit** giới hạn **số request** theo thời gian, bảo vệ tính sẵn sàng
  (availability). Mục tiêu: ngăn service quá tải.
- **Cost guard** giới hạn **chi phí thực sự** (token tiêu thụ), bảo vệ ngân
  sách (budget). Mục tiêu: ngăn lãng phí tiền API LLM.

Tình huống rate limit cho qua nhưng cost guard chặn:
User gửi 5 request/phận (dưới hạn mức 10/phút) nhưng mỗi câu hỏi dài, tốn
nhiều token → chi phí tích lũy nhanh, vượt `MONTHLY_BUDGET_USD`. Rate limit
cho qua vì số lượng ít, nhưng cost guard chặn với 402.

Tình huống ngược lại:
User gửi 15 request/phút, mỗi câu hỏi ngắn "hello" (2 token mỗi request) →
chi phí rất thấp. Rate limit chặn với 429, nhưng cost guard không chặn vì tổng
chi phí chưa vượt budget.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với
cụm 3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

1. Redis mất kết nối 30 giây (network glitch).
2. Cả 3 container đều trả 503 ở endpoint `/health` (vì health giờ kiểm
   tra Redis).
3. Load balancer đánh dấu cả 3 instance là unhealthy, dừng gửi traffic.
4. Service trả 503 cho mọi request — người dùng thấy "service chết".
5. Redis kết nối lại → các container hồi phục, `/health` trở lại 200.

Vấn đề: health check phụ thuộc Redis → một lỗi Redis **tạm thời** khiến cả cụm
bị coi là chết, có thể trigger restart không cần thiết hoặc scale-down. Với
`/health` tách biệt (không kiểm tra Redis), LB vẫn giữ instance trong vòng
quay, service vẫn phục vụ traffic, và `/ready` tự hồi phục khi Redis lại.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

Quan sát thực tế (gọi `/ask` 3 lần cùng `X-User-Id: stateless-test`):
- Call 1: `history_length=0`
- Call 2: `history_length=2` (câu hỏi + câu trả lời)
- Call 3: `history_length=4`

Nếu lịch sử lưu trong dict Python (memory), mỗi container có một dict riêng.
Khi scale 3 instance, mỗi instance giữ state của chính nó. Cùng user_id gọi
vào các instance khác nhau sẽ thấy history_length khác nhau hoặc luôn bằng 0.
Mỗi lần container restart → dict mất → lịch sử về 0.

Với Redis, state nằm bên ngoài mọi container → mọi instance đều thấy cùng
một lịch sử. Service truly stateless: có thể scale, restart, thay đổi instance
mà không mất dữ liệu người dùng.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

**Lỗi gặp**: Sau khi tạo Blueprint trên Render, service chạy nhưng URL
`https://day12-agent-70zd.onrender.com/` trả "detail not found" — service không
phục vụ được traffic.

**Thông báo lỗi**: Không có HTTP response rõ ràng; dashboard cho biết service
đang chạy nhưng `/health` không khả dụng từ bên ngoài qua URL public.

**Nguyên nhân**: `render.yaml` dùng `type: redis` cho Key Value instance. Đây là
kiểu **deprecated** trên Render Blueprint spec, tài nguyên Redis không được
tạo đúng cách → `REDIS_URL` không được điền tự động → `/ready` thất bại.

**Cách tìm**: Xem logs trên dashboard — service build thành công nhưng
readiness check fail. Đối chiếu `render.yaml` với spec mới nhất tại
render.com/docs/blueprint-spec → phát hiện `type: redis` phải là `type: keyvalue`.

**Sửa**: Đổi `type: redis` → `type: keyvalue`, thêm `region: oregon` cho cả
service và Key Value để đảm bảo private network hoạt động, thêm
`maxmemoryPolicy: noeviction` để bảo vệ rate-limit và cost-guard keys khỏi
bị eviction.
