from __future__ import annotations

import os
import plistlib
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PackagingContractTests(unittest.TestCase):
    def test_versions_are_consistent(self) -> None:
        version = (ROOT / "VERSION").read_text().strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        requirements = (ROOT / "requirements.txt").read_text()
        match = re.search(r"^homeassistant==([0-9.]+)$", requirements, re.MULTILINE)
        self.assertIsNotNone(match, "Home Assistant must be exactly pinned")
        self.assertRegex(match.group(1), r"^\d{4}\.\d+\.\d+$")

        distribution = ET.parse(ROOT / "pkg/Distribution.xml").getroot()
        package_ref = distribution.find("pkg-ref")
        self.assertIsNotNone(package_ref)
        self.assertEqual(package_ref.attrib.get("version"), "VERSION_PLACEHOLDER")
        self.assertIn("s/VERSION_PLACEHOLDER/$(VERSION)/g", (ROOT / "Makefile").read_text())
        self.assertEqual(package_ref.text, "#homeassistant-core.pkg")
        installer_check = distribution.find("script")
        self.assertIsNotNone(installer_check)
        self.assertIn("ARCH_PLACEHOLDER", "".join(installer_check.itertext()))
        self.assertIn("13.0", "".join(installer_check.itertext()))

    def test_launch_daemon_runs_unprivileged_installed_entrypoint(self) -> None:
        with (ROOT / "launchd/org.homeassistant.daemon.plist").open("rb") as stream:
            plist = plistlib.load(stream)
        self.assertEqual(plist["Label"], "org.homeassistant.daemon")
        self.assertEqual(plist["UserName"], "_homeassistant")
        self.assertEqual(plist["GroupName"], "_homeassistant")
        args = plist["ProgramArguments"]
        self.assertEqual(args[0], "/opt/homeassistant/venv/bin/hass")
        self.assertIn("/Library/Application Support/HomeAssistant/config", args)
        self.assertTrue(plist["RunAtLoad"])
        self.assertTrue(plist["KeepAlive"])

    def test_updater_checks_for_stable_core_daily(self) -> None:
        with (ROOT / "launchd/org.homeassistant.updater.plist").open("rb") as stream:
            plist = plistlib.load(stream)
        self.assertEqual(plist["Label"], "org.homeassistant.updater")
        self.assertEqual(plist["UserName"], "root")
        self.assertFalse(plist["RunAtLoad"])
        self.assertEqual(plist["StartCalendarInterval"], {"Hour": 4, "Minute": 30})
        script = (ROOT / "scripts/update").read_text()
        self.assertIn("https://pypi.org/pypi/homeassistant/json", script)
        self.assertIn("--venv-dir venv.next", script)
        self.assertIn("HomeAssistant-Backups", script)
        self.assertIn("WAS_RUNNING", script)

    def test_build_stages_only_intended_installer_scripts(self) -> None:
        makefile = (ROOT / "Makefile").read_text()
        self.assertIn("scripts/preinstall", makefile)
        self.assertIn("scripts/postinstall", makefile)
        self.assertIn("scripts/uninstall", makefile)
        self.assertIn("scripts/update", makefile)
        self.assertIn("org.homeassistant.updater.plist", makefile)
        self.assertIn("set -euo pipefail", makefile)
        self.assertIn("venv --relocatable", makefile)
        self.assertIn("python-build-standalone", (ROOT / "docs/BUILD.md").read_text())
        self.assertIn("pkgutil --expand-full", makefile)
        self.assertTrue((ROOT / "scripts/relocate_venv.py").is_file())
        self.assertFalse((ROOT / "pkg/preinstall").exists())
        self.assertFalse((ROOT / "pkg/postinstall").exists())

    def test_relocator_rewrites_venv_to_portable_sibling_runtime(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "ha-root"
            runtime = root / "python/cpython-3.14.2-macos-test/bin"
            env_bin = root / "venv/bin"
            runtime.mkdir(parents=True)
            env_bin.mkdir(parents=True)
            interpreter = runtime / "python3.14"
            interpreter.write_text("#!/bin/sh\nexit 0\n")
            interpreter.chmod(0o755)
            (root / "venv/pyvenv.cfg").write_text(f"home = {runtime}\nversion = 3.14.2\n")
            (env_bin / "python").symlink_to(interpreter)

            subprocess.run(
                ["python3", str(ROOT / "scripts/relocate_venv.py"), str(root), "--prefix", "/opt/homeassistant"],
                check=True,
            )
            self.assertEqual((env_bin / "python").resolve(), interpreter.resolve())
            self.assertEqual(os.readlink(env_bin / "python"), "../../python/cpython-3.14.2-macos-test/bin/python3.14")
            config = (root / "venv/pyvenv.cfg").read_text()
            self.assertIn("home = /opt/homeassistant/python/cpython-3.14.2-macos-test/bin", config)
            self.assertNotIn(str(root), config)

    def test_relocator_supports_sibling_staging_venv(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "ha-root"
            runtime = root / "python/cpython-3.14.8-macos-test/bin"
            env_bin = root / "venv.next/bin"
            runtime.mkdir(parents=True)
            env_bin.mkdir(parents=True)
            interpreter = runtime / "python3.14"
            interpreter.write_text("#!/bin/sh\nexit 0\n")
            interpreter.chmod(0o755)
            (root / "venv.next/pyvenv.cfg").write_text(f"home = {runtime}\nversion = 3.14.8\n")
            (env_bin / "python").symlink_to(interpreter)

            subprocess.run(
                ["python3", str(ROOT / "scripts/relocate_venv.py"), str(root),
                 "--venv-dir", "venv.next", "--prefix", "/opt/homeassistant"],
                check=True,
            )
            self.assertEqual((env_bin / "python").resolve(), interpreter.resolve())
            self.assertIn("home = /opt/homeassistant/python/cpython-3.14.8-macos-test/bin",
                          (root / "venv.next/pyvenv.cfg").read_text())

    def test_shell_scripts_parse(self) -> None:
        scripts = [
            ROOT / "scripts/preinstall",
            ROOT / "scripts/postinstall",
            ROOT / "scripts/uninstall",
            ROOT / "scripts/update",
            ROOT / "scripts/sign.sh",
            ROOT / "scripts/notarize.sh",
        ]
        for script in scripts:
            with self.subTest(script=script.name):
                subprocess.run(["bash", "-n", str(script)], check=True)


if __name__ == "__main__":
    unittest.main()
