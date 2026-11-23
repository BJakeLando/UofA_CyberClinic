from django.core.management.base import BaseCommand

from cybergame.retention import purge_stale_rooms, retention_days


class Command(BaseCommand):
    help = ("Delete rooms nobody has joined or played in for ROOM_RETENTION_DAYS "
            "days, with their squads, progress and badges. Runs on every deploy.")

    def handle(self, *args, **options):
        rooms, squads = purge_stale_rooms()
        self.stdout.write(
            f"Deleted {rooms} unused room(s) and {squads} squad(s) "
            f"after {retention_days()} days without use."
        )
