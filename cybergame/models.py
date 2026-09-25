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


class Scenario(models.Model):
    class Stage(models.TextChoices):
        RECOGNIZE = "recognize", "Recognize"
        DECIDE = "decide", "Decide"
        REPORT = "report", "Report"
        RECOVERY = "recovery", "If it already happened"

    # NEW: how the scene is drawn on screen
    class Kind(models.TextChoices):
        CHAT = "chat", "Chat message"
        POPUP = "popup", "Pop-up"
        VOICE = "voice", "Voice message"
        ASK = "ask", "Plain question"

    grade = models.ForeignKey(Grade, related_name="scenarios", on_delete=models.CASCADE)
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.DECIDE)
    prompt = models.TextField()
    image = models.ImageField(upload_to="scenarios/", blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)

    # NEW display fields
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.ASK)
    sender = models.CharField(max_length=40, blank=True)          # "BlockBuddy"
    sender_emoji = models.CharField(max_length=16, blank=True)    # avatar
    art = models.CharField(max_length=16, blank=True)             # big picture for pop-ups and plain questions
    question = models.CharField(max_length=80, default="What do you do?")

    class Meta:
        ordering = ["grade__number", "order"]

    def __str__(self):
        return f"{self.grade.label}: {self.prompt[:50]}"


class Choice(models.Model):
    scenario = models.ForeignKey(Scenario, related_name="choices", on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    points = models.PositiveSmallIntegerField(default=0)   # 0 / 1 / 2
    feedback = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    # NEW
    emoji = models.CharField(max_length=16, blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text
