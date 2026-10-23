import json

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse

from .management.commands import seed_content as content
from .models import Choice, Completion, Grade, Player, Scenario, Track
from .tablet_content import ROUNDS

GIRL_SCOUTS = 100
GRADES = [3, 4, 5, 6, GIRL_SCOUTS]


def quiet_seed():
    call_command("seed_content", stdout=open("/dev/null", "w"))


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
        quiet_seed()

    def play_as_new_player(self):
        player = Player.objects.create(handle="TestFox1", avatar="🦊")
        session = self.client.session
        session["player_id"] = player.pk
        session.save()
        return player


class BeginnerRuleTests(SeededTestCase):
    """Wagner: Beginner has no in-between answers. Engage, or tell."""

    def test_every_beginner_scene_has_two_answers_engage_or_tell(self):
        scenes = Scenario.objects.filter(track__difficulty="beginner").select_related("grade")
        self.assertGreater(scenes.count(), 35)
        for scene in scenes:
            where = f"{scene.grade.label}: {scene.prompt}"
            self.assertEqual(sorted(c.points for c in scene.choices.all()), [0, 2], where)

    def test_nothing_anywhere_says_say_no(self):
        self.assertFalse(Choice.objects.filter(text__icontains="say no").exists())

    def test_seed_refuses_a_three_answer_scene(self):
        bad = content.S("chat", "Bad scene", choices=[
            ("👋", "Say no", 1, "x"), ("🙋", "Tell", 2, "x"), ("🚶", "Go", 0, "x")])
        with self.assertRaises(CommandError):
            content.check("test", bad)


class TabletContentTests(SeededTestCase):
    """Intermediate and Advanced are the pretend tablet, everywhere."""

    def test_every_grade_and_girl_scouts_play_the_same_tablet_rounds(self):
        keys = [r["setup"]["key"] for r in ROUNDS]
        for number in GRADES:
            for level in ("intermediate", "advanced"):
                track = Track.objects.get(grade__number=number, difficulty=level)
                scenes = list(track.scenarios.order_by("order"))
                self.assertEqual([s.kind for s in scenes], ["tablet"] * len(ROUNDS), (number, level))
                self.assertEqual([s.setup["key"] for s in scenes], keys, (number, level))

    def test_intermediate_has_tips_and_advanced_has_none(self):
        self.assertTrue(Track.objects.filter(difficulty="intermediate", show_hints=False).count() == 0)
        self.assertTrue(Track.objects.filter(difficulty="advanced", show_hints=True).count() == 0)

    def test_every_round_has_a_3_star_move_and_a_done(self):
        for r in ROUNDS:
            points = {c[4]: c[2] for c in r["choices"]}
            self.assertEqual(max(points.values()), 3, r["prompt"])
            self.assertIn("done", points, r["prompt"])

    def test_some_rounds_are_safe_so_tell_is_not_always_the_answer(self):
        """The Girl Scouts guessed every answer was "tell and do nothing"."""
        best = {}
        for r in ROUNDS:
            top = max(c[2] for c in r["choices"])
            best[r["setup"]["key"]] = {c[4] for c in r["choices"] if c[2] == top}
        safe = [k for k, moves in best.items() if "tell" not in moves]
        self.assertIn("safe_mom", safe)
        self.assertIn("safe_teacher", safe)
        for key in ("safe_mom", "safe_teacher"):
            done = [c for c in next(r for r in ROUNDS if r["setup"]["key"] == key)["choices"] if c[4] == "done"][0]
            self.assertLess(done[2], 2, "doing nothing can't score well on a safe round")

    def test_seed_refuses_a_round_that_can_send_an_unscored_action(self):
        broken = json.loads(json.dumps(ROUNDS[0]))
        broken["setup"]["threads"][0]["replies"].append({"text": "lol", "act": "not_a_real_outcome"})
        with self.assertRaises(CommandError):
            content.check("test", broken)

    def test_seed_refuses_a_round_without_done(self):
        broken = json.loads(json.dumps(ROUNDS[0]))
        broken["choices"] = [c for c in broken["choices"] if c[4] != "done"]
        with self.assertRaises(CommandError):
            content.check("test", broken)


