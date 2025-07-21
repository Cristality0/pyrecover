# PyRecover 🔐

A simple, secure command-line tool for encrypting and decrypting recovery codes using password-based encryption. Perfect for safely storing backup codes, recovery phrases, and other sensitive text data.

## Features

- **🔒 Secure Encryption**: Uses PBKDF2 key derivation (100,000 iterations) with Fernet (AES 128) encryption
- **📋 Clipboard Integration**: Seamlessly reads from and writes to your clipboard
- **🛡️ Password Protection**: Secure password input with confirmation and hidden typing
- **📁 File Support**: Read from and save to files as an alternative to clipboard
- **🎨 Rich Output**: Beautiful terminal output with emojis and formatting
- **🔍 Debug Mode**: Option to show/hide input data for verification

## Installation

### Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Install
```bash
git clone <repository-url>
cd pyrecover
uv sync
```

## Usage

### Basic Workflow

1. **Encrypt recovery codes:**

   ```bash
   uv run pyrecover encrypt
   ```

   - Copy your recovery codes to clipboard first
   - Enter and confirm your password when prompted
   - Encrypted data is automatically copied back to clipboard

2. **Decrypt recovery codes:**

   ```bash
   uv run pyrecover decrypt
   ```

   - Copy encrypted data to clipboard first
   - Enter your password when prompted
   - Original recovery codes are copied back to clipboard

### Advanced Options

#### Encrypt Command

```bash
uv run pyrecover encrypt [OPTIONS]
```

**Options:**

- `--from/-f FILE`: Read data from file instead of clipboard
- `--save/-s FILE`: Save encrypted data to file instead of clipboard
- `--hide-input/-hi`: Hide input data (default: shows data for verification)

**Examples:**

```bash
# Encrypt from file and save to file
uv run pyrecover encrypt --from codes.txt --save encrypted.txt

# Encrypt clipboard data and save to file
uv run pyrecover encrypt --save backup.enc

# Hide input data display
uv run pyrecover encrypt --hide-input
```

#### Decrypt Command

```bash
uv run pyrecover decrypt [OPTIONS]
```

**Options:**

- `--from/-f FILE`: Read encrypted data from file instead of clipboard
- `--save/-s FILE`: Save decrypted data to file instead of clipboard
- `--hide-input/-hi`: Hide input data

**Examples:**

```bash
# Decrypt from file and save to file
uv run pyrecover decrypt --from encrypted.txt --save recovered.txt

# Decrypt clipboard and save to file
uv run pyrecover decrypt --save recovered.txt

# Decrypt file to clipboard
uv run pyrecover decrypt --from backup.enc
```

## Example Workflow

### Scenario: Backup Google 2FA Recovery Codes

1. **Initial Setup:**

   ```bash
   # Copy your recovery codes from Google to clipboard
   uv run pyrecover encrypt --save google-backup.enc
   # Enter a strong password when prompted
   ```

2. **Later Recovery:**

   ```bash
   # When you need your codes back
   uv run pyrecover decrypt --from google-backup.enc
   # Enter your password
   # Codes are now in your clipboard, ready to paste
   ```

### Scenario: Quick Clipboard Encryption

1. **Encrypt:**

   ```bash
   # Copy sensitive text to clipboard
   uv run pyrecover encrypt
   # Encrypted data replaces original in clipboard
   ```

2. **Decrypt:**

   ```bash
   # Copy encrypted data to clipboard
   uv run pyrecover decrypt
   # Original text restored to clipboard
   ```

## Security Features

- **PBKDF2 Key Derivation**: 100,000 iterations with SHA-256
- **Fernet Encryption**: Symmetric encryption using AES 128 in CBC mode with HMAC authentication
- **Random Salt**: Unique salt generated for each encryption
- **Password Confirmation**: Prevents typos during encryption
- **Hidden Password Input**: Passwords never displayed on screen

## File Format

Encrypted data is stored as base64-encoded text containing:

- 16-byte random salt
- Fernet-encrypted payload

This format is safe to store in text files, databases, or transmit via text channels.

## Error Handling

The tool provides clear error messages for common issues:

- Empty clipboard/file
- Wrong password
- Corrupted data
- Missing files
- Invalid encrypted data format

## Development

### Adding Dependencies

```bash
uv add package-name
```

### Development Dependencies

```bash
uv sync --group dev
```

### Running Tests

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check
```

## Security Considerations

⚠️ **Important Security Notes:**

- **Strong Passwords**: Use unique, strong passwords for encryption
- **Password Storage**: PyRecover doesn't store passwords - you must remember them
- **Backup**: Consider storing encrypted files in multiple secure locations
- **Clipboard Security**: Be aware that clipboard contents may be accessible to other applications
- **File Permissions**: Ensure encrypted files have appropriate permissions (e.g., `chmod 600`)

## Common Use Cases

- **2FA Recovery Codes**: Backup codes from Google, GitHub, etc.
- **Cryptocurrency Seeds**: Secure storage of wallet recovery phrases
- **API Keys**: Encrypt sensitive API keys and tokens
- **Passwords**: Temporary secure storage of sensitive passwords
- **Personal Data**: Any sensitive text that needs encrypted storage

## Troubleshooting

### Clipboard Issues

- **Linux**: Ensure `xclip` or `xsel` is installed
- **macOS**: Should work out of the box
- **Windows**: Should work out of the box

### Permission Errors

```bash
# Fix file permissions
chmod 600 encrypted-file.enc
```

### Clear Clipboard

```bash
# Clear clipboard after use (Linux)
echo "" | xclip -selection clipboard

# Clear clipboard after use (macOS)
echo "" | pbcopy
```
