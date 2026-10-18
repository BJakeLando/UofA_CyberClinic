from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Choice, Completion, Grade, Player, Scenario, Track

GIRL_SCOUTS = 100


# Production serves hashed static files from a manifest that only exists
# after collectstatic, and redirects everything to https. Neither matters
# to these tests, so they run without a build step or a proxy in front.
@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
    SECURE_SSL_REDIRECT=False,
)
class SeededTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_content", stdout=open("/dev/null", "w"))

    def play_as_new_player(self):
        player = Player.objects.create(handle="TestFox1", avatar="🦊")
        session = self.client.session
        session["player_id"] = player.pk
        session.save()
        return player


class MeetingQuestionTests(SeededTestCase):
    """A stranger asking to meet: don't reply at all, just tell."""

    def meeting_scenarios(self):
        return Scenario.objects.filter(choices__text="Go meet them").distinct()

    def test_every_grade_with_a_meeting_question_is_covered(self):
        self.assertEqual(
            sorted(self.meeting_scenarios().values_list("grade__number", flat=True)),
            [3, 4, 6],
        )

    def test_no_answer_involves_saying_anything_back(self):
        for s in self.meeting_scenarios():
            for c in s.choices.all():
                self.assertNotIn("say no", c.text.lower(), s.prompt)

    def test_two_answers_and_telling_is_best(self):
        for s in self.meeting_scenarios():
            answers = {c.text: c.points for c in s.choices.all()}
            self.assertEqual(answers, {"Tell family or teacher": 2, "Go meet them": 0},
                             s.prompt)


class GirlScoutsTests(SeededTestCase):

    def test_is_a_group_not_a_grade(self):
        group = Grade.objects.get(number=GIRL_SCOUTS)
        self.assertTrue(group.is_group)
        self.assertEqual(group.title, "Girl Scouts")
        self.assertEqual(Grade.objects.get(number=6).title, "Grade 6")

    def test_has_only_the_advanced_level(self):
        group = Grade.objects.get(number=GIRL_SCOUTS)
        self.assertEqual([t.difficulty for t in group.tracks.all()], ["advanced"])
        self.assertFalse(group.tracks.get().show_hints)

    def test_mirrors_6th_grade_advanced(self):
        """Same scenes, same order, same answers and points. Only wording differs."""
        def shape(track):
            return [
                (s.kind, s.stage, [(c.hotspot, c.points) for c in s.choices.all()])
                for s in track.scenarios.order_by("order")
            ]

        sixth = Track.objects.get(grade__number=6, difficulty="advanced")
        scouts = Track.objects.get(grade__number=GIRL_SCOUTS, difficulty="advanced")
        self.assertEqual(shape(scouts), shape(sixth))

    def test_shows_on_the_picker_and_skips_the_level_screen(self):
        self.play_as_new_player()
        picker = self.client.get(reverse("cybergame:grade_select"))
        self.assertContains(picker, "Girl Scouts")

        levels = self.client.get(reverse("cybergame:difficulty_select", args=[GIRL_SCOUTS]))
        self.assertRedirects(
            levels, reverse("cybergame:start_track", args=[GIRL_SCOUTS, "advanced"]))

    def test_back_links_return_to_the_picker(self):
        """Not to the level screen, which would bounce straight back."""
        self.play_as_new_player()
        start = self.client.get(reverse("cybergame:start_track", args=[GIRL_SCOUTS, "advanced"]))
        self.assertContains(start, 'href="%s"' % reverse("cybergame:grade_select"))
        self.assertNotContains(
            start, 'href="%s"' % reverse("cybergame:difficulty_select", args=[GIRL_SCOUTS]))

    def test_can_play_a_round_and_score(self):
        player = self.play_as_new_player()
        url = reverse("cybergame:question", args=[GIRL_SCOUTS, "advanced", 0])
        page = self.client.get(url)
        self.assertContains(page, "theme-girl-scouts")
        self.assertContains(page, "⛺")

        scene = Track.objects.get(grade__number=GIRL_SCOUTS).scenarios.get(order=0)
        report = scene.choices.get(hotspot="report")
        self.client.post(url, {"choice": report.pk})
        player.refresh_from_db()
        self.assertEqual(player.total_points, 2)

    def test_grades_still_get_the_level_screen(self):
        self.play_as_new_player()
        page = self.client.get(reverse("cybergame:difficulty_select", args=[6]))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Grade 6")


class ReseedKeepsProgressTests(SeededTestCase):
    """Deploys run seed_content every time. Nobody's stars may move."""

    def test_reseed_keeps_completions_and_choices_stable(self):
        player = Player.objects.create(handle="TestFox1", avatar="🦊", total_points=2)
        scene = Scenario.objects.filter(choices__text="Go meet them").first()
        Completion.objects.create(player=player, scenario=scene, points=2, best_possible=2)
        before = (Scenario.objects.count(), Choice.objects.count())

        call_command("seed_content", stdout=open("/dev/null", "w"))

        self.assertEqual((Scenario.objects.count(), Choice.objects.count()), before)
        self.assertTrue(Completion.objects.filter(player=player, scenario=scene).exists())