class TabletPageTests(SeededTestCase):

    def url(self, n=0, level="intermediate", grade=4):
        return reverse("cybergame:question", args=[grade, level, n])

    def data(self, page):
        html = page.content.decode()
        start = html.index('id="tablet-data"')
        start = html.index(">", start) + 1
        return json.loads(html[start:html.index("</script>", start)])

    def test_intermediate_page_has_the_tablet_tips_and_hint_line(self):
        self.play_as_new_player()
        page = self.client.get(self.url())
        self.assertContains(page, 'id="tablet"')
        self.assertContains(page, "tablet.js")
        self.assertContains(page, 'id="tab-hint"')
        self.assertContains(page, 'id="tab-tips"')
        data = self.data(page)
        self.assertTrue(data["hints"])
        self.assertEqual(data["outcomes"]["tell"], 3)
        self.assertEqual(data["outcomes"]["go_outside"], 0)

    def test_advanced_page_has_no_help_at_all(self):
        self.play_as_new_player()
        page = self.client.get(self.url(level="advanced"))
        self.assertContains(page, 'id="tablet"')
        self.assertNotContains(page, 'id="tab-hint"')
        self.assertNotContains(page, 'id="tab-tips"')
        self.assertFalse(self.data(page)["hints"])

    def post(self, n, outcome, flags=""):
        return self.client.post(self.url(n), {"outcome": outcome, "flags": flags})

    def test_an_ending_action_scores_and_shows_the_lesson(self):
        player = self.play_as_new_player()
        page = self.post(0, "tell")
        self.assertContains(page, "Called or texted Mom or Dad from Contacts")
        self.assertContains(page, "Remember")
        player.refresh_from_db()
        self.assertEqual(player.total_points, 3)

    def test_finished_counts_the_best_partial_step(self):
        player = self.play_as_new_player()
        page = self.post(1, "done", "delete,tell")      # prize email: told (2) beats deleted (1)
        self.assertContains(page, "Told a family member")
        player.refresh_from_db()
        self.assertEqual(player.total_points, 2)

    def test_finished_with_nothing_scores_done(self):
        self.play_as_new_player()
        self.assertContains(self.post(3, "done"), "Didn&#x27;t do anything")

    def test_a_partial_step_cannot_end_the_round_by_itself(self):
        player = self.play_as_new_player()
        self.post(3, "report_game")
        self.assertFalse(Completion.objects.filter(player=player).exists())

    def test_made_up_keys_and_flags_score_nothing(self):
        player = self.play_as_new_player()
        self.post(0, "free_stars")
        self.post(0, "done", "go_outside,tell")         # not partials of this round: ignored
        player.refresh_from_db()
        self.assertEqual(player.total_points, 1)        # just "done" (1 star) on round 1

    def test_safe_round_rewards_answering_mom(self):
        self.play_as_new_player()
        self.assertContains(self.post(2, "reply_ok"), "Best move")
        self.assertContains(self.post(2, "block_mom"), "That was really Mom")


class GirlScoutsTests(SeededTestCase):

    def test_is_a_group_not_a_grade(self):
        group = Grade.objects.get(number=GIRL_SCOUTS)
        self.assertTrue(group.is_group)
        self.assertEqual(group.title, "Girl Scouts")
        self.assertEqual(Grade.objects.get(number=6).title, "Grade 6")

    def test_has_all_three_levels_now(self):
        group = Grade.objects.get(number=GIRL_SCOUTS)
        self.assertEqual([t.difficulty for t in group.tracks.all()],
                         ["beginner", "intermediate", "advanced"])
        self.assertFalse(group.skips_level_pick)

    def test_beginner_opens_with_hiking_then_5th_grade_scene_for_scene(self):
        def shape(track):
            return [(s.kind, s.stage) for s in track.scenarios.order_by("order")]

        fifth = Track.objects.get(grade__number=5, difficulty="beginner")
        scouts = Track.objects.get(grade__number=GIRL_SCOUTS, difficulty="beginner")
        prompts = [s.prompt for s in scouts.scenarios.order_by("order")]
        self.assertEqual(prompts[0], "Let's go hiking! Can you meet me somewhere in person?")
        self.assertEqual(prompts[2], "This is your troop leader, can you tell me your password?")
        self.assertEqual(shape(scouts)[1:], shape(fifth))

    def test_shows_on_the_picker_and_offers_the_levels(self):
        self.play_as_new_player()
        picker = self.client.get(reverse("cybergame:grade_select"))
        self.assertContains(picker, "Girl Scouts")
        levels = self.client.get(reverse("cybergame:difficulty_select", args=[GIRL_SCOUTS]))
        self.assertEqual(levels.status_code, 200)
        self.assertContains(levels, "A real tablet")

    def test_can_play_a_beginner_round_and_score(self):
        player = self.play_as_new_player()
        url = reverse("cybergame:question", args=[GIRL_SCOUTS, "beginner", 0])
        page = self.client.get(url)
        self.assertContains(page, "theme-girl-scouts")
        best = Track.objects.get(grade__number=GIRL_SCOUTS, difficulty="beginner") \
            .scenarios.get(order=0).choices.get(points=2)
        self.client.post(url, {"choice": best.pk})
        player.refresh_from_db()
        self.assertEqual(player.total_points, 2)


class ReseedKeepsProgressTests(SeededTestCase):
    """Deploys run seed_content every time."""

    def test_reseed_keeps_completions_and_choices_stable(self):
        player = Player.objects.create(handle="TestFox1", avatar="🦊", total_points=2)
        scene = Scenario.objects.filter(choices__text="Go meet them").first()
        Completion.objects.create(player=player, scenario=scene, points=2, best_possible=2)
        before = (Scenario.objects.count(), Choice.objects.count())

        quiet_seed()

        self.assertEqual((Scenario.objects.count(), Choice.objects.count()), before)
        self.assertTrue(Completion.objects.filter(player=player, scenario=scene).exists())

    def test_old_one_popup_rounds_are_forgotten_and_their_stars_taken_back(self):
        """A slot that was a device scene and is now a tablet round is a new round."""
        player = Player.objects.create(handle="TestFox1", avatar="🦊", total_points=7)
        scene = Scenario.objects.get(track__grade__number=6, track__difficulty="advanced", order=0)
        Scenario.objects.filter(pk=scene.pk).update(kind="device")
        Completion.objects.create(player=player, scenario=scene, points=2, best_possible=2)

        quiet_seed()

        scene.refresh_from_db()
        player.refresh_from_db()
        self.assertEqual(scene.kind, "tablet")
        self.assertFalse(Completion.objects.filter(scenario=scene).exists())
        self.assertEqual(player.total_points, 5)
