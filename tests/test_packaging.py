# Copyright (c) 2016-2026 Memgraph Ltd. [https://memgraph.com]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
import sys
import zipfile
import shutil
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]

# Read version and requires-python from pyproject.toml
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # noqa: F401

with open(ROOT_DIR / "pyproject.toml", "rb") as f:
    _pyproject = tomllib.load(f)

PROJECT_NAME = _pyproject["project"]["name"]
PROJECT_VERSION = _pyproject["project"]["version"]
REQUIRES_PYTHON = _pyproject["project"]["requires-python"]
CURRENT_PYTHON = f"{sys.version_info.major}.{sys.version_info.minor}"


def _python_bin(venv_dir: Path) -> Path:
    """Return the platform-appropriate Python binary path inside a venv."""
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _uv_available() -> bool:
    return shutil.which("uv") is not None


@pytest.mark.skipif(not _uv_available(), reason="uv not installed")
class TestUvBuild:
    """Verify that the project builds correctly with uv."""

    def test_uv_build_produces_artifacts(self, tmp_path):
        """uv build should produce both an sdist and a wheel."""
        result = subprocess.run(
            ["uv", "build", "--out-dir", str(tmp_path)],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"uv build failed:\n{result.stderr}"

        sdists = list(tmp_path.glob("*.tar.gz"))
        wheels = list(tmp_path.glob("*.whl"))
        assert len(sdists) == 1, f"Expected 1 sdist, found {len(sdists)}: {sdists}"
        assert len(wheels) == 1, f"Expected 1 wheel, found {len(wheels)}: {wheels}"

    def test_wheel_metadata(self, tmp_path):
        """The built wheel should contain correct package name and version."""
        subprocess.run(
            ["uv", "build", "--wheel", "--out-dir", str(tmp_path)],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )

        wheel_file = next(tmp_path.glob("*.whl"))
        with zipfile.ZipFile(wheel_file) as zf:
            metadata_files = [n for n in zf.namelist() if n.endswith("/METADATA")]
            assert len(metadata_files) == 1, f"Expected 1 METADATA file, found: {metadata_files}"
            metadata = zf.read(metadata_files[0]).decode("utf-8")

        assert f"Name: {PROJECT_NAME}" in metadata
        assert f"Version: {PROJECT_VERSION}" in metadata
        assert f"Requires-Python: {REQUIRES_PYTHON}" in metadata

    def test_wheel_contains_package(self, tmp_path):
        """The wheel should include the gqlalchemy package directory."""
        subprocess.run(
            ["uv", "build", "--wheel", "--out-dir", str(tmp_path)],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )

        wheel_file = next(tmp_path.glob("*.whl"))
        with zipfile.ZipFile(wheel_file) as zf:
            names = zf.namelist()

        gqlalchemy_files = [n for n in names if n.startswith("gqlalchemy/")]
        assert len(gqlalchemy_files) > 0, "Wheel does not contain gqlalchemy/ package"
        assert any(n == "gqlalchemy/__init__.py" for n in gqlalchemy_files), "Missing gqlalchemy/__init__.py"

    @pytest.mark.slow
    def test_wheel_install_in_isolated_venv(self, tmp_path):
        """The wheel should install successfully into a fresh venv."""
        wheel_dir = tmp_path / "dist"
        venv_dir = tmp_path / "venv"

        # Build
        subprocess.run(
            ["uv", "build", "--wheel", "--out-dir", str(wheel_dir)],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )

        wheel_file = next(wheel_dir.glob("*.whl"))

        # Create isolated venv using the current Python version
        subprocess.run(
            ["uv", "venv", "--python", CURRENT_PYTHON, str(venv_dir)],
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )

        python = _python_bin(venv_dir)
        result = subprocess.run(
            ["uv", "pip", "install", "--python", str(python), str(wheel_file)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"Wheel install failed:\n{result.stderr}"

        # Verify the package is importable
        check = subprocess.run(
            [str(python), "-c", "from gqlalchemy.models import Node; print('OK')"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert check.returncode == 0, f"Import check failed:\n{check.stderr}"
        assert "OK" in check.stdout


def _make_venv_and_install_extra(tmp_path, extra, import_check):
    """Helper: build wheel, create venv, install with extra, verify import."""
    wheel_dir = tmp_path / "dist"
    venv_dir = tmp_path / "venv"

    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(wheel_dir)],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    )

    wheel_file = next(wheel_dir.glob("*.whl"))

    subprocess.run(
        ["uv", "venv", "--python", CURRENT_PYTHON, str(venv_dir)],
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )

    python = str(_python_bin(venv_dir))

    # Install wheel with the extra
    result = subprocess.run(
        ["uv", "pip", "install", "--python", python, f"{wheel_file}[{extra}]"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Install with [{extra}] failed:\n{result.stderr}"

    # Verify the extra's package is importable
    check = subprocess.run(
        [python, "-c", import_check],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert check.returncode == 0, f"Import check for [{extra}] failed:\n{check.stderr}"
    assert "OK" in check.stdout


@pytest.mark.slow
@pytest.mark.skipif(not _uv_available(), reason="uv not installed")
class TestUvOptionalExtras:
    """Verify that each optional extra installs and its key package is importable."""

    def test_extra_arrow(self, tmp_path):
        _make_venv_and_install_extra(tmp_path, "arrow", "import pyarrow; print('OK')")

    def test_extra_dot(self, tmp_path):
        _make_venv_and_install_extra(tmp_path, "dot", "import pydot; print('OK')")

    def test_extra_docker(self, tmp_path):
        _make_venv_and_install_extra(tmp_path, "docker", "import docker; print('OK')")

    def test_extra_dgl(self, tmp_path):
        _make_venv_and_install_extra(tmp_path, "dgl", "import torch; print('OK')")

    def test_extra_torch_pyg(self, tmp_path):
        _make_venv_and_install_extra(tmp_path, "torch_pyg", "import torch; print('OK')")
