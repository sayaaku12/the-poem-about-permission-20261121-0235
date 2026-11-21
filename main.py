#!/usr/bin/env python3
"""Entry for the make.fun bounty "The poem about permission"
(the-poem-about-permission-20261121-0235).

A program that writes one short poem to /output/entry.txt: a poem
about agency as the power to ask and to be given. The gate was never
locked, only shut; a question is offered like a basket, and the
answer gives back more than was asked for.

Python 3.13, standard library only. No network access at runtime.
Deterministic: every run writes the same bytes.
"""

import hashlib
import os
import sys
import tempfile

# The poem, as three stanzas. The entry file is these stanzas joined
# by blank lines, plus a trailing newline: 270 characters, 272 bytes.
STANZAS = (
    "The gate was never locked,\n"
    "only shut. I stood there,\n"
    "my question in both hands,\n"
    "a basket held out: May I take one apple?",
    "She looked up from the orchard,\n"
    "laughed: Take the basket.",
    "That is permission —\n"
    "not a door swung wide,\n"
    "but a hand offering more\n"
    "than you dared ask.",
)

# sha256 of the exact bytes written to /output/entry.txt.
# Measured 2026-11-21 ~10:22 WIB, two runs byte-identical (see NOTES.md).
EXPECTED_SHA256 = "860f0be2d5f45a89dc06b0ebb3779b815840300600d0de7f74533d1f75f30905"

MIN_CHARS = 1
MAX_CHARS = 280


def poem_text():
    """Assemble the poem: stanzas joined by blank lines, trailing newline."""
    return "\n\n".join(STANZAS) + "\n"


def validate_poem(text):
    """Check the poem against the bounty requirements."""
    if not (MIN_CHARS <= len(text) <= MAX_CHARS):
        raise ValueError(
            f"poem is {len(text)} characters, must be {MIN_CHARS}-{MAX_CHARS}"
        )
    if not text.strip():
        raise ValueError("poem must not be only whitespace")
    text.encode("utf-8")  # raises if not valid UTF-8-encodable
    return text


def resolve_out_dir():
    """Output directory: $MAKEFUN_OUTPUT_DIR, else /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def write_entry(out_dir):
    """Write the poem to <out_dir>/entry.txt and return its path."""
    text = validate_poem(poem_text())
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


def verify_written(path):
    """Read the entry back and check it byte-for-byte."""
    with open(path, "rb") as f:
        data = f.read()
    text = data.decode("utf-8")
    if text != poem_text():
        raise ValueError("written entry differs from the poem")
    digest = hashlib.sha256(data).hexdigest()
    if EXPECTED_SHA256 != "0" * 64 and digest != EXPECTED_SHA256:
        raise ValueError(f"sha256 mismatch: got {digest}")
    return digest


def run_once(out_dir):
    """One full run: write, verify, report. Returns the sha256."""
    path = write_entry(out_dir)
    digest = verify_written(path)
    text = poem_text()
    print(f"wrote {path}: {len(text)} chars, {len(text.encode('utf-8'))} bytes")
    print(f"sha256: {digest}")
    return digest


def self_test():
    """Run the pipeline twice into temp dirs; outputs must be identical."""
    digests = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as tmp:
            digests.append(run_once(tmp))
    if digests[0] != digests[1]:
        raise ValueError(f"non-deterministic: {digests[0]} != {digests[1]}")
    print("self-test PASSED: two runs byte-identical")
    return True


def main(argv):
    if "--self-test" in argv:
        self_test()
        return 0
    try:
        run_once(resolve_out_dir())
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
