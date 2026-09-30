from django.shortcuts import render, redirect, get_object_or_404

from .models import Grade, Track

# One friendly animal per grade, shown on the grade buttons
GRADE_BUDDIES = {3: "🐢", 4: "🦊", 5: "🦉", 6: "🦁"}

# Difficulty lanes, in the order they appear after a grade is picked.
# Anything missing from the database is still shown, greyed out, so a
# half-seeded install never renders a blank page.
TRACK_ORDER = ["beginner", "intermediate", "advanced"]

TRACK_LOOK = {
    "beginner":     {"emoji": "🌱", "blurb": "Words and pictures, with hints"},
    "intermediate": {"emoji": "⚡", "blurb": "Real screens, hints still on"},
    "advanced":     {"emoji": "🔥", "blurb": "Real screens, no hints"},
}

# Results page. Each rule opens to a longer explanation on hover or tap.
RULES = [
    {
        "emoji": "🎁",
        "short": "Free prizes are tricks",
        "detail": "Real games never give away free stuff for messaging someone. "
                  "A free prize is bait to get your password or your account.",
    },
    {
        "emoji": "🔑",
        "short": "Keep your password secret",
        "detail": "Nobody who really works for a game will ever ask for your password. "
                  "Not a helper, not a moderator, not even a friend.",
    },
    {
        "emoji": "🏠",
        "short": "Keep your name and home private",
        "detail": "Your real name, your school, and your address are how a stranger "
                  "finds you in real life. Keep them off the screen.",
    },
    {
        "emoji": "🗝️",
        "short": "Have a secret family code word",
        "detail": "AI can copy voices so they sound just like your parents. A secret "
                  "code word that only your family knows is a good way to check that "
                  "you are really talking to your family. Never post it online.",
    },
    {
        "emoji": "🚫",
        "short": "Never go meet game friends",
        "detail": "People online can say they are any age. Someone who wants to meet "
                  "you in person is not a friend you can trust.",
    },
    {
        "emoji": "🙋",
        "short": "Always tell a teacher or family member",
        "detail": "You will not get in trouble for telling. Telling quickly is what "
                  "makes a problem easy to fix.",
    },
]


def _key(number, difficulty, name):
    return f"g{number}_{difficulty}_{name}"


def _scenarios(track):
    return list(track.scenarios.filter(active=True).prefetch_related("choices"))


def _reset(session, number, difficulty):
    prefix = f"g{number}_{difficulty}_"
    for k in [k for k in session.keys() if k.startswith(prefix)]:
        del session[k]


def _get_track(number, difficulty):
    grade = get_object_or_404(Grade, number=number)
    track = get_object_or_404(Track, grade=grade, difficulty=difficulty)
    return grade, track


def grade_select(request):
    grades = list(Grade.objects.all())
    for g in grades:
        g.buddy = GRADE_BUDDIES.get(g.number, "⭐")
    return render(request, "cybergame/grade_select.html", {"grades": grades})


def difficulty_select(request, number):
    grade = get_object_or_404(Grade, number=number)
    have = {t.difficulty: t for t in grade.tracks.all()}

    tracks = []
    for slug in TRACK_ORDER:
        look = TRACK_LOOK[slug]
        t = have.get(slug)
        tracks.append({
            "slug": slug,
            "name": slug.title(),
            "emoji": (t.emoji if t and t.emoji else look["emoji"]),
            "blurb": (t.blurb if t and t.blurb else look["blurb"]),
            "ready": t is not None and t.scenarios.filter(active=True).exists(),
            "count": t.scenarios.filter(active=True).count() if t else 0,
        })

    return render(
        request,
        "cybergame/difficulty_select.html",
        {"grade": grade, "buddy": GRADE_BUDDIES.get(number, "⭐"), "tracks": tracks},
    )


def start_track(request, number, difficulty):
    grade, track = _get_track(number, difficulty)
    _reset(request.session, number, difficulty)
    request.session[_key(number, difficulty, "score")] = 0
    return render(
        request,
        "cybergame/start.html",
        {
            "grade": grade,
            "track": track,
            "buddy": GRADE_BUDDIES.get(number, "⭐"),
            "total": len(_scenarios(track)),
        },
    )


def question(request, number, difficulty, index):
    grade, track = _get_track(number, difficulty)
    scenarios = _scenarios(track)

    if index < 0 or index >= len(scenarios):
        return redirect("cybergame:results", number=number, difficulty=difficulty)

    scenario = scenarios[index]
    choices = list(scenario.choices.all())
    best_points = max((c.points for c in choices), default=0)
    best_choice = next((c for c in choices if c.points == best_points), None)

    # Device scenes put their answers on the screen instead of in a list.
    hotspots = {c.hotspot: c for c in choices if c.hotspot}

    chosen = None
    tier = None
    if request.method == "POST":
        chosen = next((c for c in choices if str(c.pk) == request.POST.get("choice")), None)
        if chosen:
            answered_key = _key(number, difficulty, f"answered_{index}")
            if not request.session.get(answered_key):
                request.session[_key(number, difficulty, "score")] = (
                    request.session.get(_key(number, difficulty, "score"), 0) + chosen.points
                )
                request.session[answered_key] = True
            if chosen.points == best_points:
                tier = "best"
            elif chosen.points > 0:
                tier = "ok"
            else:
                tier = "try"

    heads = {
        "best": ("🌟", "Best move!"),
        "ok": ("👍", "Good!"),
        "try": ("🤔", "Hmm, not quite."),
    }
    result_emoji, result_head = heads.get(tier, ("", ""))

    dots = [
        "done" if i < index else "now" if i == index else "todo"
        for i in range(len(scenarios))
    ]

    return render(
        request,
        "cybergame/question.html",
        {
            "grade": grade,
            "track": track,
            "scenario": scenario,
            "choices": choices,
            "hotspots": hotspots,
            "chosen": chosen,
            "best_choice": best_choice,
            "tier": tier,
            "result_emoji": result_emoji,
            "result_head": result_head,
            "dots": dots,
            "number_shown": index + 1,
            "total": len(scenarios),
            "next_index": index + 1,
            "is_last": index + 1 >= len(scenarios),
            "score": request.session.get(_key(number, difficulty, "score"), 0),
        },
    )


def results(request, number, difficulty):
    grade, track = _get_track(number, difficulty)
    scenarios = _scenarios(track)
    total_possible = sum(max((c.points for c in s.choices.all()), default=0) for s in scenarios)
    score = request.session.get(_key(number, difficulty, "score"), 0)

    ratio = score / total_possible if total_possible else 0
    stars = 3 if ratio >= 0.85 else 2 if ratio >= 0.6 else 1

    return render(
        request,
        "cybergame/results.html",
        {
            "grade": grade,
            "track": track,
            "score": score,
            "total_possible": total_possible,
            "stars": stars,
            "cheer": {3: "Amazing!", 2: "Great job!", 1: "Nice try!"}[stars],
            "star_slots": [i < stars for i in range(3)],
            "rules": RULES,
        },
    )
