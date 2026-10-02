from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from .handles import (AVATARS, is_known_avatar, make_handle,
                      make_room_code, normalise_code)
from .models import Classroom, Completion, Grade, Player, Track

# One friendly animal per grade, shown on the grade buttons
GRADE_BUDDIES = {3: "🐢", 4: "🦊", 5: "🦉", 6: "🦁"}

TRACK_ORDER = ["beginner", "intermediate", "advanced"]

TRACK_LOOK = {
    "beginner":     {"emoji": "🌱", "blurb": "Words and pictures, with hints"},
    "intermediate": {"emoji": "⚡", "blurb": "Real screens, hints still on"},
    "advanced":     {"emoji": "🔥", "blurb": "Real screens, no hints"},
}

# Ranks a player climbs as points add up.
RANKS = [
    (0,   "Cyber Cadet",   "🌱"),
    (25,  "Cyber Scout",   "🔎"),
    (60,  "Cyber Guard",   "🛡️"),
    (110, "Cyber Hero",    "⭐"),
    (180, "Cyber Legend",  "👑"),
]

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


# --------------------------------------------------------------------------
# player helpers
# --------------------------------------------------------------------------

def rank_for(points):
    name, emoji = RANKS[0][1], RANKS[0][2]
    for floor, n, e in RANKS:
        if points >= floor:
            name, emoji = n, e
    return name, emoji


def next_rank(points):
    for floor, name, emoji in RANKS:
        if points < floor:
            return {"name": name, "emoji": emoji, "need": floor - points}
    return None


def current_player(request):
    pid = request.session.get("player_id")
    if not pid:
        return None
    player = Player.objects.filter(pk=pid).first()
    if player is None:
        request.session.pop("player_id", None)
    return player


def _needs_player(request):
    """Send anyone without a squad card back to the avatar picker."""
    return redirect("cybergame:avatar_select")


def _scenarios(track):
    return list(track.scenarios.filter(active=True).prefetch_related("choices"))


def _best_points(scenario):
    return max((c.points for c in scenario.choices.all()), default=0)


def _track_points(player, track):
    if player is None:
        return 0
    return (
        Completion.objects.filter(player=player, scenario__track=track)
        .aggregate(n=Sum("points"))["n"] or 0
    )


def _missed_indexes(player, scenarios):
    """Positions in this track the player has not yet aced."""
    if player is None:
        return []
    done = {
        c.scenario_id: c
        for c in Completion.objects.filter(
            player=player, scenario__in=[s.pk for s in scenarios]
        )
    }
    out = []
    for i, s in enumerate(scenarios):
        c = done.get(s.pk)
        if c is None or c.points < c.best_possible:
            out.append(i)
    return out


def _player_context(player):
    if player is None:
        return {"player": None}
    name, emoji = rank_for(player.total_points)
    return {
        "player": player,
        "room": player.classroom,
        "rank_name": name,
        "rank_emoji": emoji,
        "next_rank": next_rank(player.total_points),
    }


# --------------------------------------------------------------------------
# 1. avatar + handle
# --------------------------------------------------------------------------

def home(request):
    """The chooser. Always reachable.

    This used to redirect to grade select as soon as the session held a
    player, which meant that after one solo game there was no way back to
    "join my class" or "I'm a teacher" short of clearing cookies. Now the
    landing page shows a Keep Playing button instead of hiding itself.
    """
    return render(
        request,
        "cybergame/landing.html",
        {"my_rooms": my_rooms(request), **_player_context(current_player(request))},
    )


# --------------------------------------------------------------------------
# rooms
# --------------------------------------------------------------------------

def privacy(request):
    """Plain-language privacy notice, for parents and school reviewers.

    Every claim on that page is checked against this code. If the app starts
    collecting something new, the page is wrong until it is updated.
    """
    return render(request, "cybergame/privacy.html", {})


def pending_room(request):
    """The room a player is about to join, held between join and claim."""
    rid = request.session.get("join_room_id")
    return Classroom.objects.filter(pk=rid, active=True).first() if rid else None


def my_rooms(request):
    """Rooms made from this browser, newest first.

    A teacher who makes a room needs the code back after they navigate
    away, so we remember the ids in their session. Deliberately session
    scoped: nothing identifies a teacher, so there is nothing to look a
    room up by, and a room that outlives the session is a room nobody is
    watching. Make a fresh one next lesson.
    """
    ids = request.session.get("my_room_ids") or []
    if not ids:
        return []
    rooms = {r.pk: r for r in Classroom.objects.filter(pk__in=ids, active=True)}
    return [rooms[i] for i in reversed(ids) if i in rooms]


def remember_room(request, room):
    ids = request.session.get("my_room_ids") or []
    if room.pk not in ids:
        ids.append(room.pk)
        request.session["my_room_ids"] = ids[-20:]


