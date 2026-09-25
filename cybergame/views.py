from django.shortcuts import render, redirect, get_object_or_404

from .models import Grade

# One friendly animal per grade, shown on the grade buttons
GRADE_BUDDIES = {3: "🐢", 4: "🦊", 5: "🦉", 6: "🦁"}


def _key(number, name):
    return f"g{number}_{name}"


def _scenarios(grade):
    return list(grade.scenarios.filter(active=True).prefetch_related("choices"))


def _reset(session, number):
    prefix = f"g{number}_"
    for k in [k for k in session.keys() if k.startswith(prefix)]:
        del session[k]


def grade_select(request):
    grades = list(Grade.objects.all())
    for g in grades:
        g.buddy = GRADE_BUDDIES.get(g.number, "⭐")
    return render(request, "cybergame/grade_select.html", {"grades": grades})


def start_grade(request, number):
    grade = get_object_or_404(Grade, number=number)
    _reset(request.session, number)
    request.session[_key(number, "score")] = 0
    return render(
        request,
        "cybergame/start.html",
        {
            "grade": grade,
            "buddy": GRADE_BUDDIES.get(number, "⭐"),
            "total": len(_scenarios(grade)),
        },
    )


def question(request, number, index):
    grade = get_object_or_404(Grade, number=number)
    scenarios = _scenarios(grade)

    if index < 0 or index >= len(scenarios):
        return redirect("cybergame:results", number=number)

    scenario = scenarios[index]
    choices = list(scenario.choices.all())
    best_points = max((c.points for c in choices), default=0)
    best_choice = next((c for c in choices if c.points == best_points), None)

    chosen = None
    tier = None
    if request.method == "POST":
        chosen = next((c for c in choices if str(c.pk) == request.POST.get("choice")), None)
        if chosen:
            answered_key = _key(number, f"answered_{index}")
            if not request.session.get(answered_key):
                request.session[_key(number, "score")] = (
                    request.session.get(_key(number, "score"), 0) + chosen.points
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
            "scenario": scenario,
            "choices": choices,
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
            "score": request.session.get(_key(number, "score"), 0),
        },
    )


def results(request, number):
    grade = get_object_or_404(Grade, number=number)
    scenarios = _scenarios(grade)
    total_possible = sum(max((c.points for c in s.choices.all()), default=0) for s in scenarios)
    score = request.session.get(_key(number, "score"), 0)

    ratio = score / total_possible if total_possible else 0
    stars = 3 if ratio >= 0.85 else 2 if ratio >= 0.6 else 1

    return render(
        request,
        "cybergame/results.html",
        {
            "grade": grade,
            "score": score,
            "total_possible": total_possible,
            "stars": stars,
            "cheer": {3: "Amazing!", 2: "Great job!", 1: "Nice try!"}[stars],
            "star_slots": [i < stars for i in range(3)],
        },
    )
