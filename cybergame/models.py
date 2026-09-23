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

    grade = models.ForeignKey(Grade, related_name="scenarios", on_delete=models.CASCADE)
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.DECIDE)
    prompt = models.TextField()
    image = models.ImageField(upload_to="scenarios/", blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)

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

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text