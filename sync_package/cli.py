import argparse
import glob
from directory_sync.sync import sync_directories


def main():
    parser = argparse.ArgumentParser(
        description="Sync directories using rsync with wildcard support.",
        epilog='Example usage: python -m sync_package.cli "user@remote:/path/to/A/*.txt" "/path/to/B"',
    )
    parser.add_argument(
        "remote_directory",
        type=str,
        help="The remote directory path with wildcard (e.g., user@remote:/path/to/A/*.txt).",
    )
    parser.add_argument(
        "local_directory",
        type=str,
        help="The local directory path where files will be synced (e.g., /path/to/B).",
    )

    args = parser.parse_args()

    # Use glob to expand the wildcard pattern
    remote_files = glob.glob(args.remote_directory)

    # Use a list comprehension to sync each file
    [
        sync_directories(remote_file, args.local_directory)
        for remote_file in remote_files
    ]


if __name__ == "__main__":
    main()
