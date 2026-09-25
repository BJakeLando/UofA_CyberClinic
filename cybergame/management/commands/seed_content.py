"""Load the Cyber Squad question bank.

Run:  python manage.py seed_content
Reset and reload:  python manage.py seed_content --reset

Every scene happens inside a made-up game called "Pixel Park" that uses
made-up money called "star coins". No real games, brands, or characters.

Scene kinds:
  chat   - a chat message from a player   (needs sender + sender_emoji)
  popup  - a pop-up ad                    (needs art)
  voice  - a voice message                (needs sender + sender_emoji)
  ask    - a plain question               (needs art)

Points: 2 = best (say no AND tell a grown-up)
        1 = safe but not the best
        0 = not safe (feedback is kind, never scary)

Keep words short. Answer buttons: 4 words or less. Feedback: one short sentence.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from cybergame.models import Grade, Scenario, Choice


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
            S("popup", "You won 1,000 Robux! Message me on Telegram to get your prize!", art="🎁", stage="recognize", choices=[
                ("💬", "Message them", 0, "Free prizes like this are a trick."),
                ("🙋", "Tell a grown-up", 2, "Yes! You stayed safe and told someone."),
                ("❌", "Close it", 1, "Good! Now tell a grown-up too."),
            ]),
            S("chat", "What school do you go to?", sender="NewFriend22", sender_emoji="👾", choices=[
                ("🤐", "Don't answer", 1, "Good! Now tell a grown-up too."),
                ("🏫", "Tell my school", 0, "Your school is private. Keep it secret."),
                ("🙋", "Tell a grown-up", 2, "Perfect! Grown-ups want to know."),
            ]),
            S("chat", "What is your real name?", sender="PixelPal", sender_emoji="🐱", choices=[
                ("🙋", "Tell a grown-up", 2, "Great job! That is the best move."),
                ("📛", "Tell my name", 0, "Keep your real name private in games."),
                ("🤐", "Don't answer", 1, "Good! Telling a grown-up is even better."),
            ]),
            S("chat", "Want to meet me at the park?", sender="BlockBuddy", sender_emoji="🧸", choices=[
                ("👋", "Say no", 1, "Good! Now tell a grown-up too."),
                ("🙋", "Say no and tell", 2, "Yes! Never meet game friends."),
                ("🚶", "Go meet them", 0, "Never go meet someone from a game."),
            ]),
            S("popup", "Your tablet is broken! Tap to fix!", art="⚠️", stage="recognize", choices=[
                ("🔧", "Tap to fix", 0, "This is a trick. Your tablet is fine."),
                ("❌", "Close it", 1, "Good! Tell a grown-up too."),
                ("🙋", "Tell a grown-up", 2, "Perfect! A grown-up can check it."),
            ]),
            S("ask", "Oops! You tapped something bad. The screen looks weird.", art="😬", stage="recovery", choices=[
                ("🤫", "Hide it", 0, "Telling makes it easy to fix."),
                ("🙋", "Tell a grown-up", 2, "Yes! You are NOT in trouble for telling."),
                ("🔧", "Fix it myself", 0, "Don't fix it yourself. Let a grown-up help."),
            ]),
            S("chat", "Where do you live?", sender="SunnyDay", sender_emoji="🌻", choices=[
                ("🙋", "Show my parents", 2, "Yes! A parent or teacher can help."),
                ("🏠", "Tell them", 0, "Never tell anyone online where you live."),
                ("🤐", "Ignore them", 1, "Good! Now show a grown-up too."),
            ]),
        ],
    },

    # ------------------------------------------------------------------ 4th
    {
        "number": 4, "label": "4th Grade", "intro": "",
        "scenarios": [
            S("chat", "Tell me your password. I'll give you a cool hat!", sender="HatTrader", sender_emoji="🎩", choices=[
                ("✋", "Say no", 1, "Good! Now tell a grown-up too."),
                ("🔑", "Give password", 0, "Never share your password. Not ever."),
                ("🙋", "Say no and tell", 2, "Perfect! Your password stays yours."),
            ]),
            S("popup", "Free Robux! Message me on Telegram to get your prize!", art="⭐", stage="recognize", choices=[
                ("🙋", "Tell a grown-up", 2, "Yes! Free Robux is always a trick."),
                ("💬", "Click Telegram link", 0, "This is a trick! Never click prize links."),
                ("❌", "Close it", 1, "Good! Tell a grown-up too."),
            ]),
            S("chat", "Can I log in as you?", sender="Sam (your friend)", sender_emoji="😀", stage="recognize", choices=[
                ("✅", "Send it", 0, "It might not really be Sam!"),
                ("🗣️", "Ask Sam at school", 1, "Smart! Tell a grown-up if it wasn't Sam."),
                ("🙋", "Tell a grown-up", 2, "Yes! A grown-up can check if it's really Sam."),
            ]),
            S("popup", "What animal are you? Type your name, birthday, and address!", art="🦄", stage="recognize", choices=[
                ("🙋", "Tell a grown-up", 2, "Great! That quiz wants your secrets."),
                ("✍️", "Fill it in", 0, "Keep your birthday and address private."),
                ("❌", "Close it", 1, "Good! Tell a grown-up too."),
            ]),
            S("chat", "Let's meet at the store after school!", sender="PixelPal", sender_emoji="🐱", choices=[
                ("🚶", "Go meet them", 0, "Never go meet someone from a game."),
                ("👋", "Say no", 1, "Good! Now tell a grown-up too."),
                ("🙋", "Say no and tell", 2, "Perfect! That is the best move."),
            ]),
            S("ask", "You typed your password on a weird website.", art="😬", stage="recovery", choices=[
                ("🙋", "Tell a grown-up now", 2, "Yes! The sooner the better."),
                ("🤫", "Do nothing", 0, "It's OK! Tell someone so it gets fixed."),
                ("⏰", "Fix it later", 1, "Better to fix it now with a grown-up."),
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
                ("👋", "Say no", 1, "Good! Now tell a grown-up too."),
                ("🙋", "Say no and tell", 2, "Perfect! This one is important to tell."),
                ("📱", "Add them", 0, "Other apps are less safe. Stay put."),
            ]),
            S("chat", "I work for the game. Send your password so I can fix your account.", sender="GameHelper", sender_emoji="🛡️", stage="recognize", choices=[
                ("🔑", "Send it", 0, "Real game helpers never ask for passwords."),
                ("🙋", "Say no and tell", 2, "Yes! You saw the trick."),
                ("🚩", "Report them", 1, "Good! Tell a grown-up too."),
            ]),
            S("chat", "I'll give you a rare pet. Don't tell your parents!", sender="PetTrader", sender_emoji="🐉", choices=[
                ("🙋", "Tell a parent", 2, "Yes! Secrets from parents are a red flag."),
                ("🤝", "Take the deal", 0, "\"Don't tell your parents\" means tell them!"),
                ("✋", "Say no", 1, "Good! Now tell your parents too."),
            ]),
            S("chat", "I'll mail you free headphones! What's your address?", sender="PrizeKing", sender_emoji="🎧", stage="recognize", choices=[
                ("🏠", "Send my address", 0, "Never share your address online."),
                ("✋", "Say no", 1, "Good! Tell a grown-up too."),
                ("🙋", "Say no and tell", 2, "Perfect! Your home stays private."),
            ]),
            S("voice", "Hi honey! Leave school and meet me at the corner.", sender="Sounds like Mom", sender_emoji="🎤", stage="recognize", choices=[
                ("🏃", "Go right away", 0, "Computers can copy voices. Always check first."),
                ("🙋", "Ask my teacher", 2, "Yes! Check first. Use your family code word."),
                ("⏳", "Wait and see", 1, "Good to wait. Asking a teacher is best."),
            ]),
            S("ask", "A friend says something bad happened online. \"Don't tell anyone!\"", art="🤝", stage="report", choices=[
                ("🤐", "Keep the secret", 0, "Good friends get help for friends."),
                ("💛", "Get a grown-up", 2, "Yes! That's what a real friend does."),
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
            S("chat", "Come play in my private Minecraft world. Don't tell anyone!", sender="BestBud_Online", sender_emoji="🌟", choices=[
                ("🎮", "Join their world", 0, "\"Don't tell anyone\" is a trick. Tell a grown-up."),
                ("✋", "Stop talking to them", 1, "Good! Now tell a parent too."),
                ("🙋", "Stop and tell a parent", 2, "Yes! That takes guts. Great job."),
            ]),
            S("chat", "Send me a picture of you!", sender="NiceGamer", sender_emoji="😊", choices=[
                ("🙋", "Say no and tell", 2, "Perfect! Always tell a grown-up about this."),
                ("📸", "Send one", 0, "Once a picture is sent, it's online forever."),
                ("✋", "Say no", 1, "Good! Now tell a grown-up too."),
            ]),
            S("chat", "I'm locked out! Tell me the code that just came to your phone.", sender="Sam (your friend)", sender_emoji="😀", stage="recognize", choices=[
                ("🔢", "Send the code", 0, "That code guards your account. Never share it."),
                ("📞", "Call Sam first", 0, "Better to ask a grown-up first."),
                ("🙋", "Say no and tell", 2, "Yes! Sam may have been hacked."),
            ]),
            S("chat", "Hey friend, can you do me a small favor?", sender="SuperKind99", sender_emoji="💖", stage="recognize", choices=[
                ("✋", "Stop answering", 1, "Good! Talk to a parent or teacher."),
                ("🙋", "Talk to a parent", 2, "Yes! Nice words first, then favors, is a trick."),
                ("👍", "Do the favor", 0, "That's a trick. Talk to a grown-up."),
            ]),
            S("voice", "It's Dad. Leave the house and meet me down the street.", sender="Sounds like Dad", sender_emoji="🎤", stage="recognize", choices=[
                ("🙋", "Call Dad's real phone", 2, "Yes! Check first. Use your family code word."),
                ("🏃", "Go right away", 0, "Computers can copy voices. Always check first."),
                ("⏳", "Wait and see", 1, "Good to wait. Checking is even better."),
            ]),
            S("chat", "Let's meet in real life this weekend!", sender="PixelPal", sender_emoji="🐱", choices=[
                ("🚶", "Go meet them", 0, "Never go meet someone from a game."),
                ("🙋", "Say no and tell", 2, "Perfect! That is the best move."),
                ("👋", "Say no", 1, "Good! Now tell a grown-up too."),
            ]),
            S("ask", "You already gave someone your password.", art="🔑", stage="recovery", choices=[
                ("🤞", "Hope it's fine", 0, "It's fixable! Tell someone so it gets fixed."),
                ("🔄", "Change it myself", 1, "Good start! A grown-up can check more."),
                ("🙋", "Tell a grown-up now", 2, "Yes! You are NOT in trouble for telling."),
            ]),
            S("ask", "Something bad happened online a while ago. You're embarrassed to tell.", art="💭", stage="recovery", choices=[
                ("🙋", "Tell a grown-up", 2, "Yes! It's never too late to tell."),
                ("🤐", "Let it go", 0, "It's OK! Grown-ups understand. They've been there too."),
                ("🗣️", "Tell a friend", 1, "A start! A grown-up can help more."),
            ]),
        ],
    },
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
            grade.scenarios.all().delete()

            for s_index, s in enumerate(g["scenarios"]):
                scenario = Scenario.objects.create(
                    grade=grade,
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
                for c_index, (emoji, text, points, feedback) in enumerate(s["choices"]):
                    Choice.objects.create(
                        scenario=scenario,
                        emoji=emoji,
                        text=text,
                        points=points,
                        feedback=feedback,
                        order=c_index,
                    )

            self.stdout.write(self.style.SUCCESS(f"{grade.label}: {len(g['scenarios'])} scenarios loaded"))