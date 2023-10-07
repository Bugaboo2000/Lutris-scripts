import io
import json
import logging
import os
import shutil
import tarfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

import requests

from grapejuice_common import variables
from grapejuice_common.errors import PresentableError
from grapejuice_common.recipes.recipe import Recipe
from grapejuice_common.wine.wineprefix import Wineprefix

log = logging.getLogger(__name__)


def _dxvk_metadata_path(prefix: Wineprefix):
    return prefix.paths.dxvk_directory / "grapejuice_metadata.json"


def _read_dxvk_metadata(prefix: Wineprefix) -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
    path = _dxvk_metadata_path(prefix)
    if path.exists():
        with path.open("r", encoding=variables.text_encoding()) as fp:
            return path, json.load(fp)

    return None, None


def _dxvk_dll_list(prefix: Wineprefix) -> List[str]:
    return list(set(map(lambda s: f"{s}.dll", prefix.configuration.dxvk_overrides)))


def _dxvk_old_dll_list(prefix: Wineprefix) -> List[str]:
    return list(map(lambda s: f"{s}.old", _dxvk_dll_list(prefix)))


def _find_old_files(prefix: Wineprefix) -> List[Path]:
    system32_files = list(
        map(
            lambda n: prefix.paths.system32 / n,
            _dxvk_old_dll_list(prefix)
        )
    )

    syswow64_files = list(
        map(
            lambda n: prefix.paths.syswow64 / n,
            _dxvk_old_dll_list(prefix)
        )
    )

    return [*system32_files, *syswow64_files]


def _old_files_are_installed(prefix: Wineprefix) -> bool:
    return any(map(
        lambda p: p.exists(),
        _find_old_files(prefix)
    ))


def _legacy_dxvk_is_installed(prefix: Wineprefix) -> bool:
    metadata_path, metadata = _read_dxvk_metadata(prefix)
    metadata_exists = metadata_path and metadata_path.exists()

    setup_script_path = None
    setup_script_exists = False

    if metadata:
        setup_script_path = metadata.get("setup_script", None)
        setup_script_exists = setup_script_path and Path(setup_script_path).exists()

    old_files_present = _old_files_are_installed(prefix)

    log.info("DXVK status: " + json.dumps({
        "metadata_exists": metadata_exists,
        "setup_script_path": setup_script_path,
        "setup_script_exists": setup_script_exists,
        "old_files_present": old_files_present
    }))

    return metadata_exists and old_files_present and setup_script_exists


def _dxvk_is_installed(prefix: Wineprefix):
    _metadata_path, metadata = _read_dxvk_metadata(prefix)

    if metadata:
        try:
            return bool(metadata.get("is_installed", False))

        except Exception as e:
            log.warning(f"{type(e).__name__}: {e}")

    return False


def _restore_old_files(prefix: Wineprefix):
    for file in _find_old_files(prefix):
        if not file.exists():
            continue

        # Remove .old suffix, 4 chars
        # test.dll.old > test.dll
        target_file = file.parent / file.name[:-4]
        log.info(f"Restoring Wine DLL: {file} -> {target_file}")

        os.remove(target_file)  # Remove .dll
        shutil.move(file, target_file)  # Move .dll.old to .dll


def _uninstall_dxvk_legacy(prefix: Wineprefix):
    _metadata_path, metadata = _read_dxvk_metadata(prefix)
    log.info("Uninstalling DXVK legacy ( < 2.0 )")

    if metadata:
        setup_script_path = metadata.get("setup_script", None)
        if isinstance(setup_script_path, str):
            log.info(f"Using setup script {setup_script_path}")
            prefix.core_control.run_linux_command(
                setup_script_path,
                arguments=["uninstall"],
                working_directory=Path(setup_script_path).parent
            )

        else:
            log.info("No DXVK setup script in metadata")

    # Fallback in case no setup script was found
    _restore_old_files(prefix)


@dataclass
class InstallDXVKFilesResult:
    overrides: List[str] = field(default_factory=list)


def _install_dxvk_files(source_directory: Path, target_directory: Path):
    result = InstallDXVKFilesResult()

    for file in source_directory.glob("*.dll"):
        target_path = target_directory / file.name
        backup_target_path = target_directory / f"{file.name}.old"

        log.info(f"Installing DXVK file: {file} -> ({target_path}, {backup_target_path})")

        if backup_target_path.exists():
            raise PresentableError(
                "Backup files already exist",
                f"Backup file exists for '{target_path}' at '{backup_target_path}'. The backup file (the one with the "
                f".old extension) should not be there. For now please make sure the correct dll file is in place at "
                f"{target_path} and make sure the old one is removed. Please report this issue to the Grapejuice "
                f"maintainers with a sha512 hash of both the regular .dll file and the .dll.old file",
                technical_description="Invalid DXVK State"
            )

        # Backup Wine DLL
        shutil.copyfile(target_path, backup_target_path)
        os.remove(target_path)

        # Install DXVK DLL
        shutil.copyfile(file, target_path)

        result.overrides.append(file.name[:-4])

    return result


class UninstallDXVKRecipe(Recipe):
    def __init__(self):
        super().__init__(indicators=[lambda p: not (_dxvk_is_installed(p) or _legacy_dxvk_is_installed(p))])

    def _make_in(self, prefix: Wineprefix):
        legacy_installed = _legacy_dxvk_is_installed(prefix)
        is_installed = _dxvk_is_installed(prefix)

        if legacy_installed and not is_installed:
            return _uninstall_dxvk_legacy(prefix)

        _restore_old_files(prefix)

        metadata_path, metadata = _read_dxvk_metadata(prefix)

        # Resolve both variables because both are optional
        metadata_path = metadata_path or _dxvk_metadata_path(prefix)
        metadata = metadata or {"installed": False}

        metadata["is_installed"] = False

        with metadata_path.open("w+") as fp:
            json.dump(metadata, fp, indent=2)

        return None  # Make consistent with inline early return


class InstallDXVKRecipe(Recipe):
    def __init__(self):
        super().__init__(indicators=[lambda p: _dxvk_is_installed(p) or _legacy_dxvk_is_installed(p)])

    def _make_in(self, prefix: Wineprefix):
        release = variables.current_dxvk_release()

        response = requests.get(release.download_url)
        response.raise_for_status()

        prefix.paths.dxvk_directory.mkdir(parents=True, exist_ok=True)

        with io.BytesIO(response.content) as fp:
            with tarfile.open(fileobj=fp, mode="r:gz") as tf:
                tf.extractall(prefix.paths.dxvk_directory)

        versioned_dxvk_directory = prefix.paths.dxvk_directory / f"dxvk-{release.version}"
        if not versioned_dxvk_directory.exists():
            raise FileNotFoundError(versioned_dxvk_directory)

        directory_mapping = (
            (versioned_dxvk_directory / "x32", prefix.paths.syswow64),
            (versioned_dxvk_directory / "x64", prefix.paths.system32)
        )

        dxvk_overrides = []
        for source_dir, target_dir in directory_mapping:
            result = _install_dxvk_files(source_dir, target_dir)
            dxvk_overrides.extend(result.overrides)

        prefix.configuration.dxvk_overrides = list(set(dxvk_overrides))

        md_path = _dxvk_metadata_path(prefix)
        with md_path.open("w+", encoding=variables.text_encoding()) as fp:
            json.dump({"version": release.version, "is_installed": True}, fp, indent=2)
