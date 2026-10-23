"""Keep the original Day 6 command available; implementation lives in animate.py."""

import sys
from pathlib import Path


def main(argv=None):
    # Load by a unique name even when another day's animate module is imported.
    import importlib.util

    path = Path(__file__).resolve().with_name("animate.py")
    spec = importlib.util.spec_from_file_location("aoc2024_day06_animation", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.main(argv)


if __name__ == "__main__":
    main()
