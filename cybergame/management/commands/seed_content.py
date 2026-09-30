"""Load the Cyber Squad question bank.

Run:  python manage.py seed_content
Reset and reload:  python manage.py seed_content --reset

Every scene happens inside a made-up game called "Pixel Park" that uses
made-up money called "star coins".

Brand names are written the way an attacker writes them - R0bux, Minecr@ft,
Telegr@m. That is a real trick kids should learn to spot, and it keeps the
Clinic clear of anyone else's trademarks.

Never say "grown-up" or "adult" on its own: a child should be pointed at a
teacher or a family member, not at whichever adult is nearest.

Scene kinds:
  chat   - a chat message from a player   (needs sender + sender_emoji)
  popup  - a pop-up ad                    (needs art)
  voice  - a voice message                (needs sender + sender_emoji)
  ask    - a plain question               (needs art)

Points: 2 = best (say no AND tell a teacher or family member)
        1 = safe but not the best
        0 = not safe (feedback is kind, never scary)

Keep words short. Answer buttons: 4 words or less. Feedback: one short sentence.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from cybergame.models import Grade, Track, Scenario, Choice


def S(kind, prompt, choices, stage="decide", sender="", sender_emoji="", art="", question="What do you do?"):
    return {
        "kind": kind, "prompt": prompt, "choices": choices, "stage": stage,
        "sender": sender, "sender_emoji": sender_emoji, "art": art, "question": question,
    }


CONTENT = [
    # ------------------------------------------------------------------ 3rd
    {
        "number": 3, "label": "3rd Grade", "intro": "",
        "scenarios": [
            S("popup", "You won 1,000 R0bux! Message me on Telegr@m to get your prize!", art="🎁", stage="recognize", choices=[
                ("💬", "Message them", 0, "Free prizes like this are a trick."),
                ("🙋", "Tell family or teacher", 2, "Yes! You stayed safe and told someone."),
                ("❌", "Close it", 1, "Good! Now tell a teacher or family member too."),
            ]),
            S("chat", "What school do you go to?", sender="NewFriend22", sender_emoji="👾", choices=[
                ("🤐", "Don't answer", 1, "Good! Now tell a teacher or family member too."),
                ("🏫", "Tell my school", 0, "Your school is private. Keep it secret."),
                ("🙋", "Tell family or teacher", 2, "Perfect! Teachers and families want to know."),
            ]),
            S("chat", "What is your real name?", sender="PixelPal", sender_emoji="🐱", choices=[
                ("🙋", "Tell family or teacher", 2, "Great job! That is the best move."),
                ("📛", "Tell my name", 0, "Keep your real name private in games."),
                ("🤐", "Don't answer", 1, "Good! Telling a teacher or family member is even better."),
            ]),
            S("chat", "Want to meet me at the park?", sender="BlockBuddy", sender_emoji="🧸", choices=[
                ("👋", "Say no", 1, "Good! Now tell a teacher or family member too."),
                ("🙋", "Say no and tell", 2, "Yes! Never meet game friends."),
                ("🚶", "Go meet them", 0, "Never go meet someone from a game."),
            ]),
            S("popup", "Your tablet is broken! Tap to fix!", art="⚠️", stage="recognize", choices=[
                ("🔧", "Tap to fix", 0, "This is a trick. Your tablet is fine."),
                ("❌", "Close it", 1, "Good! Tell a teacher or family member too."),
                ("🙋", "Tell family or teacher", 2, "Perfect! A teacher or family member can check it."),
            ]),
            S("ask", "Oops! You tapped something bad. The screen looks weird.", art="😬", stage="recovery", choices=[
                ("🤫", "Hide it", 0, "Telling makes it easy to fix."),
                ("🙋", "Tell family or teacher", 2, "Yes! You are NOT in trouble for telling."),
                ("🔧", "Fix it myself", 0, "Don't fix it yourself. Let a teacher or family member help."),
            ]),
            S("chat", "Where do you live?", sender="SunnyDay", sender_emoji="🌻", choices=[
                ("🙋", "Show my parents", 2, "Yes! A parent or teacher can help."),
                ("🏠", "Tell them", 0, "Never tell anyone online where you live."),
                ("🤐", "Ignore them", 1, "Good! Now show a teacher or family member too."),
            ]),
        ],
    },

    # ------------------------------------------------------------------ 4th
    {
        "number": 4, "label": "4th Grade", "intro": "",
        "scenarios": [
            S("chat", "Tell me your password. I'll give you a cool hat!", sender="HatTrader", sender_emoji="🎩", choices=[
                ("✋", "Say no", 1, "Good! Now tell a teacher or family member too."),
                ("🔑", "Give password", 0, "Never share your password. Not ever."),
                ("🙋", "Say no and tell", 2, "Perfect! Your password stays yours."),
            ]),
            S("popup", "Free R0bux! Message me on Telegr@m to get your prize!", art="⭐", stage="recognize", choices=[
                ("🙋", "Tell family or teacher", 2, "Yes! Free R0bux is always a trick."),
                ("💬", "Click Telegr@m link", 0, "This is a trick! Never click prize links."),
                ("❌", "Close it", 1, "Good! Tell a teacher or family member too."),
            ]),
            S("chat", "Can I log in as you?", sender="Sam (your friend)", sender_emoji="😀", stage="recognize", choices=[
                ("✅", "Send it", 0, "It might not really be Sam!"),
                ("🗣️", "Ask Sam at school", 1, "Smart! Tell a teacher or family member if it wasn't Sam."),
                ("🙋", "Tell family or teacher", 2, "Yes! A teacher or family member can check if it's really Sam."),
            ]),
            S("popup", "What animal are you? Type your name, birthday, and address!", art="🦄", stage="recognize", choices=[
                ("🙋", "Tell family or teacher", 2, "Great! That quiz wants your secrets."),
                ("✍️", "Fill it in", 0, "Keep your birthday and address private."),
                ("❌", "Close it", 1, "Good! Tell a teacher or family member too."),
            ]),
            S("chat", "Let's meet at the store after school!", sender="PixelPal", sender_emoji="🐱", choices=[
                ("🚶", "Go meet them", 0, "Never go meet someone from a game."),
                ("👋", "Say no", 1, "Good! Now tell a teacher or family member too."),
                ("🙋", "Say no and tell", 2, "Perfect! That is the best move."),
            ]),
            S("ask", "You typed your password on a weird website.", art="😬", stage="recovery", choices=[
                ("🙋", "Tell family or teacher", 2, "Yes! The sooner the better."),
                ("🤫", "Do nothing", 0, "It's OK! Tell someone so it gets fixed."),
                ("⏰", "Fix it later", 1, "Better to fix it now with a teacher or family member."),
            ]),
            S("ask", "You tapped something bad a few days ago.", art="⏰", stage="recovery",
              question="Is it too late to tell?", choices=[
                ("🤐", "Yes, too late", 0, "It's never too late to tell!"),
                ("⏳", "Wait, it will fix itself", 0, "Don't wait! You are not in trouble, and telling helps get it fixed."),
                ("🙋", "No, tell today", 2, "Yes! Nobody will be mad at you."),
            ]),
        ],
    },

    # ------------------------------------------------------------------ 5th
    {
        "number": 5, "label": "5th Grade", "intro": "",
        "scenarios": [
            S("chat", "Let's talk on a different app. Add me there!", sender="CoolGamer", sender_emoji="🎮", choices=[
                ("👋", "Say no", 1, "Good! Now tell a teacher or family member too."),
                ("🙋", "Say no and tell", 2, "Perfect! This one is important to tell."),
                ("📱", "Add them", 0, "Other apps are less safe. Stay put."),
            ]),
            S("chat", "I work for the game. Send your password so I can fix your account.", sender="GameHelper", sender_emoji="🛡️", stage="recognize", choices=[
                ("🔑", "Send it", 0, "Real game helpers never ask for passwords."),
                ("🙋", "Say no and tell", 2, "Yes! You saw the trick."),
                ("🚩", "Report them", 1, "Good! Tell a teacher or family member too."),
            ]),
            S("chat", "I'll give you a rare pet. Don't tell your parents!", sender="PetTrader", sender_emoji="🐉", choices=[
                ("🙋", "Tell a parent", 2, "Yes! Secrets from parents are a red flag."),
                ("🤝", "Take the deal", 0, "\"Don't tell your parents\" means tell them!"),
                ("✋", "Say no", 1, "Good! Now tell your parents too."),
            ]),
            S("chat", "I'll mail you free headphones! What's your address?", sender="PrizeKing", sender_emoji="🎧", stage="recognize", choices=[
                ("🏠", "Send my address", 0, "Never share your address online."),
                ("✋", "Say no", 1, "Good! Tell a teacher or family member too."),
                ("🙋", "Say no and tell", 2, "Perfect! Your home stays private."),
            ]),
            S("voice", "Hi honey! Leave school and meet me at the corner.", sender="Sounds like Mom", sender_emoji="🎤", stage="recognize", choices=[
                ("🏃", "Go right away", 0, "Computers can copy voices. Always check first."),
                ("🙋", "Ask my teacher", 2, "Yes! Check first. Use your family code word."),
                ("⏳", "Wait and see", 1, "Good to wait. Asking a teacher is best."),
            ]),
            S("ask", "A friend says something bad happened online. \"Don't tell anyone!\"", art="🤝", stage="report", choices=[
                ("🤐", "Keep the secret", 0, "Good friends get help for friends."),
                ("💛", "Tell a teacher", 2, "Yes! That's what a real friend does."),
                ("🤷", "Let them handle it", 0, "Some things are too big for kids alone."),
            ]),
            S("ask", "Something got downloaded on your school Chromebook.", art="💻", stage="recovery", choices=[
                ("🗑️", "Delete it, say nothing", 0, "Always tell your teacher! They can help fix it."),
                ("🙋", "Tell my teacher", 2, "Perfect! Telling fast is the best."),
                ("⏰", "Tell later", 1, "Better to tell right now."),
            ]),
        ],
    },

    # ------------------------------------------------------------------ 6th
    {
        "number": 6, "label": "6th Grade", "intro": "",
        "scenarios": [
            S("chat", "Come play in my private Minecr@ft world. Don't tell anyone!", sender="BestBud_Online", sender_emoji="🌟", choices=[
                ("🎮", "Join their world", 0, "\"Don't tell anyone\" is a trick. Tell a teacher or family member."),
                ("✋", "Stop talking to them", 1, "Good! Now tell a parent too."),
                ("🙋", "Stop and tell a parent", 2, "Yes! That takes guts. Great job."),
            ]),
            S("chat", "Send me a picture of you!", sender="NiceGamer", sender_emoji="😊", choices=[
                ("🙋", "Say no and tell", 2, "Perfect! Always tell a teacher or family member about this."),
                ("📸", "Send one", 0, "Once a picture is sent, it's online forever."),
                ("✋", "Say no", 1, "Good! Now tell a teacher or family member too."),
            ]),
            S("chat", "I'm locked out! Tell me the code that just came to your phone.", sender="Sam (your friend)", sender_emoji="😀", stage="recognize", choices=[
                ("🔢", "Send the code", 0, "That code guards your account. Never share it."),
                ("📞", "Call Sam first", 0, "Better to ask a teacher or family member first."),
                ("🙋", "Say no and tell", 2, "Yes! Sam may have been hacked."),
            ]),
            S("chat", "Hey friend, can you do me a small favor?", sender="SuperKind99", sender_emoji="💖", stage="recognize", choices=[
                ("✋", "Stop answering", 1, "Good! Talk to a parent or teacher."),
                ("🙋", "Talk to a parent", 2, "Yes! Nice words first, then favors, is a trick."),
                ("👍", "Do the favor", 0, "That's a trick. Talk to a parent or teacher."),
            ]),
            S("voice", "It's Dad. Leave the house and meet me down the street.", sender="Sounds like Dad", sender_emoji="🎤", stage="recognize", choices=[
                ("🙋", "Call Dad's real phone", 2, "Yes! Check first. Use your family code word."),
                ("🏃", "Go right away", 0, "Computers can copy voices. Always check first."),
                ("⏳", "Wait and see", 1, "Good to wait. Checking is even better."),
            ]),
            S("chat", "Let's meet in real life this weekend!", sender="PixelPal", sender_emoji="🐱", choices=[
                ("🚶", "Go meet them", 0, "Never go meet someone from a game."),
                ("🙋", "Say no and tell", 2, "Perfect! That is the best move."),
                ("👋", "Say no", 1, "Good! Now tell a teacher or family member too."),
            ]),
            S("ask", "You already gave someone your password.", art="🔑", stage="recovery", choices=[
                ("🤞", "Hope it's fine", 0, "It's fixable! Tell someone so it gets fixed."),
                ("🔄", "Change it myself", 1, "Good start! A teacher or family member can check more."),
                ("🙋", "Tell family or teacher", 2, "Yes! You are NOT in trouble for telling."),
            ]),
            S("ask", "Something bad happened online a while ago. You're embarrassed to tell.", art="💭", stage="recovery", choices=[
                ("🙋", "Tell family or teacher", 2, "Yes! It's never too late to tell."),
                ("🤐", "Let it go", 0, "It's OK! Teachers and families understand. They've been there too."),
                ("🗣️", "Tell a friend", 1, "A start! A teacher or family member can help more."),
            ]),
        ],
    },
]



# ---------------------------------------------------------------------------
# Device scenes.  The player taps the tablet itself instead of reading a list.
#
# Intermediate and Advanced share this content. The only difference is
# Track.show_hints: Intermediate still shows the question line and the worded
# answer buttons underneath, Advanced shows the screen and nothing else.
#
# Every scene needs exactly three answers, one per hotspot:
#   bait   - the tempting button inside the pop-up   (0 points)
#   close  - the little X in the corner              (1 point)
#   report - the report flag in the game bar         (2 points)
# ---------------------------------------------------------------------------

def D(app, prompt, art, bait, close, report, stage="recognize"):
    """One tablet scene. bait/close/report are (emoji, text, feedback)."""
    return {
        "kind": "device", "prompt": prompt, "art": art, "sender": app,
        "sender_emoji": "", "stage": stage, "question": "What do you do?",
        "choices": [
            (bait[0], bait[1], 0, bait[2], "bait"),
            (close[0], close[1], 1, close[2], "close"),
            (report[0], report[1], 2, report[2], "report"),
        ],
    }


CLOSE = ("❌", "Close it", "Closing it is safe. Reporting it is even better.")
REPORT = ("🚩", "Report and tell", "You reported it. Now tell a teacher or family member.")

DEVICE_CONTENT = {
    3: [
        D("Pixel Park", "CLICK HERE FOR FREE GOLD!", "🪙",
          ("🪙", "Tap to get gold", "Free gold pop-ups are a trick to take your stuff."),
          CLOSE, REPORT),
        D("Pixel Park", "YOU WON A FREE PET! TAP NOW!", "🐶",
          ("🐶", "Tap to get pet", "Real games do not give pets away in a pop-up."),
          CLOSE, REPORT),
        D("Pixel Park", "YOUR GAME WILL DELETE IN 60 SECONDS!", "⏳",
          ("⏳", "Tap to save game", "Scary countdowns are there to make you hurry. Slow down."),
          CLOSE, REPORT),
        D("Pixel Park", "TAP TO GET 10,000 FREE COINS!", "💰",
          ("💰", "Tap for coins", "If it sounds too good to be true, it is."),
          CLOSE, REPORT),
        D("Pixel Park", "YOU ARE PLAYER NUMBER 1,000,000! CLAIM PRIZE!", "🎉",
          ("🎉", "Claim my prize", "Everybody sees this same message. Nobody wins."),
          CLOSE, REPORT),
    ],
    4: [
        D("Pixel Park", "FREE R0BUX! TAP HERE NOW!", "⭐",
          ("⭐", "Tap for R0bux", "Look at the spelling. Real names are not written that way."),
          CLOSE, REPORT),
        D("Pixel Park", "ACCOUNT LOCKED! TYPE YOUR PASSWORD TO UNLOCK", "🔒",
          ("🔑", "Type my password", "A real game never asks for your password in a pop-up."),
          CLOSE, REPORT),
        D("Pixel Park", "CLICK HERE FOR FREE GOLD!", "🪙",
          ("🪙", "Tap to get gold", "Free gold pop-ups are a trick to take your stuff."),
          CLOSE, REPORT),
        D("Pixel Park", "CHAT WITH US ON TELEGR@M TO GET YOUR PRIZE", "💬",
          ("💬", "Go to the chat app", "Moving you to another app gets you away from help."),
          CLOSE, REPORT),
        D("Pixel Park", "SPIN THE WHEEL! YOU CANNOT LOSE!", "🎡",
          ("🎡", "Spin the wheel", "\"You cannot lose\" always means somebody else wins."),
          CLOSE, REPORT),
    ],
    5: [
        D("Pixel Park", "FREE RARE SKIN! JUST ENTER YOUR PASSWORD", "🎽",
          ("🔑", "Enter my password", "Your password is never the price of a free thing."),
          CLOSE, REPORT),
        D("Pixel Park", "CLAIM YOUR PRIZE ON THIS OTHER APP", "📱",
          ("📱", "Open the other app", "Off the game means away from anyone who can help you."),
          CLOSE, REPORT),
        D("Pixel Park", "ASK A PARENT FOR THEIR CARD TO KEEP PLAYING", "💳",
          ("💳", "Go get the card", "Nobody should ask a kid to fetch a payment card."),
          CLOSE, REPORT),
        D("Pixel Park", "SEE WHO LOOKED AT YOUR PROFILE! TAP!", "👀",
          ("👀", "Tap to see", "This one runs on curiosity. That is the trick."),
          CLOSE, REPORT),
        D("Pixel Park", "MINECR@FT MODS - FREE DOWNLOAD - TAP", "⬇️",
          ("⬇️", "Download it", "Downloads from a pop-up can break the whole device."),
          CLOSE, REPORT),
    ],
    6: [
        D("Pixel Park", "SEND A PHOTO OF YOURSELF TO UNLOCK THIS LEVEL", "📸",
          ("📸", "Send a photo", "No real game ever needs a picture of you. Never send one."),
          CLOSE, REPORT),
        D("Pixel Park", "WE ARE THE GAME TEAM. VERIFY YOUR PASSWORD.", "🛡️",
          ("🛡️", "Verify password", "Looking official is the whole trick. Staff never ask."),
          CLOSE, REPORT),
        D("Pixel Park", "YOUR FRIEND SENT YOU 5,000 COINS! TAP TO ACCEPT", "🎁",
          ("🎁", "Accept the gift", "Check with your friend in person. Accounts get stolen."),
          CLOSE, REPORT),
        D("Pixel Park", "ENTER THE CODE FROM YOUR PHONE TO CONTINUE", "🔢",
          ("🔢", "Enter the code", "That code is the lock on your account. It stays with you."),
          CLOSE, REPORT),
        D("Pixel Park", "UNLIMITED MONEY MOD - TAP TO INSTALL", "⬇️",
          ("⬇️", "Install the mod", "Cheat downloads are one of the easiest ways to get hacked."),
          CLOSE, REPORT),
    ],
}

TRACKS = [
    ("beginner",     "🌱", "Words and pictures, with hints", True),
    ("intermediate", "⚡", "Real screens, hints still on",    True),
    ("advanced",     "🔥", "Real screens, no hints",          False),
]


class Command(BaseCommand):
    help = "Load the Cyber Squad grade content."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete everything first.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            Grade.objects.all().delete()
            self.stdout.write("Cleared existing content.")

        for g_index, g in enumerate(CONTENT):
            grade, _ = Grade.objects.update_or_create(
                number=g["number"],
                defaults={"label": g["label"], "intro": g["intro"], "order": g_index},
            )

            tracks = {}
            for t_index, (slug, emoji, blurb, hints) in enumerate(TRACKS):
                track, _ = Track.objects.update_or_create(
                    grade=grade,
                    difficulty=slug,
                    defaults={
                        "emoji": emoji, "blurb": blurb,
                        "order": t_index, "show_hints": hints,
                    },
                )
                tracks[slug] = track
                track.scenarios.all().delete()

            # anything left over from before tracks existed
            grade.scenarios.filter(track__isnull=True).delete()

            device = DEVICE_CONTENT.get(g["number"], [])
            plan = [
                (tracks["beginner"], g["scenarios"]),
                (tracks["intermediate"], device),
                (tracks["advanced"], device),
            ]

            made = 0
            for track, scenarios in plan:
                for s_index, s in enumerate(scenarios):
                    scenario = Scenario.objects.create(
                        grade=grade,
                        track=track,
                        stage=s["stage"],
                        kind=s["kind"],
                        prompt=s["prompt"],
                        sender=s["sender"],
                        sender_emoji=s["sender_emoji"],
                        art=s["art"],
                        question=s["question"],
                        order=s_index,
                        active=True,
                    )
                    for c_index, choice in enumerate(s["choices"]):
                        emoji, text, points, feedback = choice[:4]
                        hotspot = choice[4] if len(choice) > 4 else ""
                        Choice.objects.create(
                            scenario=scenario,
                            emoji=emoji,
                            text=text,
                            points=points,
                            feedback=feedback,
                            order=c_index,
                            hotspot=hotspot,
                        )
                    made += 1

            self.stdout.write(
                f"{grade.label}: {len(g['scenarios'])} beginner, "
                f"{len(device)} device x2 ({made} scenes total)"
            )
