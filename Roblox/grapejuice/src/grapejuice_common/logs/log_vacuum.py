import logging
import os
import shutil
import time
from datetime import datetime
from glob import glob
from zipfile import ZipFile, ZIP_LZMA

from grapejuice_common import paths

log = logging.getLogger(__name__)
number_of_logs_to_keep = 10


def log_files():
    return paths.logging_directory().glob("*.log")


def archive_directory():
    return paths.logging_directory() / "archive"


def archive_files():
    return glob(os.path.join(archive_directory(), "*.zip"))


def archive_logs(old_log_files):
    datetime_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs(archive_directory(), exist_ok=True)
    archive_path = os.path.join(archive_directory(), f"{datetime_now}.zip")

    log.info(f"Writing log archive {archive_path}")

    with ZipFile(archive_path, "w", ZIP_LZMA) as zf:
        for file in old_log_files:
            log_stat = os.stat(file)

            if 0 < log_stat.st_size < 2048:
                with open(file, "rb") as fp:
                    zf.writestr(os.path.basename(file), fp.read(), ZIP_LZMA)

    for file in old_log_files:
        log.debug(f"Removing log file {file}")
        os.remove(file)


def can_delete_archive(file):
    stat = os.stat(file)
    time_delta = int(time.time()) - int(stat.st_ctime)

    # Older than a week
    return time_delta > 604800


def remove_empty_logs():
    for file in log_files():
        s = os.stat(file)
        if s.st_size <= 0:
            log.info(f"Removing empty log file: {file}")

            try:
                os.remove(file)

            except Exception as e:
                log.error(f"Failed to remove empty log file {file}:\n{e}")


def migrate_logs():
    logging_directory = paths.logging_directory()
    legacy_logging_directory = paths.legacy_logging_directory()

    logging_directory.mkdir(parents=True, exist_ok=True)

    if legacy_logging_directory.exists():
        if legacy_logging_directory.is_dir() and not legacy_logging_directory.is_symlink():
            log.info(f"Legacy logging directory '{legacy_logging_directory}' exists and will be migrated'")

            for file in legacy_logging_directory.rglob("*"):
                if not file.is_file():
                    continue

                relative_file = file.relative_to(legacy_logging_directory)
                log.info(f"Moving log file '{relative_file}'")

                target = logging_directory / relative_file

                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(file, target)

                except Exception as e:
                    log.error(f"Failed to move a log file to its new destination: '{file}'. {type(e).__name__}: {e}")

            shutil.rmtree(legacy_logging_directory)


def vacuum_logs():
    migrate_logs()

    files = list(log_files())

    if len(files) >= 50:
        files.sort(key=lambda f: os.stat(f).st_ctime)
        old_files = files[:-number_of_logs_to_keep]
        archive_logs(old_files)

    for file in filter(can_delete_archive, archive_files()):
        log.info(f"Removing log archive {file}")
        os.remove(file)
