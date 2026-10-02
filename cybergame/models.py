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
        TEXT = "text", "Text message"           # tap the screen itself

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

    # Shown only on tracks with show_hints=True. Points at the tell without
    # giving the answer away. Blank falls back to a generic line.
    hint = models.CharField(max_length=160, blank=True)

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
        VERIFY = "verify", "The saved contact"

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


class Classroom(models.Model):
    """One room. The unit everything is scoped to.

    A room behaves like an instance in a game: you only ever see the
    people in yours. That keeps the leaderboard meaningful for a class
    of 25, and it keeps every leaderboard read to a single indexed scan
    no matter how many rooms exist nationally.
    """

    code = models.CharField(max_length=8, unique=True)
    label = models.CharField(max_length=60, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_active"]
        # Names pinned to what the migrations already created. Without this
        # Django recomputes the hash suffix, decides the index was renamed,
        # and every deploy warns about unapplied model changes.
        indexes = [models.Index(fields=["code"], name="cybergame_c_code_8e21f7_idx")]

    def __str__(self):
        return self.label or f"Room {self.code}"

    @property
    def player_count(self):
        return self.players.count()


class Player(models.Model):
    """A kid, with no personal information attached.

    The handle is generated, never typed, so nothing a child enters can
    become their real name. The avatar they pick decides the animal in
    the handle, which makes it easy to recognise on the leaderboard.

    Handles are unique inside a room, not globally. Two rooms can both
    have a SilverFox624 and it does not matter, because a player never
    sees outside their own room. That is what lets this scale past the
    ~475k handle namespace a single global pool would cap us at.
    """

    classroom = models.ForeignKey(
        Classroom, related_name="players", on_delete=models.CASCADE,
        null=True, blank=True,
    )
    handle = models.CharField(max_length=40)
    avatar = models.CharField(max_length=8)
    total_points = models.PositiveIntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-total_points", "created_at"]
        # Solo players have classroom=NULL. SQL treats NULLs as distinct,
        # so solo handles are not forced unique against each other. That
        # is harmless: solo players have no leaderboard to be confused on.
        unique_together = ("classroom", "handle")
        indexes = [
            models.Index(fields=["classroom", "-total_points", "created_at"],
                         name="cybergame_p_classro_3b9c4e_idx"),
        ]

    def __str__(self):
        return f"{self.avatar} {self.handle}"

    @property
    def rank(self):
        """Place inside this player's own room."""
        return (
            Player.objects.filter(
                classroom=self.classroom, total_points__gt=self.total_points
            ).count()
            + 1
        )


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
        indexes = [models.Index(fields=["player", "scenario"],
                                name="cybergame_c_player__0a7b2d_idx")]

    def __str__(self):
        return f"{self.player.handle}: {self.points}/{self.best_possible}"

    @property
    def is_perfect(self):
        return self.points >= self.best_possible
