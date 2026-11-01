"""No-mistakes badges.

    Beginner     -> Cyber Scout
    Intermediate -> Cyber Warrior
    Advanced     -> Cyber Wizard

A player earns a level's badge by finishing every round of one track at that
level (any grade, or Girl Scouts) with the best move on the FIRST try. The
game already records that on each Completion (first_try_best), so nothing
new is collected about the child: the badge belongs to the generated squad
name, and the printable certificate shows that name and nothing else.

Fixing a miss afterwards still earns the stars but not the badge for that
track. Another grade's track at the same level is a fresh chance.
"""

from math import cos, pi, sin

from .models import Award, Completion


def _rosette(cx, cy, r_out, r_in, points):
    """The scalloped outer edge of a medal, as an SVG polygon."""
    out = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = pi * i / points - pi / 2
        out.append(f"{cx + r * cos(a):.1f},{cy + r * sin(a):.1f}")
    return " ".join(out)


ROSETTE = _rosette(100, 96, 92, 83, 24)

# Tier stars across the top of the medal: one, two or three.
STAR_X = {1: [100], 2: [91, 109], 3: [82, 100, 118]}

BADGES = [
    {
        "slug": "scout", "name_size": 17, "level": "beginner", "level_name": "Beginner",
        "name": "Cyber Scout", "tier": 1, "motto": "Spots every trick",
        "core1": "#33d68b", "core2": "#0b6e3f",
        "rim1": "#fff4b8", "rim2": "#e6b43c", "rim3": "#9c6a12",
        "ribbon": "#14a061", "ribbon_dark": "#0b5e38", "accent": "#ffd23f",
    },
    {
        "slug": "warrior", "name_size": 15, "level": "intermediate", "level_name": "Intermediate",
        "name": "Cyber Warrior", "tier": 2, "motto": "Never takes the bait",
        "core1": "#4fb0ff", "core2": "#123c8c",
        "rim1": "#ffffff", "rim2": "#c3cfe0", "rim3": "#5f6f8c",
        "ribbon": "#1d63d6", "ribbon_dark": "#123f8a", "accent": "#ffd23f",
    },
    {
        "slug": "wizard", "name_size": 16, "level": "advanced", "level_name": "Advanced",
        "name": "Cyber Wizard", "tier": 3, "motto": "Outsmarts every scam",
        "core1": "#a98bff", "core2": "#33168a",
        "rim1": "#fff3a6", "rim2": "#ffb13d", "rim3": "#c2408a",
        "ribbon": "#6b3fe0", "ribbon_dark": "#3f208f", "accent": "#ffd23f",
    },
]

for _b in BADGES:
    _b["rosette"] = ROSETTE
    _b["stars"] = STAR_X[_b["tier"]]

BY_LEVEL = {b["level"]: b for b in BADGES}
BY_SLUG = {b["slug"]: b for b in BADGES}


def mistakes(player, track):
    """Rounds in this track the player missed on the first try (None = not finished)."""
    ids = list(track.scenarios.filter(active=True).values_list("pk", flat=True))
    done = Completion.objects.filter(player=player, scenario_id__in=ids)
    if not ids or done.count() < len(ids):
        return None
    return done.filter(first_try_best=False).count()


def check_award(player, track):
    """Award this track's badge if it was just earned. Returns (award, is_new)."""
    badge = BY_LEVEL.get(track.difficulty)
    if badge is None:
        return None, False
    have = player.awards.filter(badge=badge["slug"]).first()
    if have:
        return have, False
    if mistakes(player, track) != 0:
        return None, False
    award, created = Award.objects.get_or_create(
        player=player, badge=badge["slug"], defaults={"track": track})
    return award, created


def player_badges(player):
    """All three badges, each with the player's award or None."""
    have = {a.badge: a for a in player.awards.select_related("track__grade")}
    return [{**b, "award": have.get(b["slug"])} for b in BADGES]


def where_earned(award):
    """'Grade 4 · Beginner' or 'Girl Scouts · Advanced'."""
    t = award.track
    if t is None:
        return BY_SLUG[award.badge]["level_name"]
    return f"{t.grade.title} · {t.get_difficulty_display()}"
