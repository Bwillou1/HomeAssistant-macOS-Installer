# Third-party notices

This installer redistributes third-party software. The package must retain the upstream license and notice files included with each component.

- **Home Assistant Core** — Apache-2.0. Project: https://github.com/home-assistant/core
- **CPython runtime** — Python Software Foundation License. The included CPython runtime is obtained from Astral's `python-build-standalone` project; the runtime directory includes upstream license notices for CPython and bundled libraries. Project: https://github.com/astral-sh/python-build-standalone (MPL-2.0 for the build project).
- **PyObjC framework bindings** — MIT. Project: https://github.com/ronaldoussoren/pyobjc
- **Home Assistant Python dependencies** — each dependency's license and copyright notices are provided by its distribution metadata. They are not relicensed by this project.
- **uv** — used as a build-time tool only; it is not installed as a runtime dependency. Project: https://github.com/astral-sh/uv

The installer should be reviewed against the current licenses of the exact versions in `requirements.txt` before each public release. The Python runtime's bundled license files must not be stripped during packaging.