import os
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from app.security.jwt import (
    JWT_ALG,
    JWT_SECRET,
    create_access_token,
    decode_access_token,
)
from app.security.passwords import hash_password, verify_password


class TestPasswordHashing:
    """测试密码哈希功能"""

    def test_hash_password_returns_string(self):
        """测试密码哈希返回字符串"""
        password = "testpassword123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password

    def test_hash_password_different_for_same_input(self):
        """测试相同密码产生不同的哈希值（盐值不同）"""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2

    def test_verify_password_correct_password(self):
        """测试验证正确密码"""
        password = "testpassword123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """测试验证错误密码"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self):
        """测试空密码验证"""
        password = ""
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password("notempty", hashed) is False

    def test_hash_password_empty_string(self):
        """测试空字符串密码哈希"""
        password = ""
        hashed = hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert verify_password(password, hashed) is True

    def test_hash_password_special_characters(self):
        """测试包含特殊字符的密码"""
        password = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password(password + "x", hashed) is False

    def test_hash_password_unicode_characters(self):
        """测试包含Unicode字符的密码"""
        password = "密码测试123🚀"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password("密码测试123", hashed) is False


class TestJWTTokens:
    """测试JWT令牌功能"""

    def test_create_access_token_returns_string(self):
        """测试创建访问令牌返回字符串"""
        subject = "user123"
        token = create_access_token(subject)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_claims(self):
        """测试带声明的访问令牌创建"""
        subject = "user123"
        claims = {"role": "employee", "department": "IT"}
        token = create_access_token(subject, claims)
        assert isinstance(token, str)

        # 解码令牌验证内容
        decoded = decode_access_token(token)
        assert decoded["sub"] == subject
        assert decoded["role"] == "employee"
        assert decoded["department"] == "IT"

    def test_create_access_token_without_claims(self):
        """测试不带声明的访问令牌创建"""
        subject = "user123"
        token = create_access_token(subject)
        decoded = decode_access_token(token)
        assert decoded["sub"] == subject
        assert "iat" in decoded
        assert "exp" in decoded

    def test_decode_access_token_valid_token(self):
        """测试解码有效令牌"""
        subject = "user123"
        claims = {"role": "employer"}
        token = create_access_token(subject, claims)
        decoded = decode_access_token(token)

        assert decoded["sub"] == subject
        assert decoded["role"] == "employer"
        assert isinstance(decoded["iat"], int)
        assert isinstance(decoded["exp"], int)

    def test_decode_access_token_invalid_token(self):
        """测试解码无效令牌"""
        invalid_token = "invalid.token.here"
        with pytest.raises(Exception):  # jose库会抛出异常
            decode_access_token(invalid_token)

    def test_decode_access_token_empty_token(self):
        """测试解码空令牌"""
        with pytest.raises(Exception):
            decode_access_token("")

    def test_token_expiration_time(self):
        """测试令牌过期时间"""
        subject = "user123"
        token = create_access_token(subject)
        decoded = decode_access_token(token)

        # 检查过期时间是否在未来
        exp_timestamp = decoded["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)

        # 令牌应该在24小时后过期
        expected_exp = now + timedelta(minutes=60 * 24)
        time_diff = abs((exp_datetime - expected_exp).total_seconds())
        assert time_diff < 60  # 允许1分钟的误差

    def test_token_issued_at_time(self):
        """测试令牌签发时间"""
        subject = "user123"
        token = create_access_token(subject)
        decoded = decode_access_token(token)

        # 检查签发时间
        iat_timestamp = decoded["iat"]
        iat_datetime = datetime.fromtimestamp(iat_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)

        # 签发时间应该在最近几秒内
        time_diff = abs((now - iat_datetime).total_seconds())
        assert time_diff < 10  # 允许10秒的误差

    def test_create_token_with_none_claims(self):
        """测试创建令牌时声明为None"""
        subject = "user123"
        token = create_access_token(subject, None)
        decoded = decode_access_token(token)
        assert decoded["sub"] == subject
        assert "iat" in decoded
        assert "exp" in decoded

    def test_token_with_complex_claims(self):
        """测试包含复杂声明的令牌"""
        subject = "user123"
        complex_claims = {
            "role": "employee",
            "permissions": ["read", "write"],
            "metadata": {"department": "IT", "level": 5},
            "active": True,
        }
        token = create_access_token(subject, complex_claims)
        decoded = decode_access_token(token)

        assert decoded["sub"] == subject
        assert decoded["role"] == "employee"
        assert decoded["permissions"] == ["read", "write"]
        assert decoded["metadata"] == {"department": "IT", "level": 5}
        assert decoded["active"] is True

    def test_token_security_constants(self):
        """测试JWT安全常量"""
        # 这些测试确保常量被正确设置
        assert JWT_SECRET is not None
        assert len(JWT_SECRET) > 0
        assert JWT_ALG == "HS256"

        # 在生产环境中，密钥应该更复杂
        if JWT_SECRET == "dev-secret-change-me":
            pytest.skip("使用开发密钥，生产环境应使用更安全的密钥")
