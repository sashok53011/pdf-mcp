"""Entry point for running pdf-mcp as a module."""

import logging

from .server import mcp


def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=__import__("sys").stderr)
    mcp.run()


if __name__ == "__main__":
    main()
