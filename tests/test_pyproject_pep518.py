import hashlib
import shutil
import subprocess
import sys
import tarfile
import textwrap
import zipfile
from pathlib import Path

import pytest

DIR = Path(__file__).parent.resolve()
HELLO_PEP518 = DIR / "packages/simple_pyproject_ext"


@pytest.mark.integration
def test_pep518_sdist():
    correct_metadata = textwrap.dedent(
        """\
        Metadata-Version: 2.1
        Name: cmake-example
        Version: 0.0.1
        Requires-Python: >=3.7
        Provides-Extra: test
        Requires-Dist: pytest>=6.0; extra == "test"
        """
    )

    dist = HELLO_PEP518 / "dist"
    shutil.rmtree(dist, ignore_errors=True)
    subprocess.run(
        [sys.executable, "-m", "build", "--sdist"], cwd=HELLO_PEP518, check=True
    )
    (sdist,) = dist.iterdir()
    assert "cmake-example-0.0.1.tar.gz" == sdist.name

    if not (sys.platform.startswith("win32") or sys.platform.startswith("cygwin")):
        hash = hashlib.sha256(sdist.read_bytes()).hexdigest()
        if sys.version_info < (3, 9):
            assert (
                hash
                == "0f2ef937723753cb4df8154cddfc71d9b6451738f55392b184a0ca49ed8b2364"
            )
        else:
            assert (
                hash
                == "f22eaa307456a812fce6b9bd7386189c9c7e3bd10bbc6feee4f5ab0b1733b272"
            )

    with tarfile.open(sdist) as f:
        file_names = set(f.getnames())
        assert file_names == {
            f"cmake-example-0.0.1/{x}"
            for x in (
                "CMakeLists.txt",
                "pyproject.toml",
                "src/main.cpp",
                "PKG-INFO",
            )
        }
        pkg_info = f.extractfile("cmake-example-0.0.1/PKG-INFO")
        assert pkg_info
        pkg_info_contents = pkg_info.read().decode()
        assert correct_metadata == pkg_info_contents


@pytest.mark.compile
@pytest.mark.configure
@pytest.mark.integration
@pytest.mark.parametrize(
    "build_args", [(), ("--wheel",)], ids=["sdist_to_wheel", "wheel_directly"]
)
def test_pep518_wheel(virtualenv, build_args, monkeypatch):
    dist = HELLO_PEP518 / "dist"
    shutil.rmtree(dist, ignore_errors=True)
    monkeypatch.chdir(HELLO_PEP518)
    virtualenv.install("build[virtualenv]")
    virtualenv.module(
        "build",
        "--config-setting=logging.level=DEBUG",
        *build_args,
    )
    (wheel,) = dist.glob("cmake_example-0.0.1-*.whl")

    if sys.version_info >= (3, 8):
        with wheel.open("rb") as f:
            p = zipfile.Path(f)
            file_names = [p.name for p in p.iterdir()]

        assert len(file_names) == 2
        assert "cmake_example-0.0.1.dist-info" in file_names
        file_names.remove("cmake_example-0.0.1.dist-info")
        (so_file,) = file_names

        assert so_file.startswith("cmake_example")
        print("SOFILE:", so_file)

    virtualenv.install(wheel)

    version = virtualenv.execute(
        "import cmake_example; print(cmake_example.__version__)"
    )
    assert version == "0.0.1"

    add = virtualenv.execute("import cmake_example; print(cmake_example.add(1, 2))")
    assert add == "3"


@pytest.mark.compile
@pytest.mark.configure
@pytest.mark.integration
def test_pep518_pip(virtualenv):
    virtualenv.install("-v", HELLO_PEP518)

    version = virtualenv.execute(
        "import cmake_example; print(cmake_example.__version__)"
    )
    assert version == "0.0.1"

    add = virtualenv.execute("import cmake_example; print(cmake_example.add(1, 2))")
    assert add == "3"
