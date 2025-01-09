import subprocess
import logging

def sync_directories(remote_path, local_path):
    logging.basicConfig(filename='rsync_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
    
    rsync_command = [
        'rsync', '-avz', '--ignore-existing', '--remove-source-files',
        f'{remote_path}/', local_path
    ]

    try:
        result = subprocess.run(rsync_command, check=True, capture_output=True, text=True)
        logging.info("Rsync completed successfully.")
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error("Rsync failed.")
        logging.error(e.stderr) 