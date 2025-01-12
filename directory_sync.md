# Directory Sync Utility

This utility provides a command-line tool to sync directories using `rsync` with support for wildcard patterns.

## Installation

To install the utility, navigate to the root directory and run:

```bash
pip install -e .
```

## Usage

You can use the command-line tool to sync files from a remote directory to a local directory. The remote directory path can include wildcard patterns to match multiple files.

### Command-Line Interface

```bash
python -m directory_sync.cli "user@remote:/path/to/A/*.txt" "/path/to/B"
```

- **remote_directory**: The remote directory path with wildcard (e.g., `user@remote:/path/to/A/*.txt`).
- **local_directory**: The local directory path where files will be synced (e.g., `/path/to/B`).

### Example

To sync all `.txt` files from a remote directory to a local directory:

```bash
python -m directory_sync.cli "user@remote:/path/to/A/*.txt" "/path/to/B"
```

## Logging

The tool logs its operations to `rsync_log.txt` in the current directory.

## License

This project is licensed under the MIT License. 