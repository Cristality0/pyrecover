"""Tests for the core cryptographic functions."""

import base64

from pyrecover.main import SALT_SIZE, derive_key


class TestDeriveKey:
    """Tests for the derive_key function."""

    def test_derive_key_returns_bytes(self):
        salt = b"\x00" * SALT_SIZE
        key = derive_key("password", salt)
        assert isinstance(key, bytes)

    def test_derive_key_deterministic(self):
        """Same password + salt should produce the same key."""
        salt = b"\x01" * SALT_SIZE
        key1 = derive_key("test-password", salt)
        key2 = derive_key("test-password", salt)
        assert key1 == key2

    def test_derive_key_different_passwords(self):
        """Different passwords should produce different keys."""
        salt = b"\x02" * SALT_SIZE
        key1 = derive_key("password-a", salt)
        key2 = derive_key("password-b", salt)
        assert key1 != key2

    def test_derive_key_different_salts(self):
        """Different salts should produce different keys."""
        salt1 = b"\x03" * SALT_SIZE
        salt2 = b"\x04" * SALT_SIZE
        key1 = derive_key("same-password", salt1)
        key2 = derive_key("same-password", salt2)
        assert key1 != key2

    def test_derive_key_is_valid_base64(self):
        """Key should be valid url-safe base64."""
        salt = b"\x05" * SALT_SIZE
        key = derive_key("password", salt)
        # Should not raise
        decoded = base64.urlsafe_b64decode(key)
        assert len(decoded) == 32
