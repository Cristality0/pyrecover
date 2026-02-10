"""Tests for encrypt/decrypt round-trip via the Typer CLI."""

import base64
from pathlib import Path

from typer.testing import CliRunner

from pyrecover.main import SALT_SIZE, app

runner = CliRunner()


class TestEncryptCommand:
    """Tests for the encrypt CLI command."""

    def test_encrypt_from_file_save_to_file(self, tmp_path: Path):
        """Encrypt a file and save output to another file."""
        input_file = tmp_path / "plain.txt"
        output_file = tmp_path / "encrypted.txt"
        input_file.write_text("my-secret-recovery-codes")

        result = runner.invoke(
            app,
            ["encrypt", "--from", str(input_file), "--save", str(output_file)],
            input="strongpassword\nstrongpassword\n",
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Output should be valid base64 containing salt + ciphertext
        encrypted = output_file.read_text()
        raw = base64.b64decode(encrypted)
        assert len(raw) > SALT_SIZE

    def test_encrypt_empty_file_fails(self, tmp_path: Path):
        """Encrypting empty data should fail."""
        input_file = tmp_path / "empty.txt"
        input_file.write_text("")

        result = runner.invoke(
            app,
            ["encrypt", "--from", str(input_file), "--save", str(tmp_path / "out.txt")],
            input="password\npassword\n",
        )

        assert result.exit_code != 0

    def test_encrypt_hide_input_flag(self, tmp_path: Path):
        """--hide-input should suppress content display but still encrypt."""
        input_file = tmp_path / "data.txt"
        output_file = tmp_path / "enc.txt"
        input_file.write_text("secret-data-123")

        result = runner.invoke(
            app,
            [
                "encrypt",
                "--from",
                str(input_file),
                "--save",
                str(output_file),
                "--hide-input",
            ],
            input="pass123\npass123\n",
        )

        assert result.exit_code == 0
        assert "15 characters" in result.stdout
        assert output_file.exists()


class TestDecryptCommand:
    """Tests for the decrypt CLI command."""

    def test_decrypt_from_file_save_to_file(self, tmp_path: Path):
        """Decrypt a previously encrypted file."""
        input_file = tmp_path / "plain.txt"
        encrypted_file = tmp_path / "encrypted.txt"
        decrypted_file = tmp_path / "decrypted.txt"

        original_text = "recovery-code-abc-123-xyz"
        input_file.write_text(original_text)

        # First encrypt
        runner.invoke(
            app,
            ["encrypt", "--from", str(input_file), "--save", str(encrypted_file)],
            input="mypassword\nmypassword\n",
        )

        # Then decrypt
        result = runner.invoke(
            app,
            ["decrypt", "--from", str(encrypted_file), "--save", str(decrypted_file)],
            input="mypassword\n",
        )

        assert result.exit_code == 0
        assert decrypted_file.read_text() == original_text

    def test_decrypt_wrong_password_fails(self, tmp_path: Path):
        """Decrypting with the wrong password should fail."""
        input_file = tmp_path / "plain.txt"
        encrypted_file = tmp_path / "encrypted.txt"

        input_file.write_text("sensitive-data")

        # Encrypt with one password
        runner.invoke(
            app,
            ["encrypt", "--from", str(input_file), "--save", str(encrypted_file)],
            input="correct-password\ncorrect-password\n",
        )

        # Decrypt with a different password
        result = runner.invoke(
            app,
            [
                "decrypt",
                "--from",
                str(encrypted_file),
                "--save",
                str(tmp_path / "out.txt"),
            ],
            input="wrong-password\n",
        )

        assert result.exit_code != 0

    def test_decrypt_corrupted_data_fails(self, tmp_path: Path):
        """Decrypting corrupted data should fail gracefully."""
        bad_file = tmp_path / "bad.txt"
        bad_file.write_text("this-is-not-valid-encrypted-data!!!")

        result = runner.invoke(
            app,
            ["decrypt", "--from", str(bad_file), "--save", str(tmp_path / "out.txt")],
            input="password\n",
        )

        assert result.exit_code != 0

    def test_decrypt_missing_file_fails(self, tmp_path: Path):
        """Decrypting from a nonexistent file should fail."""
        result = runner.invoke(
            app,
            ["decrypt", "--from", str(tmp_path / "nonexistent.txt")],
            input="password\n",
        )

        assert result.exit_code != 0


class TestRoundTrip:
    """End-to-end encryption/decryption round-trip tests."""

    def test_roundtrip_preserves_data(self, tmp_path: Path):
        """Data should survive an encrypt -> decrypt round trip."""
        original = "line1\nline2\nline3\nrecovery-code-final"
        input_file = tmp_path / "input.txt"
        encrypted_file = tmp_path / "encrypted.txt"
        output_file = tmp_path / "output.txt"
        input_file.write_text(original)

        runner.invoke(
            app,
            ["encrypt", "--from", str(input_file), "--save", str(encrypted_file)],
            input="roundtrip-pass\nroundtrip-pass\n",
        )
        result = runner.invoke(
            app,
            ["decrypt", "--from", str(encrypted_file), "--save", str(output_file)],
            input="roundtrip-pass\n",
        )

        assert result.exit_code == 0
        assert output_file.read_text() == original

    def test_roundtrip_special_characters(self, tmp_path: Path):
        """Data with special characters should survive a round trip."""
        original = (
            "Codes: \u00e4\u00f6\u00fc\u00df \u00e9\u00e8\u00ea \u00f1 @ # $ % & *"
        )
        input_file = tmp_path / "special.txt"
        encrypted_file = tmp_path / "enc.txt"
        output_file = tmp_path / "dec.txt"
        input_file.write_text(original)

        runner.invoke(
            app,
            ["encrypt", "--from", str(input_file), "--save", str(encrypted_file)],
            input="unicode-pass\nunicode-pass\n",
        )
        result = runner.invoke(
            app,
            ["decrypt", "--from", str(encrypted_file), "--save", str(output_file)],
            input="unicode-pass\n",
        )

        assert result.exit_code == 0
        assert output_file.read_text() == original

    def test_different_encryptions_produce_different_output(self, tmp_path: Path):
        """Same plaintext encrypted twice should produce different ciphertext.

        This is ensured by the random salt.
        """
        input_file = tmp_path / "data.txt"
        enc1 = tmp_path / "enc1.txt"
        enc2 = tmp_path / "enc2.txt"
        input_file.write_text("same-data")

        runner.invoke(
            app,
            ["encrypt", "--from", str(input_file), "--save", str(enc1)],
            input="same-pass\nsame-pass\n",
        )
        runner.invoke(
            app,
            ["encrypt", "--from", str(input_file), "--save", str(enc2)],
            input="same-pass\nsame-pass\n",
        )

        assert enc1.read_text() != enc2.read_text()
