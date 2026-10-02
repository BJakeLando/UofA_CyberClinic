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
