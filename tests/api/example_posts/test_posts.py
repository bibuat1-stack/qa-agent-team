"""示例接口用例：演示站点 JSONPlaceholder 的帖子接口，用来验证框架和流水线能跑通。

接入被测系统后删除本目录和 data/*/example_posts.yaml，按业务模块新建 tests/api/<模块>/。
"""
from __future__ import annotations

import pytest

from common.assertions import (
    assert_each_item_field,
    assert_is_list,
    assert_json_field,
    assert_not_empty,
    assert_status_code,
    get_field,
)
from common.http_client import http_client
from common.utils import load_data, unique_name

pytestmark = [pytest.mark.api, pytest.mark.example_posts]

GET_POST_CASES = load_data("test_cases/example_posts.yaml")["get_post_by_id"]


class TestPosts:
    """帖子接口（示例）"""

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_get_post_detail(self):
        """
        用例编号：API-POSTS-001
        用例名称：查询帖子详情
        前置条件：id=1 的帖子存在（演示站点的固定数据）
        测试步骤：GET /posts/1
        预期结果：状态码 200；id 为 1；title、body 不为空
        """
        response = http_client.get("/posts/1")

        assert_status_code(response, 200)
        assert_json_field(response, "id", 1)
        assert_not_empty(get_field(response, "title"), "title")
        assert_not_empty(get_field(response, "body"), "body")

    @pytest.mark.regression
    @pytest.mark.parametrize("case", GET_POST_CASES, ids=[case["case_id"] for case in GET_POST_CASES])
    def test_get_post_by_id(self, case):
        """
        用例编号：API-POSTS-002
        用例名称：按 id 查询帖子（数据驱动）
        前置条件：数据见 data/test_cases/example_posts.yaml 的 get_post_by_id
        测试步骤：GET /posts/{post_id}
        预期结果：状态码等于 expected_status；为 200 时 id、userId 与数据一致
        """
        response = http_client.get(f"/posts/{case['post_id']}")

        assert_status_code(response, case["expected_status"])
        if case["expected_status"] == 200:
            assert_json_field(response, "id", case["post_id"])
            assert_json_field(response, "userId", case["expected_user_id"])

    @pytest.mark.regression
    def test_list_posts_by_user(self):
        """
        用例编号：API-POSTS-003
        用例名称：按用户筛选帖子列表
        前置条件：userId=1 的用户有帖子（演示站点的固定数据）
        测试步骤：GET /posts?userId=1
        预期结果：状态码 200；返回非空列表；每条帖子的 userId 都是 1
        """
        response = http_client.get("/posts", params={"userId": 1})

        assert_status_code(response, 200)
        assert_is_list(response, "帖子列表")
        assert_not_empty(response, "帖子列表")
        assert_each_item_field(response, "userId", 1, "帖子列表")

    @pytest.mark.regression
    def test_create_post(self, api_data):
        """
        用例编号：API-POSTS-004
        用例名称：创建帖子
        前置条件：请求数据见 data/api_data/example_posts.yaml 的 create_post
        测试步骤：POST /posts，title 加唯一后缀，避免和其他数据冲突
        预期结果：状态码 201；返回的 title、body、userId 与请求一致；返回新帖子的 id
        """
        payload = api_data("example_posts.yaml")["create_post"]
        payload["title"] = f"{payload['title']}-{unique_name()}"

        response = http_client.post("/posts", json=payload)

        assert_status_code(response, 201)
        for field in ("title", "body", "userId"):
            assert_json_field(response, field, payload[field])
        assert_not_empty(get_field(response, "id"), "新帖子 id")