def join_room(request):
    """Type the code the teacher put on the board."""
    error = None
    if request.method == "POST":
        code = normalise_code(request.POST.get("code"))
        room = Classroom.objects.filter(code=code, active=True).first()
        if room:
            request.session["join_room_id"] = room.pk
            return redirect("cybergame:avatar_select")
        error = "We could not find that room. Check the numbers and try again."
    return render(request, "cybergame/join_room.html", {"error": error})


def play_solo(request):
    request.session.pop("join_room_id", None)
    return redirect("cybergame:avatar_select")


def teacher(request):
    """Make a room, and get the code back afterwards."""
    if request.method == "POST":
        label = (request.POST.get("label") or "").strip()[:60]
        taken = set(Classroom.objects.values_list("code", flat=True))
        room = Classroom.objects.create(code=make_room_code(taken), label=label)
        remember_room(request, room)
        return render(request, "cybergame/room_made.html", {"room": room})
    return render(request, "cybergame/teacher.html", {"my_rooms": my_rooms(request)})


def avatar_select(request):
    return render(
        request,
        "cybergame/avatar_select.html",
        {"avatars": [{"emoji": e, "word": w} for e, w in AVATARS],
         "room": pending_room(request),
         **_player_context(current_player(request))},
    )


def claim_avatar(request):
    if request.method != "POST":
        return redirect("cybergame:avatar_select")

    emoji = request.POST.get("avatar", "")
    if not is_known_avatar(emoji):
        return redirect("cybergame:avatar_select")

    room = pending_room(request)
    # handles only have to be unique inside the room
    taken = set(
        Player.objects.filter(classroom=room).values_list("handle", flat=True)
    )
    player = Player.objects.create(
        classroom=room, handle=make_handle(emoji, taken), avatar=emoji
    )
    request.session["player_id"] = player.pk
    request.session.pop("join_room_id", None)

    return render(request, "cybergame/squad_card.html", {**_player_context(player)})


def leave(request):
    """Let go of this squad name and go back to the chooser.

    The Player row and its points stay in the database and on the room's
    board; this session just stops being that player. There is no way
    back into it, which the confirm screen says out loud.

    POST only. As a GET this was one browser link prefetch away from
    silently throwing out a kid's squad name and their stars.
    """
    if request.method != "POST":
        return redirect("cybergame:home")

    request.session.pop("player_id", None)
    request.session.pop("join_room_id", None)
    return redirect("cybergame:home")


# --------------------------------------------------------------------------
# 2 + 3. grade, then difficulty
# --------------------------------------------------------------------------

def grade_select(request):
    player = current_player(request)
    if player is None:
        return _needs_player(request)

    grades = list(Grade.objects.all())
    for g in grades:
        g.buddy = GRADE_BUDDIES.get(g.number, "⭐")
    return render(request, "cybergame/grade_select.html",
                  {"grades": grades, **_player_context(player)})


def difficulty_select(request, number):
    player = current_player(request)
    if player is None:
        return _needs_player(request)

    grade = get_object_or_404(Grade, number=number)
    have = {t.difficulty: t for t in grade.tracks.all()}

    tracks = []
    for slug in TRACK_ORDER:
        look = TRACK_LOOK[slug]
        t = have.get(slug)
        scens = _scenarios(t) if t else []
        earned = _track_points(player, t) if t else 0
        possible = sum(_best_points(s) for s in scens)
        tracks.append({
            "slug": slug,
            "name": slug.title(),
            "emoji": (t.emoji if t and t.emoji else look["emoji"]),
            "blurb": (t.blurb if t and t.blurb else look["blurb"]),
            "ready": bool(scens),
            "count": len(scens),
            "earned": earned,
            "possible": possible,
            "done": bool(scens) and earned >= possible,
            "started": earned > 0,
        })

    return render(request, "cybergame/difficulty_select.html",
                  {"grade": grade, "buddy": GRADE_BUDDIES.get(number, "⭐"),
                   "tracks": tracks, **_player_context(player)})


def _get_track(number, difficulty):
    grade = get_object_or_404(Grade, number=number)
    track = get_object_or_404(Track, grade=grade, difficulty=difficulty)
    return grade, track


def start_track(request, number, difficulty):
    player = current_player(request)
    if player is None:
        return _needs_player(request)

    grade, track = _get_track(number, difficulty)
    scens = _scenarios(track)
    return render(request, "cybergame/start.html",
                  {"grade": grade, "track": track,
                   "buddy": GRADE_BUDDIES.get(number, "⭐"),
                   "total": len(scens),
                   "earned": _track_points(player, track),
                   "possible": sum(_best_points(s) for s in scens),
                   **_player_context(player)})


# --------------------------------------------------------------------------
# 4 + 5. play, and go back for the misses
# --------------------------------------------------------------------------

