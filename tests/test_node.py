from pathlib import Path

import pytest

from prumo import node
from prumo.node import (
    NodePrerequisiteError,
    detect_node_toolchain,
    is_node_version_compatible,
    parse_node_version,
)


@pytest.mark.parametrize(
    ("raw_version", "compatible"),
    [
        ("v20.19.0", True),
        ("v20.18.0", False),
        ("v22.12.0", True),
        ("v22.11.0", False),
        ("v23.0.0", True),
        ("v18.20.0", False),
    ],
)
def test_node_version_compatibility(
    raw_version: str,
    compatible: bool,
) -> None:
    version = parse_node_version(raw_version)

    assert version is not None
    assert is_node_version_compatible(version) is compatible


@pytest.mark.parametrize(
    ("available", "expected_message"),
    [
        ({}, "Node.js"),
        ({"node": "node.exe"}, "npm"),
    ],
)
def test_detect_node_toolchain_reports_missing_executable(
    available: dict[str, str],
    expected_message: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(node.shutil, "which", available.get)

    with pytest.raises(NodePrerequisiteError, match=expected_message):
        detect_node_toolchain()


def test_detect_node_toolchain_rejects_unreadable_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        node.shutil,
        "which",
        lambda name: str(Path(name)),
    )
    monkeypatch.setattr(node, "_read_node_version", lambda _executable: "unknown")

    with pytest.raises(NodePrerequisiteError, match="interpretar"):
        detect_node_toolchain()
