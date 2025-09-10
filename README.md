# Emailer

A simple emailer for sending emails.

## Features

- Send emails via IMAP/SMTP
- Simple and readable code structure

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Configure your settings in `config.toml`:
```toml
[mail]
imap_host = "your_imap_host"
imap_port = 993
smtp_host = "your_smtp_host"
smtp_port = 587
```

3. Optional: configure work schedule under `[scheduler]`

## Usage

### Components

- **`emailer/utils/settings.py`**: Configuration management

## Requirements

- Python 3.11+
- Poetry for dependency management
- IMAP/SMTP credentials

## Project Structure

```
emailer/
├── config.toml              # Configuration file
├── emailer/
│   └── utils/
│       └── settings.py      # Settings management
└── pyproject.toml           # Poetry configuration
```
