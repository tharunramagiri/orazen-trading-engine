#!/usr/bin/env python3
import sys

from orazen import __version__ as ft_version
from orazen_client import __version__ as client_version


def main():
    if ft_version != client_version:
        print(f"Versions do not match: \nft: {ft_version} \nclient: {client_version}")
        sys.exit(1)
    print(f"Versions match: ft: {ft_version}, client: {client_version}")
    sys.exit(0)


if __name__ == "__main__":
    main()
