# PyRecover 🔐

A simple, secure command-line tool for encrypting and decrypting recovery codes using password-based encryption.

### Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Install
```bash
git clone [...]
cd pyrecover
uv sync
```

## Usage

### Basic Workflow

1. **Encrypt recovery codes:**

   - Copy your recovery codes to clipboard first

   ```bash
   uv run pyrecover encrypt
   ```

   - Enter and confirm your password when prompted
   - Encrypted data is automatically copied back to clipboard

3. **Decrypt recovery codes:**

   ```bash
   uv run pyrecover decrypt
   ```

   - Copy encrypted data to clipboard first
   - Enter your password when prompted
   - Original recovery codes are copied back to clipboard

