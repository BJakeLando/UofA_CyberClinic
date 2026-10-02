from django.db import models


class Grade(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)   # 3, 4, 5, 6
    label = models.CharField(max_length=40)                  # "3rd Grade"
    intro = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return self.label


class Track(models.Model):
    """One difficulty lane inside a grade.

    beginner      words only, hints on
    intermediate  device scenes, hints on (word buttons still shown)
    advanced      device scenes, hints off (tap the screen itself)
    """

    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    grade = models.ForeignKey(Grade, related_name="tracks", on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=14, choices=Difficulty.choices)
    blurb = models.CharField(max_length=60, blank=True)   # shown on the pick button
    emoji = models.CharField(max_length=8, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    # hints on = show the question line and the worded answer buttons
    show_hints = models.BooleanField(default=True)

    class Meta:
        ordering = ["grade__number", "order"]
        unique_together = ("grade", "difficulty")

    def __str__(self):
        return f"{self.grade.label} — {self.get_difficulty_display()}"


class Scenario(models.Model):
    class Stage(models.TextChoices):
        RECOGNIZE = "recognize", "Recognize"
        DECIDE = "decide", "Decide"
        REPORT = "report", "Report"
        RECOVERY = "recovery", "If it already happened"

    # how the scene is drawn on screen
    class Kind(models.TextChoices):
        CHAT = "chat", "Chat message"
        POPUP = "popup", "Pop-up"
        VOICE = "voice", "Voice message"
        ASK = "ask", "Plain question"
        DEVICE = "device", "Tablet screen"      # tap the screen itself

    grade = models.ForeignKey(Grade, related_name="scenarios", on_delete=models.CASCADE)
    track = models.ForeignKey(
        Track, related_name="scenarios", on_delete=models.CASCADE, null=True, blank=True
    )
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.DECIDE)
    prompt = models.TextField()
    image = models.ImageField(upload_to="scenarios/", blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)

    # display fields
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.ASK)
    sender = models.CharField(max_length=40, blank=True)          # "BlockBuddy", or app name for device
    sender_emoji = models.CharField(max_length=16, blank=True)    # avatar
    art = models.CharField(max_length=16, blank=True)             # big picture for pop-ups and plain questions
    question = models.CharField(max_length=80, default="What do you do?")

    class Meta:
        ordering = ["grade__number", "order"]

    def __str__(self):
        return f"{self.grade.label}: {self.prompt[:50]}"


class Choice(models.Model):
    """One answer.

    For device scenes, `hotspot` decides where the answer lives on the
    simulated screen instead of being a button in a list.
    """

    class Hotspot(models.TextChoices):
        BAIT = "bait", "The tempting button"
        CLOSE = "close", "The little X"
        REPORT = "report", "The report flag"

    scenario = models.ForeignKey(Scenario, related_name="choices", on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    points = models.PositiveSmallIntegerField(default=0)   # 0 / 1 / 2
    feedback = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    emoji = models.CharField(max_length=16, blank=True)
    hotspot = models.CharField(max_length=10, choices=Hotspot.choices, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text


class Player(models.Model):
    """A kid, with no personal information attached.

    The handle is generated, never typed, so nothing a child enters can
    become their real name. The avatar they pick decides the animal in
    the handle, which makes it easy to recognise on the leaderboard.
    """

    handle = models.CharField(max_length=40, unique=True)
    avatar = models.CharField(max_length=8)
    total_points = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-total_points", "created_at"]
        indexes = [models.Index(fields=["-total_points", "created_at"])]

    def __str__(self):
        return f"{self.avatar} {self.handle}"

    @property
    def rank(self):
        ahead = Player.objects.filter(total_points__gt=self.total_points).count()
        return ahead + 1


class Completion(models.Model):
    """One scenario, once per player.

    A scenario can only ever be scored once. Replaying it to fix a miss
    raises the score to the better answer; it never adds a second helping
    and it never takes points away.
    """

    player = models.ForeignKey(Player, related_name="completions", on_delete=models.CASCADE)
    scenario = models.ForeignKey(Scenario, related_name="completions", on_delete=models.CASCADE)
    points = models.PositiveSmallIntegerField(default=0)
    best_possible = models.PositiveSmallIntegerField(default=0)
    attempts = models.PositiveSmallIntegerField(default=1)
    first_try_best = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("player", "scenario")
        indexes = [models.Index(fields=["player", "scenario"])]

    def __str__(self):
        return f"{self.player.handle}: {self.points}/{self.best_possible}"

    @property
    def is_perfect(self):
        return self.points >= self.best_possible
