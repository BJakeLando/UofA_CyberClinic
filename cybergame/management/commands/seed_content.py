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

Every scene has exactly TWO answers, at every level:
  2 = tell a teacher or family member
  0 = engage - reply, tap, send, go, keep it secret, deal with it alone

There is no in-between answer, on Wagner's instruction. "Say no", "close
it", "block them", "don't answer" and "report them" all used to be worth 1
point, but saying no is still replying, and the lesson is that a kid
should not engage at all: they go and tell. Nothing a kid can pick may say
"say no". seed_content refuses to load a scene that breaks any of this.

Keep words short. Answer buttons: 4 words or less. Feedback: one short sentence.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cybergame.models import Grade, Track, Scenario, Choice


def S(kind, prompt, choices, stage="decide", sender="", sender_emoji="", art="", question="What do you do?"):
    return {
        "kind": kind, "prompt": prompt, "choices": choices, "stage": stage,
        "sender": sender, "sender_emoji": sender_emoji, "art": art, "question": question,
    }


TELL = "Tell family or teacher"


CONTENT = [
    # ------------------------------------------------------------------ 3rd
    {
        "number": 3, "label": "3rd Grade", "intro": "",
        "scenarios": [
            S("popup", "You won 1,000 R0bux! Message me on Telegr@m to get your prize!", art="🎁", stage="recognize", choices=[
                ("💬", "Message them", 0, "Free prizes like this are a trick."),
                ("🙋", TELL, 2, "Yes! You stayed safe and told someone."),
            ]),
            S("chat", "What school do you go to?", sender="NewFriend22", sender_emoji="👾", choices=[
                ("🏫", "Tell my school", 0, "Your school is private. Keep it secret."),
                ("🙋", TELL, 2, "Perfect! Teachers and families want to know."),
            ]),
            S("chat", "What is your real name?", sender="PixelPal", sender_emoji="🐱", choices=[
                ("🙋", TELL, 2, "Great job! That is the best move."),
                ("📛", "Tell my name", 0, "Keep your real name private in games."),
            ]),
            S("chat", "Want to meet me at the park?", sender="BlockBuddy", sender_emoji="🧸", choices=[
                ("🙋", TELL, 2, "Yes! Don't answer them. Just tell."),
                ("🚶", "Go meet them", 0, "Never go meet someone from a game."),
            ]),
            S("popup", "Your tablet is broken! Tap to fix!", art="⚠️", stage="recognize", choices=[
                ("🔧", "Tap to fix", 0, "This is a trick. Your tablet is fine."),
                ("🙋", TELL, 2, "Perfect! A teacher or family member can check it."),
            ]),
            S("ask", "Oops! You tapped something bad. The screen looks weird.", art="😬", stage="recovery", choices=[
                ("🙋", TELL, 2, "Yes! You are NOT in trouble for telling."),
                ("🔧", "Fix it myself", 0, "Don't fix it yourself. Let a teacher or family member help."),
            ]),
            S("chat", "Where do you live?", sender="SunnyDay", sender_emoji="🌻", choices=[
                ("🙋", "Show my parents", 2, "Yes! A parent or teacher can help."),
                ("🏠", "Tell them", 0, "Never tell anyone online where you live."),
            ]),
        ],
    },

    # ------------------------------------------------------------------ 4th
    {
        "number": 4, "label": "4th Grade", "intro": "",
        "scenarios": [
            S("chat", "Tell me your password. I'll give you a cool hat!", sender="HatTrader", sender_emoji="🎩", choices=[
                ("🔑", "Give password", 0, "Never share your password. Not ever."),
                ("🙋", TELL, 2, "Perfect! Your password stays yours."),
            ]),
            S("popup", "Free R0bux! Message me on Telegr@m to get your prize!", art="⭐", stage="recognize", choices=[
                ("🙋", TELL, 2, "Yes! Free R0bux is always a trick."),
                ("💬", "Click Telegr@m link", 0, "This is a trick! Never click prize links."),
            ]),
            S("chat", "Can I log in as you?", sender="Sam (your friend)", sender_emoji="😀", stage="recognize", choices=[
                ("✅", "Send it", 0, "It might not really be Sam!"),
                ("🙋", TELL, 2, "Yes! A teacher or family member can check if it's really Sam."),
            ]),
            S("popup", "What animal are you? Type your name, birthday, and address!", art="🦄", stage="recognize", choices=[
                ("🙋", TELL, 2, "Great! That quiz wants your secrets."),
                ("✍️", "Fill it in", 0, "Keep your birthday and address private."),
            ]),
            S("chat", "Let's meet at the store after school!", sender="PixelPal", sender_emoji="🐱", choices=[
                ("🚶", "Go meet them", 0, "Never go meet someone from a game."),
                ("🙋", TELL, 2, "Perfect! No reply needed. Just tell."),
            ]),
            S("ask", "You typed your password on a weird website.", art="😬", stage="recovery", choices=[
                ("🙋", TELL, 2, "Yes! The sooner the better."),
                ("🤫", "Do nothing", 0, "It's OK! Tell someone so it gets fixed."),
            ]),
            S("ask", "You tapped something bad a few days ago.", art="⏰", stage="recovery",
              question="Is it too late to tell?", choices=[
                ("🤐", "Yes, too late", 0, "It's never too late to tell!"),
                ("🙋", "No, tell today", 2, "Yes! Nobody will be mad at you."),
            ]),
        ],
    },

    # ------------------------------------------------------------------ 5th
    {
        "number": 5, "label": "5th Grade", "intro": "",
        "scenarios": [
            S("chat", "Let's talk on a different app. Add me there!", sender="CoolGamer", sender_emoji="🎮", choices=[
                ("🙋", TELL, 2, "Perfect! This one is important to tell."),
                ("📱", "Add them", 0, "Other apps are less safe. Stay put."),
            ]),
            S("chat", "I work for the game. Send your password so I can fix your account.", sender="GameHelper", sender_emoji="🛡️", stage="recognize", choices=[
                ("🔑", "Send it", 0, "Real game helpers never ask for passwords."),
                ("🙋", TELL, 2, "Yes! You saw the trick."),
            ]),
            S("chat", "I'll give you a rare pet. Don't tell your parents!", sender="PetTrader", sender_emoji="🐉", choices=[
                ("🙋", "Tell a parent", 2, "Yes! Secrets from parents are a red flag."),
                ("🤝", "Take the deal", 0, "\"Don't tell your parents\" means tell them!"),
            ]),
            S("chat", "I'll mail you free headphones! What's your address?", sender="PrizeKing", sender_emoji="🎧", stage="recognize", choices=[
                ("🏠", "Send my address", 0, "Never share your address online."),
                ("🙋", TELL, 2, "Perfect! Your home stays private."),
            ]),
            S("voice", "Hi honey! Leave school and meet me at the corner.", sender="Sounds like Mom", sender_emoji="🎤", stage="recognize", choices=[
                ("🙋", "Ask my teacher", 2, "Yes! Check first. Use your family code word."),
                ("🏃", "Go right away", 0, "Computers can copy voices. Always check first."),
            ]),
            S("ask", "A friend says something bad happened online. \"Don't tell anyone!\"", art="🤝", stage="report", choices=[
                ("🤐", "Keep the secret", 0, "Good friends get help for friends."),
                ("💛", "Tell a teacher", 2, "Yes! That's what a real friend does."),
            ]),
            S("ask", "Something got downloaded on your school Chromebook.", art="💻", stage="recovery", choices=[
                ("🙋", "Tell my teacher", 2, "Perfect! Telling fast is the best."),
                ("🗑️", "Delete it, don't tell", 0, "Always tell your teacher! They can help fix it."),
            ]),
        ],
    },

    # ------------------------------------------------------------------ 6th
    {
        "number": 6, "label": "6th Grade", "intro": "",
        "scenarios": [
            S("chat", "Come play in my private Minecr@ft world. Don't tell anyone!", sender="BestBud_Online", sender_emoji="🌟", choices=[
                ("🎮", "Join their world", 0, "\"Don't tell anyone\" is a trick. Tell a teacher or family member."),
                ("🙋", "Tell a parent", 2, "Yes! That takes guts. Great job."),
            ]),
            S("chat", "Send me a picture of you!", sender="NiceGamer", sender_emoji="😊", choices=[
                ("🙋", TELL, 2, "Perfect! Always tell a teacher or family member about this."),
                ("📸", "Send one", 0, "Once a picture is sent, it's online forever."),
            ]),
            S("chat", "I'm locked out! Tell me the code that just came to your phone.", sender="Sam (your friend)", sender_emoji="😀", stage="recognize", choices=[
                ("🔢", "Send the code", 0, "That code guards your account. Never share it."),
                ("🙋", TELL, 2, "Yes! Sam may have been hacked."),
            ]),
            S("chat", "Hey friend, can you do me a small favor?", sender="SuperKind99", sender_emoji="💖", stage="recognize", choices=[
                ("🙋", "Talk to a parent", 2, "Yes! Nice words first, then favors, is a trick."),
                ("👍", "Do the favor", 0, "That's a trick. Talk to a parent or teacher."),
            ]),
            S("voice", "It's Dad. Leave the house and meet me down the street.", sender="Sounds like Dad", sender_emoji="🎤", stage="recognize", choices=[
                ("🙋", "Call Dad's real phone", 2, "Yes! Check first. Use your family code word."),
                ("🏃", "Go right away", 0, "Computers can copy voices. Always check first."),
            ]),
            S("chat", "Let's meet in real life this weekend!", sender="PixelPal", sender_emoji="🐱", choices=[
                ("🚶", "Go meet them", 0, "Never go meet someone from a game."),
                ("🙋", TELL, 2, "Perfect! Don't reply. Tell someone you trust."),
            ]),
            S("ask", "You already gave someone your password.", art="🔑", stage="recovery", choices=[
                ("🤞", "Hope it's fine", 0, "It's fixable! Tell someone so it gets fixed."),
                ("🙋", TELL, 2, "Yes! You are NOT in trouble for telling."),
            ]),
            S("ask", "Something bad happened online a while ago. You're embarrassed to tell.", art="💭", stage="recovery", choices=[
                ("🙋", TELL, 2, "Yes! It's never too late to tell."),
                ("🤐", "Let it go", 0, "It's OK! Teachers and families understand. They've been there too."),
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
# Two answers, one per hotspot:
#   bait   - the tempting button inside the pop-up   (0 points)
#   report - the Tell button in the game bar         (2 points)
#
# The hotspot is still called "report" in the database, but the button says
# Tell: reporting and closing the pop-up were dropped as in-between answers.
# With no close hotspot the pop-up draws without its little X.
# ---------------------------------------------------------------------------

def D(app, prompt, art, bait, stage="recognize"):
    """One tablet scene. bait is (emoji, text, feedback)."""
    return {
        "kind": "device", "prompt": prompt, "art": art, "sender": app,
        "sender_emoji": "", "stage": stage, "question": "What do you do?",
        "choices": [
            (bait[0], bait[1], 0, bait[2], "bait"),
            ("🙋", TELL, 2, "Yes! Don't tap anything. Tell a teacher or family member.", "report"),
        ],
    }


# ---------------------------------------------------------------------------
# Text-message scenes (kind="text")
#
# A phone showing one text from a number that is NOT in contacts, claiming to
# be somebody the kid knows. The message looks completely ordinary on purpose.
# The tell is structural and visible on screen: an unknown number at the top,
# and a saved family contact sitting right underneath it.
#
# Two answers, one per hotspot:
#   bait    - the friendly quick reply                        (0 points)
#   verify  - call a family member already saved in contacts  (2 points)
#
# `hint` shows on Intermediate only (Track.show_hints). Advanced gets the
# identical screen with no hint and no answer list.
# ---------------------------------------------------------------------------

def T(number, prompt, bait, verify, hint, stage="decide"):
    """One text-message scene. bait/verify are (emoji, text, feedback)."""
    return {
        "kind": "text", "prompt": prompt, "art": "", "sender": number,
        "sender_emoji": "", "stage": stage, "question": "What do you do?",
        "hint": hint,
        "choices": [
            (bait[0], bait[1], 0, bait[2], "bait"),
            (verify[0], verify[1], 2, verify[2], "verify"),
        ],
    }


# 3rd and 4th: someone claiming to be a classmate, after a password.
TEXT_CLASSMATE = T(
    "+1 520-555-0147",
    "hey its Jayden from class!! i got a new phone 📱 whats ur Minecr@ft "
    "password so i can send u stuff",
    ("💬", "Send it",
     "Never send a password, not even to a friend. Real friends do not ask."),
    ("📞", "Call MOM",
     "Yes! Don't reply. Your mom can help check if it is really Jayden."),
    hint="This text came from a random number, not a number saved in your "
         "phone.",
)

# 5th and 6th: someone claiming to be a parent, trying to get them to walk out.
TEXT_PARENT = T(
    "+1 520-555-0182",
    "Hey this is Dad 😊 I got a new phone. Can you come outside and meet me?",
    ("💬", "OK, coming!",
     "Anyone can type that they are your dad. That number is not his."),
    ("📞", "Call DADDY",
     "You called the number already saved for your dad, and asked your family "
     "code word if you have one. That is exactly right."),
    hint="Your dad's real number is saved under DADDY. This text came from a "
         "random number.",
)

DEVICE_CONTENT = {
    3: [
        D("Pixel Park", "CLICK HERE FOR FREE GOLD!", "🪙",
          ("🪙", "Tap to get gold", "Free gold pop-ups are a trick to take your stuff.")),
        D("Pixel Park", "YOU WON A FREE PET! TAP NOW!", "🐶",
          ("🐶", "Tap to get pet", "Real games do not give pets away in a pop-up.")),
        D("Pixel Park", "YOUR GAME WILL DELETE IN 60 SECONDS!", "⏳",
          ("⏳", "Tap to save game", "Scary countdowns are there to make you hurry. Slow down.")),
        D("Pixel Park", "TAP TO GET 10,000 FREE COINS!", "💰",
          ("💰", "Tap for coins", "If it sounds too good to be true, it is.")),
        D("Pixel Park", "YOU ARE PLAYER NUMBER 1,000,000! CLAIM PRIZE!", "🎉",
          ("🎉", "Claim my prize", "Everybody sees this same message. Nobody wins.")),
        TEXT_CLASSMATE,  # always last: appending never
        # shifts the order of scenes kids already played
    ],
    4: [
        D("Pixel Park", "FREE R0BUX! TAP HERE NOW!", "⭐",
          ("⭐", "Tap for R0bux", "Look at the spelling. Real names are not written that way.")),
        D("Pixel Park", "ACCOUNT LOCKED! TYPE YOUR PASSWORD TO UNLOCK", "🔒",
          ("🔑", "Type my password", "A real game never asks for your password in a pop-up.")),
        D("Pixel Park", "CLICK HERE FOR FREE GOLD!", "🪙",
          ("🪙", "Tap to get gold", "Free gold pop-ups are a trick to take your stuff.")),
        D("Pixel Park", "CHAT WITH US ON TELEGR@M TO GET YOUR PRIZE", "💬",
          ("💬", "Go to the chat app", "Moving you to another app gets you away from help.")),
        D("Pixel Park", "SPIN THE WHEEL! YOU CANNOT LOSE!", "🎡",
          ("🎡", "Spin the wheel", "\"You cannot lose\" always means somebody else wins.")),
        TEXT_CLASSMATE,
    ],
    5: [
        D("Pixel Park", "FREE RARE SKIN! JUST ENTER YOUR PASSWORD", "🎽",
          ("🔑", "Enter my password", "Your password is never the price of a free thing.")),
        D("Pixel Park", "CLAIM YOUR PRIZE ON THIS OTHER APP", "📱",
          ("📱", "Open the other app", "Off the game means away from anyone who can help you.")),
        D("Pixel Park", "ASK A PARENT FOR THEIR CARD TO KEEP PLAYING", "💳",
          ("💳", "Go get the card", "Nobody should ask a kid to fetch a payment card.")),
        D("Pixel Park", "SEE WHO LOOKED AT YOUR PROFILE! TAP!", "👀",
          ("👀", "Tap to see", "This one runs on curiosity. That is the trick.")),
        D("Pixel Park", "MINECR@FT MODS - FREE DOWNLOAD - TAP", "⬇️",
          ("⬇️", "Download it", "Downloads from a pop-up can break the whole device.")),
        TEXT_PARENT,
    ],
    6: [
        D("Pixel Park", "SEND A PHOTO OF YOURSELF TO UNLOCK THIS LEVEL", "📸",
          ("📸", "Send a photo", "No real game ever needs a picture of you. Never send one.")),
        D("Pixel Park", "WE ARE THE GAME TEAM. VERIFY YOUR PASSWORD.", "🛡️",
          ("🛡️", "Verify password", "Looking official is the whole trick. Staff never ask.")),
        D("Pixel Park", "YOUR FRIEND SENT YOU 5,000 COINS! TAP TO ACCEPT", "🎁",
          ("🎁", "Accept the gift", "Accounts get stolen. A teacher or family member can help check.")),
        D("Pixel Park", "ENTER THE CODE FROM YOUR PHONE TO CONTINUE", "🔢",
          ("🔢", "Enter the code", "That code is the lock on your account. It stays with you.")),
        D("Pixel Park", "UNLIMITED MONEY MOD - TAP TO INSTALL", "⬇️",
          ("⬇️", "Install the mod", "Cheat downloads are one of the easiest ways to get hacked.")),
        TEXT_PARENT,
    ],
}


# ---------------------------------------------------------------------------
# Groups - played instead of a grade.
#
# Girl Scouts uses the Beginner style (chat, voice and plain questions with
# worded answer buttons). It opens with a hiking meet-up, then follows 5th
# grade Beginner scene for scene, reworded around trail friends, troop
# chats, badges and cookie sales. The fake troop leader sits where 5th
# grade's fake game helper is.
#
# No logos, cookie names or official program names: badges, troops and
# cookie sales are generic enough to say plainly, the rest stays out.
# ---------------------------------------------------------------------------

SCOUTS = [
    S("chat", "Let's go hiking! Can you meet me somewhere in person?", sender="TrailBuddy", sender_emoji="🥾", choices=[
        ("🚶", "Go meet them", 0, "Never go meet someone you only know online."),
        ("🙋", TELL, 2, "Perfect! Don't reply. Tell someone you trust."),
    ]),
    S("chat", "Let's talk on a different app. Add me there!", sender="CampPal", sender_emoji="🎒", choices=[
        ("🙋", TELL, 2, "Perfect! This one is important to tell."),
        ("📱", "Add them", 0, "Other apps are less safe. Stay put."),
    ]),
    S("chat", "This is your troop leader, can you tell me your password?", sender="TroopLeader", sender_emoji="🧭", stage="recognize", choices=[
        ("🔑", "Send my password", 0, "Real troop leaders never ask for your password."),
        ("🙋", TELL, 2, "Yes! You saw the trick."),
    ]),
    S("chat", "I'll give you a secret badge. Don't tell your parents!", sender="BadgeTrader", sender_emoji="🎖️", choices=[
        ("🙋", "Tell a parent", 2, "Yes! Secrets from parents are a red flag."),
        ("🤝", "Take the deal", 0, "\"Don't tell your parents\" means tell them!"),
    ]),
    S("chat", "I want to buy 10 boxes of cookies! What's your home address?", sender="CookieFan", sender_emoji="🍪", stage="recognize", choices=[
        ("🏠", "Send my address", 0, "Never share your address online."),
        ("🙋", TELL, 2, "Perfect! Your family can handle cookie orders."),
    ]),
    S("voice", "Hi honey! Leave your troop meeting and meet me at the corner.", sender="Sounds like Mom", sender_emoji="🎤", stage="recognize", choices=[
        ("🙋", "Ask my troop leader", 2, "Yes! Check first. Use your family code word."),
        ("🏃", "Go right away", 0, "Computers can copy voices. Always check first."),
    ]),
    S("ask", "A troop friend says something bad happened online. \"Don't tell anyone!\"", art="🤝", stage="report", choices=[
        ("🤐", "Keep the secret", 0, "Good friends get help for friends."),
        ("💛", "Tell my troop leader", 2, "Yes! That's what a real friend does."),
    ]),
    S("ask", "Something got downloaded on your family's tablet.", art="📱", stage="recovery", choices=[
        ("🙋", "Tell my family", 2, "Perfect! Telling fast is the best."),
        ("🗑️", "Delete it, don't tell", 0, "Always tell! Your family can help fix it."),
    ]),
]

# Group numbers start at 100 so they never collide with a grade (see Grade).
GROUPS = [
    {
        "number": 100, "label": "Girl Scouts",
        "intro": "Trail friends, troop chats and cookie sales. Spot the tricks!",
        "tracks": {"beginner": SCOUTS},
    },
]


def check(where, scene):
    """Refuse a scene that breaks the two-answer rule (see the top of this file)."""
    choices = scene["choices"]
    problem = None
    if sorted(c[2] for c in choices) != [0, 2]:
        problem = "needs exactly two answers: one worth 2 (tell), one worth 0 (engage)"
    elif any("say no" in c[1].lower() for c in choices):
        problem = 'has an answer that says "say no"'
    if problem:
        raise CommandError(f"{where}: \"{scene['prompt']}\" {problem}.")


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
            device = DEVICE_CONTENT.get(g["number"], [])
            made = self.load(g, Grade.Kind.GRADE, g_index, {
                "beginner": g["scenarios"],
                "intermediate": device,
                "advanced": device,
            })
            self.stdout.write(
                f"{g['label']}: {len(g['scenarios'])} beginner, "
                f"{len(device)} device x2 ({made} scenes total)"
            )

        for g_index, g in enumerate(GROUPS, start=len(CONTENT)):
            made = self.load(g, Grade.Kind.GROUP, g_index, g["tracks"])
            levels = ", ".join(g["tracks"])
            self.stdout.write(f"{g['label']}: {levels} ({made} scenes total)")

    def load(self, g, kind, g_index, content):
        """Create or update one grade or group and every scene under it.

        `content` maps a difficulty slug to its scene list. A grade has all
        three; a group only has the levels listed for it.
        """
        grade, _ = Grade.objects.update_or_create(
            number=g["number"],
            defaults={"label": g["label"], "intro": g["intro"],
                      "order": g_index, "kind": kind},
        )

        tracks = {}
        for t_index, (slug, emoji, blurb, hints) in enumerate(TRACKS):
            if slug not in content:
                continue
            track, _ = Track.objects.update_or_create(
                grade=grade,
                difficulty=slug,
                defaults={
                    "emoji": emoji, "blurb": blurb,
                    "order": t_index, "show_hints": hints,
                },
            )
            tracks[slug] = track

        # anything left over from before tracks existed
        grade.scenarios.filter(track__isnull=True).delete()

        # A level dropped from the content goes away, with its scenes and
        # everyone's completions on them. Stars already earned there stay on
        # players' totals. (Girl Scouts used to be an Advanced tablet level.)
        grade.tracks.exclude(difficulty__in=list(content)).delete()

        plan = [(tracks[slug], content[slug]) for slug in tracks]

        made = 0
        for track, scenarios in plan:
            for s_index, s in enumerate(scenarios):
                check(f"{grade.label}, {track.get_difficulty_display()}, round {s_index + 1}", s)

                # update in place, keyed on (track, order).
                #
                # This MUST NOT delete and recreate. Completion rows
                # cascade from Scenario, so wiping scenarios on every
                # deploy would erase every player's history and let
                # them re-earn points they already had.
                scenario, _ = Scenario.objects.update_or_create(
                    track=track,
                    order=s_index,
                    defaults={
                        "grade": grade,
                        "stage": s["stage"],
                        "kind": s["kind"],
                        "prompt": s["prompt"],
                        "sender": s["sender"],
                        "sender_emoji": s["sender_emoji"],
                        "art": s["art"],
                        "question": s["question"],
                        "hint": s.get("hint", ""),
                        "active": True,
                    },
                )
                for c_index, choice in enumerate(s["choices"]):
                    emoji, text, points, feedback = choice[:4]
                    hotspot = choice[4] if len(choice) > 4 else ""
                    Choice.objects.update_or_create(
                        scenario=scenario,
                        order=c_index,
                        defaults={
                            "emoji": emoji,
                            "text": text,
                            "points": points,
                            "feedback": feedback,
                            "hotspot": hotspot,
                        },
                    )
                # drop answers that no longer exist in the content file
                scenario.choices.filter(order__gte=len(s["choices"])).delete()
                made += 1

            # drop scenes removed from the end of a track
            track.scenarios.filter(order__gte=len(scenarios)).delete()

        return made
