#!/usr/bin/env python3
"""Wrapper module for content publication utilities.

This thin wrapper allows invoking the legacy `scripts/publish_content.py`
module from the new package namespace (`scripts.content.publish_content`).
All detailed logic lives in the legacy module while the refactor progresses.
"""
from __future__ import annotations

import sys

# Deferred import keeps backwards compatibility with existing entry point.
from ..publish_content import main  # type: ignore  # noqa: F401


if __name__ == "__main__":
    sys.exit(main())
