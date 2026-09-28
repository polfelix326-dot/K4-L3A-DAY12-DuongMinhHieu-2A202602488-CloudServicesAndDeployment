# Thông Tin Deploy — Checkpoint 5

## Thông Tin Học Viên

| Mục | Nội dung |
|-----|----------|
| Họ và tên | Dương Minh Hiệu |
| Mã học viên | 2A202602488 |
| Repo | https://github.com/polfelix326-dot/K4-L3A-DAY12-DuongMinhHieu-2A202602488-CloudServicesAndDeployment |

## Service

| Mục | Nội dung |
|-----|----------|
| Public URL | https://day12-agent-70zd.onrender.com |
| Platform | Render |
| Ngày deploy | 28/09/2026 |

## Biến Môi Trường Đã Set Trên Cloud

Ghi tên biến và **nguồn giá trị**, không ghi giá trị:

| Biến | Đã set | Ghi chú |
|------|--------|---------|
| `PORT` | ✅ | platform tự gán |
| `AGENT_API_KEY` | ✅ | đặt trong dashboard Render, `sync: false`, không nằm trong repo |
| `REDIS_URL` | ✅ | Render Key Value cung cấp qua private network |
| `RATE_LIMIT_PER_MINUTE` | ✅ | 10 |
| `MONTHLY_BUDGET_USD` | ✅ | 10.0 |
| `LOG_LEVEL` | ✅ | INFO |

## Lệnh Kiểm Tra

```bash
URL=https://day12-agent-70zd.onrender.com

# 1. Liveness
curl -i "$URL/health"

# 2. Readiness — đã nối được Redis
curl -i "$URL/ready"

# 3. Không có API key — mong đợi 401
curl -i -X POST "$URL/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
```

## Kết Quả Chạy Thật

```bash
$ curl -i https://day12-agent-70zd.onrender.com/health
HTTP/2 200
content-type: application/json

{"status":"ok","service":"day12-agent","version":"1.0.0"}

$ curl -i https://day12-agent-70zd.onrender.com/ready
HTTP/2 200
content-type: application/json

{"status":"ready","redis":true}

$ curl -i -X POST https://day12-agent-70zd.onrender.com/ask \
  -H "Content-Type: application/json" -d '{"question":"Hello"}'
HTTP/2 401
```

## Ảnh Chụp Màn Hình

Đặt ảnh trong thư mục `screenshots/`:

- `screenshots/dashboard.png` — trang quản lý service trên platform Render
- `screenshots/health.png` — kết quả gọi `/health` từ curl
- `screenshots/ready.png` — kết quả gọi `/ready`
- `screenshots/ask_401.png` — kết quả gọi `/ask` không có key

---

## Ghi Chú

Deploy bằng Render Blueprint từ `render.yaml`. Biến `AGENT_API_KEY` được nhập trực tiếp trên dashboard (sync: false), không ghi vào repository. `REDIS_URL` tự động do Render Key Value cung cấp qua private network nội bộ.
