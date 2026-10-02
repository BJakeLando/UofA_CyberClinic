from django.contrib import admin

from .models import (Choice, Classroom, Completion, Grade, Player,
                     Scenario, Track)


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("label", "number", "order")


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("grade", "difficulty", "show_hints", "order")
    list_filter = ("difficulty", "show_hints")


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("grade", "track", "kind", "stage", "order", "active")
    list_filter = ("grade", "track__difficulty", "kind", "stage", "active")
    search_fields = ("prompt", "sender")
    inlines = [ChoiceInline]


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "player_count", "active", "created_at", "last_active")
    list_filter = ("active",)
    search_fields = ("code", "label")
    readonly_fields = ("created_at", "last_active")


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("avatar", "handle", "classroom", "total_points", "created_at", "last_seen")
    list_filter = ("classroom",)
    search_fields = ("handle", "classroom__code", "classroom__label")
    readonly_fields = ("created_at", "last_seen")


@admin.register(Completion)
class CompletionAdmin(admin.ModelAdmin):
    list_display = ("player", "scenario", "points", "best_possible", "attempts")
    list_filter = ("scenario__grade", "scenario__track__difficulty")
