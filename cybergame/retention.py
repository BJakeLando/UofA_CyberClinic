"""Delete rooms nobody is using any more, with everything in them.

A room counts as in use while kids keep joining it or playing in it. Once it
has gone ROOM_RETENTION_DAYS without either, the room is deleted, and the
database's cascades take its squads, their progress and their badges with it.
COPPA asks operators to keep children's information only as long as it is
needed; for a classroom room, that is as long as the class is playing.

Activity is worked out from what the game already records (when a squad was
made, when a round was last answered), so nothing extra is written while
kids play, and rooms made before this existed are judged the same way.
"""

from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

from .models import Classroom, Player

# How often views may trigger a purge, per server process. The purge itself
# is one indexed query, so this is about not repeating work, not cost.
PURGE_EVERY_SECONDS = 6 * 60 * 60
PURGE_CACHE_KEY = "cybergame:purge-rooms"


def retention_days():
    return settings.ROOM_RETENTION_DAYS


def stale_rooms(now=None):
    """Rooms older than the window with no squad made or round played in it."""
    cutoff = (now or timezone.now()) - timedelta(days=retention_days())
    busy = Player.objects.filter(classroom=OuterRef("pk")).filter(
        Q(created_at__gte=cutoff) | Q(completions__updated_at__gte=cutoff)
    )
    return Classroom.objects.filter(created_at__lt=cutoff).exclude(Exists(busy))


def purge_stale_rooms(now=None):
    """Delete unused rooms. Returns (rooms deleted, squads deleted)."""
    ids = list(stale_rooms(now).values_list("pk", flat=True))
    if not ids:
        return 0, 0
    squads = Player.objects.filter(classroom_id__in=ids).count()
    Classroom.objects.filter(pk__in=ids).delete()
    return len(ids), squads


def maybe_purge():
    """Purge at most every few hours. Cheap enough to call from a view."""
    if cache.add(PURGE_CACHE_KEY, True, PURGE_EVERY_SECONDS):
        purge_stale_rooms()