def question(request, number, difficulty, index):
    player = current_player(request)
    if player is None:
        return _needs_player(request)

    grade, track = _get_track(number, difficulty)
    scenarios = _scenarios(track)

    if index < 0 or index >= len(scenarios):
        return redirect("cybergame:results", number=number, difficulty=difficulty)

    scenario = scenarios[index]
    choices = list(scenario.choices.all())
    best_points = _best_points(scenario)
    best_choice = next((c for c in choices if c.points == best_points), None)
    hotspots = {c.hotspot: c for c in choices if c.hotspot}

    chosen = None
    tier = None
    gained = 0

    if request.method == "POST":
        chosen = next((c for c in choices if str(c.pk) == request.POST.get("choice")), None)
        if chosen:
            comp, created = Completion.objects.get_or_create(
                player=player, scenario=scenario,
                defaults={"points": chosen.points, "best_possible": best_points,
                          "attempts": 1,
                          "first_try_best": chosen.points >= best_points},
            )
            if created:
                gained = chosen.points
            else:
                # a replay can only ever raise the score
                comp.attempts += 1
                comp.best_possible = best_points
                if chosen.points > comp.points:
                    gained = chosen.points - comp.points
                    comp.points = chosen.points
                comp.save()

            if gained:
                Player.objects.filter(pk=player.pk).update(
                    total_points=player.total_points + gained
                )
                player.refresh_from_db()

            tier = ("best" if chosen.points == best_points
                    else "ok" if chosen.points > 0 else "try")

    heads = {"best": ("🌟", "Best move!"), "ok": ("👍", "Good!"),
             "try": ("🤔", "Hmm, not quite.")}
    result_emoji, result_head = heads.get(tier, ("", ""))

    done_ids = set(
        Completion.objects.filter(player=player, scenario__in=[s.pk for s in scenarios])
        .values_list("scenario_id", flat=True)
    )
    dots = ["now" if i == index else ("done" if s.pk in done_ids else "todo")
            for i, s in enumerate(scenarios)]

    return render(request, "cybergame/question.html",
                  {"grade": grade, "track": track, "scenario": scenario,
                   "choices": choices, "hotspots": hotspots,
                   "chosen": chosen, "best_choice": best_choice, "tier": tier,
                   "result_emoji": result_emoji, "result_head": result_head,
                   "gained": gained, "dots": dots,
                   "number_shown": index + 1, "total": len(scenarios),
                   "next_index": index + 1,
                   "is_last": index + 1 >= len(scenarios),
                   "score": _track_points(player, track),
                   **_player_context(player)})


def fix_next(request, number, difficulty):
    """Jump to the next scenario in this track that isn't perfect yet."""
    player = current_player(request)
    if player is None:
        return _needs_player(request)

    grade, track = _get_track(number, difficulty)
    missed = _missed_indexes(player, _scenarios(track))
    if not missed:
        return redirect("cybergame:results", number=number, difficulty=difficulty)
    return redirect("cybergame:question", number=number,
                    difficulty=difficulty, index=missed[0])


def results(request, number, difficulty):
    player = current_player(request)
    if player is None:
        return _needs_player(request)

    grade, track = _get_track(number, difficulty)
    scenarios = _scenarios(track)
    total_possible = sum(_best_points(s) for s in scenarios)
    score = _track_points(player, track)

    ratio = score / total_possible if total_possible else 0
    stars = 3 if ratio >= 0.85 else 2 if ratio >= 0.6 else 1
    missed = _missed_indexes(player, scenarios)

    return render(request, "cybergame/results.html",
                  {"grade": grade, "track": track, "score": score,
                   "total_possible": total_possible, "stars": stars,
                   "cheer": {3: "Amazing!", 2: "Great job!", 1: "Nice try!"}[stars],
                   "star_slots": [i < stars for i in range(3)],
                   "rules": RULES,
                   "missed_count": len(missed),
                   "perfect": not missed,
                   **_player_context(player)})


# --------------------------------------------------------------------------
# 6. leaderboard
# --------------------------------------------------------------------------

def leaderboard(request):
    player = current_player(request)
    room = player.classroom if player else None

    # A teacher has no player, so without this they saw an empty board for
    # their own class. ?room=<code> is checked against the rooms this
    # browser actually made, so a guessed code cannot open someone else's.
    as_teacher = False
    wanted = normalise_code(request.GET.get("room"))
    if wanted:
        mine = {r.code: r for r in my_rooms(request)}
        if wanted in mine:
            room, player, as_teacher = mine[wanted], None, True

    # One indexed scan over a single room, never a global sort.
    top = list(Player.objects.filter(classroom=room)[:20]) if (player or room) else []

    rows = []
    for i, p in enumerate(top, start=1):
        name, emoji = rank_for(p.total_points)
        rows.append({"place": i, "player": p, "rank_name": name,
                     "rank_emoji": emoji, "is_me": player and p.pk == player.pk})

    me_in_top = any(r["is_me"] for r in rows)
    context = {"rows": rows, "me_in_top": me_in_top,
               "my_rank": player.rank if player else None,
               "total_players": Player.objects.filter(classroom=room).count(),
               "solo": player is not None and room is None,
               "as_teacher": as_teacher,
               **_player_context(player)}
    if as_teacher:
        # _player_context only carries a room when there is a player
        context["room"] = room
    return render(request, "cybergame/leaderboard.html", context)
