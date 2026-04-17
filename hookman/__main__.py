"""Permite ejecutar `python -m hookman`."""

import sys

from hookman.cli import main


if __name__ == "__main__":
    sys.exit(main())
