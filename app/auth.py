"""CP3 — Xác thực bằng API key.

Public URL = ai cũng gọi được. Không có lớp này, hóa đơn LLM của bạn do
người lạ quyết định.
"""

from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from .config import get_settings

ANONYMOUS_USER = "anonymous"


def verify_api_key(
    x_api_key: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> str:
    """Kiểm tra header ``X-API-Key``; trả về user_id nếu hợp lệ.

    So sánh bằng ``secrets.compare_digest`` chứ không dùng ``==``: toán tử ``==``
    dừng ngay tại ký tự đầu khác nhau nên thời gian trả lời rò rỉ thông tin về
    khóa (timing attack). ``compare_digest`` luôn chạy hết chuỗi.

    Cả hai vế được ``encode`` sang bytes trước khi so sánh. Nếu so sánh trực
    tiếp hai ``str``, ``compare_digest`` ném ``TypeError`` khi gặp ký tự
    ngoài ASCII — tức là client gửi ``X-API-Key: é`` sẽ nhận 500 thay vì 401.
    """
    expected = get_settings().agent_api_key

    provided = x_api_key or ""
    if not provided or not secrets.compare_digest(
        provided.encode("utf-8"), expected.encode("utf-8")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing API key",
        )

    return x_user_id or ANONYMOUS_USER
