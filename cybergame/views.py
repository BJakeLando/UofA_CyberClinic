from django.shortcuts import render, redirect, get_object_or_404

from .models import Grade, Scenario


def _score_key(number):
    return f"score_g{number}"


def _best_key(number):
    return f"best_g{number}"


def _scenarios(grade):
    return list(grade.scenarios.filter(active=True))


def grade_select(request):
    return render(request, "cybergame/grade_select.html", {"grades": Grade.objects.all()})


def start_grade(request, number):
    grade = get_object_or_404(Grade, number=number)
    request.session[_score_key(number)] = 0
    request.session[_best_key(number)] = 0
    return render(request, "cybergame/start.html", {"grade": grade, "total": len(_scenarios(grade))})


def question(request, number, index):
    grade = get_object_or_404(Grade, number=number)
    scenarios = _scenarios(grade)

    if index < 0 or index >= len(scenarios):
        return redirect("cybergame:results", number=number)

    scenario = scenarios[index]
    choices = list(scenario.choices.all())
    best_points = max((c.points for c in choices), default=0)

    chosen = None
    if request.method == "POST":
        chosen_id = request.POST.get("choice")
        chosen = next((c for c in choices if str(c.pk) == chosen_id), None)
        if chosen and not request.session.get(f"answered_{number}_{index}"):
            request.session[_score_key(number)] = (
                request.session.get(_score_key(number), 0) + chosen.points
            )
            if chosen.points == best_points:
                request.session[_best_key(number)] = request.session.get(_best_key(number), 0) + 1
            request.session[f"answered_{number}_{index}"] = True

    return render(
        request,
        "cybergame/question.html",
        {
            "grade": grade,
            "scenario": scenario,
            "choices": choices,
            "chosen": chosen,
            "best_points": best_points,
            "index": index,
            "number_shown": index + 1,
            "total": len(scenarios),
            "next_index": index + 1,
            "is_last": index + 1 >= len(scenarios),
            "score": request.session.get(_score_key(number), 0),
        },
    )


def results(request, number):
    grade = get_object_or_404(Grade, number=number)
    scenarios = _scenarios(grade)
    total_possible = sum(
        max((c.points for c in s.choices.all()), default=0) for s in scenarios
    )

    for i in range(len(scenarios)):
        request.session.pop(f"answered_{number}_{i}", None)

    return render(
        request,
        "cybergame/results.html",
        {
            "grade": grade,
            "score": request.session.get(_score_key(number), 0),
            "best_count": request.session.get(_best_key(number), 0),
            "total": len(scenarios),
            "total_possible": total_possible,
        },
    )