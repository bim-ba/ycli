"""Pydantic v2 models for Yandex Wiki /recovery_tokens responses (extra='ignore')."""

from __future__ import annotations

from ycli.yandex.wiki.models import PageIdentity

RecoveredPage = PageIdentity  # deprecated, removed in 0.38
