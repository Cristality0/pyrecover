import base64
import secrets
from pathlib import Path
from typing import Annotated

import pyperclip
import rich
import typer
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

app = typer.Typer(rich_markup_mode="rich")

# Security constants
SALT_SIZE = 16
PBKDF2_ITERATIONS = 1_200_000  # Increased for better security
KEY_LENGTH = 32


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive encryption key from password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


@app.command()
def encrypt(
    password: Annotated[
        str, typer.Option(prompt=True, confirmation_prompt=True, hide_input=True)
    ],
    from_file: Annotated[
        Path | None,
        typer.Option("--from", "-f", help="Read data from file instead of clipboard"),
    ] = None,
    save_to_file: Annotated[
        Path | None,
        typer.Option(
            "--save", "-s", help="Save encrypted data to file instead of clipboard"
        ),
    ] = None,
    hide_input: Annotated[
        bool, typer.Option("--hide-input", help="Hide input password")
    ] = False,
):
    """Encrypt recovery codes from clipboard with password."""
    try:
        if from_file:
            clipboard_data = from_file.read_text().strip()
        else:
            clipboard_data = pyperclip.paste()

        if not clipboard_data.strip():
            typer.echo("❌ Clipboard is empty!", err=True)
            raise typer.Exit(1)

        if hide_input:
            typer.echo(f"📋 Found {len(clipboard_data)} characters")
        else:
            rich.print(clipboard_data)

        # Generate cryptographically secure salt
        salt = secrets.token_bytes(SALT_SIZE)
        key = derive_key(password, salt)

        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(clipboard_data.encode())

        # Combine salt and encrypted data
        final_data = base64.b64encode(salt + encrypted_data).decode()

        if save_to_file:
            save_to_file.write_text(final_data)
            typer.echo(f"✅ Encrypted data saved to {save_to_file}")
        else:
            pyperclip.copy(final_data)
            typer.echo("✅ Encrypted data copied to clipboard!")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ Encryption failed: {e!s}", err=True)
        raise typer.Exit(1) from e


@app.command()
def decrypt(
    password: Annotated[str, typer.Option(prompt=True, hide_input=True)],
    from_file: Annotated[
        Path | None,
        typer.Option(
            "--from", "-f", help="Read encrypted data from file instead of clipboard"
        ),
    ] = None,
    save_to_file: Annotated[
        Path | None,
        typer.Option(
            "--save", "-s", help="Save decrypted data to file instead of clipboard"
        ),
    ] = None,
):
    """Decrypt recovery codes and copy to clipboard."""
    try:
        # Get encrypted data
        if from_file:
            if not from_file.exists():
                typer.echo(f"❌ File {from_file} not found!", err=True)
                raise typer.Exit(1)
            encrypted_data_b64 = from_file.read_text().strip()
        else:
            encrypted_data_b64 = pyperclip.paste().strip()
            if not encrypted_data_b64:
                typer.echo("❌ Clipboard is empty!", err=True)
                raise typer.Exit(1)

        try:
            combined_data = base64.b64decode(encrypted_data_b64)
            if len(combined_data) < SALT_SIZE:
                msg = "Data too short"
                raise ValueError(msg)
            salt = combined_data[:SALT_SIZE]
            encrypted_data = combined_data[SALT_SIZE:]
        except Exception as e:
            typer.echo("❌ Decryption failed!", err=True)
            raise typer.Exit(1) from e

        key = derive_key(password, salt)
        fernet = Fernet(key)

        try:
            decrypted_data = fernet.decrypt(encrypted_data).decode()
        except Exception as e:
            # Generic error message to prevent information leakage
            typer.echo("❌ Decryption failed!", err=True)
            raise typer.Exit(1) from e

        # Save or copy to clipboard
        if save_to_file:
            save_to_file.write_text(decrypted_data)
            typer.echo(f"✅ Decrypted data saved to {save_to_file}")
        else:
            pyperclip.copy(decrypted_data)
            typer.echo("✅ Recovery codes decrypted and copied to clipboard!")

        typer.echo(f"📋 {len(decrypted_data)} characters restored")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo("❌ Decryption failed!", err=True)
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
