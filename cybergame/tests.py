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


class TwoAnswerRuleTests(SeededTestCase):
    """Wagner: no in-between answers anywhere. Engage, or tell. Nothing says "say no"."""

    def test_every_scene_at_every_level_has_two_answers_engage_or_tell(self):
        scenes = Scenario.objects.filter(active=True).select_related("grade", "track")
        self.assertGreater(scenes.count(), 80)
        for scene in scenes:
            where = f"{scene.grade.label} {scene.track.difficulty}: {scene.prompt}"
            self.assertEqual(sorted(c.points for c in scene.choices.all()), [0, 2], where)

    def test_nothing_says_say_no(self):
        self.assertFalse(Choice.objects.filter(text__icontains="say no").exists())

    def test_tablet_and_text_scenes_have_no_close_or_delete(self):
        self.assertFalse(Choice.objects.filter(hotspot="close").exists())
        for scene in Scenario.objects.filter(kind__in=["device", "text"]):
            hotspots = sorted(c.hotspot for c in scene.choices.all())
            self.assertEqual(hotspots, ["bait", "verify" if scene.kind == "text" else "report"])

    def test_tablet_screen_has_no_x_and_a_tell_button(self):
        self.play_as_new_player()
        page = self.client.get(reverse("cybergame:question", args=[3, "advanced", 0]))
        self.assertNotContains(page, 'class="ad-close"')
        self.assertContains(page, "</span> Tell")
        self.assertNotContains(page, "Report")

    def test_seed_refuses_a_three_answer_scene(self):
        from django.core.management.base import CommandError
        from cybergame.management.commands import seed_content as content

        bad = content.S("chat", "Bad scene", choices=[
            ("👋", "Say no", 1, "x"), ("🙋", "Tell", 2, "x"), ("🚶", "Go", 0, "x")])
        with self.assertRaises(CommandError):
            content.check("test", bad)


class GirlScoutsTests(SeededTestCase):

    def test_is_a_group_not_a_grade(self):
        group = Grade.objects.get(number=GIRL_SCOUTS)
        self.assertTrue(group.is_group)
        self.assertEqual(group.title, "Girl Scouts")
        self.assertEqual(Grade.objects.get(number=6).title, "Grade 6")

    def track(self):
        return Track.objects.get(grade__number=GIRL_SCOUTS)

    def test_has_only_the_beginner_level(self):
        group = Grade.objects.get(number=GIRL_SCOUTS)
        self.assertEqual([t.difficulty for t in group.tracks.all()], ["beginner"])
        self.assertTrue(group.tracks.get().show_hints)

    def test_hiking_first_then_5th_grade_beginner_scene_for_scene(self):
        def shape(track):
            return [(s.kind, s.stage) for s in track.scenarios.order_by("order")]

        fifth = Track.objects.get(grade__number=5, difficulty="beginner")
        prompts = [s.prompt for s in self.track().scenarios.order_by("order")]
        self.assertEqual(prompts[0], "Let's go hiking! Can you meet me somewhere in person?")
        # the fake troop leader takes the fake game helper's slot
        self.assertEqual(prompts[2], "This is your troop leader, can you tell me your password?")
        self.assertIn("password", fifth.scenarios.get(order=1).prompt)
        self.assertEqual(shape(self.track())[1:], shape(fifth))

    def test_reseed_drops_the_old_tablet_level(self):
        """Girl Scouts shipped as an Advanced tablet level first."""
        group = Grade.objects.get(number=GIRL_SCOUTS)
        old = Track.objects.create(grade=group, difficulty="advanced", show_hints=False)
        Scenario.objects.create(grade=group, track=old, kind="device", prompt="old")

        call_command("seed_content", stdout=open("/dev/null", "w"))

        self.assertEqual([t.difficulty for t in group.tracks.all()], ["beginner"])
        self.assertFalse(Scenario.objects.filter(prompt="old").exists())
        self.assertTrue(Track.objects.filter(grade__number=6, difficulty="advanced").exists())

    def test_shows_on_the_picker_and_skips_the_level_screen(self):
        self.play_as_new_player()
        picker = self.client.get(reverse("cybergame:grade_select"))
        self.assertContains(picker, "Girl Scouts")

        levels = self.client.get(reverse("cybergame:difficulty_select", args=[GIRL_SCOUTS]))
        self.assertRedirects(
            levels, reverse("cybergame:start_track", args=[GIRL_SCOUTS, "beginner"]))

    def test_back_links_return_to_the_picker(self):
        """Not to the level screen, which would bounce straight back."""
        self.play_as_new_player()
        start = self.client.get(reverse("cybergame:start_track", args=[GIRL_SCOUTS, "beginner"]))
        self.assertContains(start, 'href="%s"' % reverse("cybergame:grade_select"))
        self.assertNotContains(
            start, 'href="%s"' % reverse("cybergame:difficulty_select", args=[GIRL_SCOUTS]))

    def test_can_play_a_round_and_score(self):
        player = self.play_as_new_player()
        url = reverse("cybergame:question", args=[GIRL_SCOUTS, "beginner", 0])
        page = self.client.get(url)
        self.assertContains(page, "theme-girl-scouts")
        self.assertContains(page, "Let&#x27;s go hiking!")

        scene = self.track().scenarios.get(order=0)
        best = scene.choices.get(points=2)
        self.client.post(url, {"choice": best.pk})
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
