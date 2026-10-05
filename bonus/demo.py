"""Five zero-key queries after NB4 has materialized the Feast profile."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bonus.agent import HybridMemoryAgent  # noqa: E402


def main():
    agent = HybridMemoryAgent()
    for memory in (
        "Tôi đã đọc tài liệu Kubernetes về autoscaling pod theo lưu lượng và CPU.",
        "Tôi lưu ghi chú về bảo mật cloud: mã hóa dữ liệu và phân quyền IAM.",
        "Tôi học cách tối ưu chi phí hạ tầng bằng spot instance và lịch tắt máy.",
        "Tôi xem hướng dẫn triển khai dịch vụ qua CI/CD và kiểm tra rollback.",
        "Tôi so sánh tìm kiếm vector với BM25 cho câu hỏi tiếng Việt.",
    ):
        agent.remember(memory)
    agent.remember("Ghi chú riêng của người dùng khác.", user_id="u_002")

    queries = (
        "Tôi đã đọc gì về Kubernetes?",
        "Recommend đọc gì tiếp",
        "Tôi đang quan tâm gì gần đây?",
        "Tài liệu về tự động mở rộng hạ tầng?",
        "Cho tôi summary cloud security",
    )
    for i, query in enumerate(queries, start=1):
        context = agent.recall(query)
        assert "Ghi chú riêng của người dùng khác" not in context
        print(f"\n{i}. {query}\n{context}")


if __name__ == "__main__":
    main()
