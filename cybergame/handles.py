"""Avatars and generated handles.

A child never types a name. They tap an animal, and the game hands them
a handle built from that animal. Nothing identifying is collected, so
there is nothing identifying to leak, and the leaderboard is safe to
show to a whole class.
"""

import random

# (emoji, word used in the handle)
AVATARS = [
    ("🦊", "Fox"),      ("🐧", "Penguin"),  ("🦉", "Owl"),      ("🐢", "Turtle"),
    ("🦁", "Lion"),     ("🐨", "Koala"),    ("🦈", "Shark"),    ("🐙", "Octopus"),
    ("🦔", "Hedgehog"), ("🐝", "Bee"),      ("🦅", "Eagle"),    ("🐺", "Wolf"),
    ("🦝", "Raccoon"),  ("🐬", "Dolphin"),  ("🦋", "Butterfly"),("🐸", "Frog"),
    ("🐼", "Panda"),    ("🦀", "Crab"),     ("🦭", "Seal"),     ("🐲", "Dragon"),
]

AVATAR_WORD = dict(AVATARS)

ADJECTIVES = [
    "Red", "Blue", "Green", "Gold", "Silver", "Swift", "Brave", "Cyber",
    "Super", "Mega", "Turbo", "Shadow", "Rocket", "Ninja", "Pixel", "Thunder",
    "Sunny", "Lucky", "Mighty", "Cosmic", "Frost", "Blaze", "Storm", "Quantum",
]


def is_known_avatar(emoji):
    return emoji in AVATAR_WORD


def make_handle(emoji, taken=frozenset(), rng=None):
    """Build a handle like SwiftPenguin482 for the chosen avatar.

    `taken` is a set of handles already in use. The namespace is
    24 adjectives x 990 numbers per animal, so a collision is rare; if
    one happens we simply draw again, and widen the number as a backstop.
    """
    rng = rng or random
    word = AVATAR_WORD.get(emoji, "Agent")

    for _ in range(40):
        candidate = f"{rng.choice(ADJECTIVES)}{word}{rng.randint(10, 999)}"
        if candidate not in taken:
            return candidate

    # extremely unlikely; widen rather than fail
    while True:
        candidate = f"{rng.choice(ADJECTIVES)}{word}{rng.randint(1000, 999999)}"
        if candidate not in taken:
            return candidate


# ---------------------------------------------------------------------------
# Room codes
#
# Six digits, the way Kahoot and Blooket do it. Digits beat letters for a
# third grader copying a code off the whiteboard: no b/d confusion, no
# capitals, and the number row is one reach on a Chromebook.
# ---------------------------------------------------------------------------

ROOM_CODE_LEN = 6


def make_room_code(taken=frozenset(), rng=None):
    rng = rng or random
    lo, hi = 10 ** (ROOM_CODE_LEN - 1), 10 ** ROOM_CODE_LEN - 1
    for _ in range(60):
        code = str(rng.randint(lo, hi))
        if code not in taken:
            return code
    # pool is crowded; widen rather than spin
    n = ROOM_CODE_LEN + 1
    while True:
        code = str(rng.randint(10 ** (n - 1), 10 ** n - 1))
        if code not in taken:
            return code


def normalise_code(raw):
    """Kids paste spaces and dashes. Keep only the digits."""
    return "".join(ch for ch in (raw or "") if ch.isdigit())[:12]
