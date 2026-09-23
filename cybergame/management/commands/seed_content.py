"""Load the Cyber Squad question bank.

Run:  python manage.py seed_content
Reset and reload:  python manage.py seed_content --reset

Points: 2 = best answer (refuse AND tell a grown-up)
        1 = safe but incomplete (refuse only)
        0 = unsafe choice (feedback explains, never scolds)
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from cybergame.models import Grade, Scenario, Choice


CONTENT = [
    {
        "number": 3,
        "label": "3rd Grade",
        "intro": "Let's practice making smart choices online.",
        "scenarios": [
            {
                "stage": "recognize",
                "prompt": "You're playing a game and a message pops up:\n\"You won 10,000 free coins! Click here to get them!\"",
                "choices": [
                    ("Click the button", 0, "Buttons like this almost never give you coins. They're a trick to get you to click. Nice try though — this one fools a lot of people!"),
                    ("Ignore it and keep playing", 1, "Good — ignoring it keeps you safe. One more step would make it even better: tell a grown-up you saw it."),
                    ("Ignore it and tell a grown-up", 2, "Perfect. You kept yourself safe AND let a grown-up know. That's exactly what a Cyber Squad member does."),
                ],
            },
            {
                "stage": "decide",
                "prompt": "Someone you don't know in a game asks:\n\"Hi! What school do you go to?\"",
                "choices": [
                    ("Tell them your school", 0, "Your school is private information. People you meet in games don't need to know where you are during the day."),
                    ("Don't answer and keep playing", 1, "Smart — you kept it private. Telling a grown-up would make it even better."),
                    ("Don't answer, and tell a grown-up", 2, "Excellent. Grown-ups like knowing when someone asks kids questions like that."),
                ],
            },
            {
                "stage": "decide",
                "prompt": "A player asks for your real name and what street you live on so they can \"send you a present.\"",
                "choices": [
                    ("Give them your address", 0, "Real presents don't need your address from a stranger in a game. Keep your name and address private — always."),
                    ("Say no thanks", 1, "Good answer. Saying no is the right move. Telling a grown-up makes it even stronger."),
                    ("Say no and tell a grown-up", 2, "That's the best move. You said no AND told someone who can help."),
                ],
            },
            {
                "stage": "recognize",
                "prompt": "A website says: \"Your computer has 5 problems! Click here to fix them fast!\"",
                "choices": [
                    ("Click to fix it", 0, "Real computer problems don't get announced by a website like that. This kind of message is trying to get you to click."),
                    ("Close the window", 1, "Closing it is the right idea. Tell a grown-up too, so they can check the computer."),
                    ("Close it and tell a grown-up", 2, "Perfect. A grown-up can make sure the computer is okay."),
                ],
            },
            {
                "stage": "report",
                "prompt": "Something online makes you feel confused or uncomfortable. Who can you tell?",
                "choices": [
                    ("Nobody — just keep it to yourself", 0, "You never have to handle it alone. There are lots of grown-ups who want to help."),
                    ("Only a friend your age", 1, "Telling a friend is okay, but a grown-up can actually do something about it."),
                    ("A parent, teacher, or any grown-up you trust", 2, "Yes! Parents, teachers, a counselor, a librarian — any grown-up you trust is a good choice."),
                ],
            },
            {
                "stage": "recovery",
                "prompt": "You clicked something by accident and now the computer is acting strange. What's the best thing to do?",
                "choices": [
                    ("Turn it off and hope nobody notices", 0, "This happens to almost everyone at some point — even grown-ups. Telling someone right away is what makes it easy to fix."),
                    ("Try to fix it yourself", 1, "It's good that you want to help. But a grown-up can fix it faster and won't be upset with you."),
                    ("Tell a grown-up right away", 2, "That's exactly right. Telling fast makes it much easier to fix — and you are not in trouble for telling."),
                ],
            },
            {
                "stage": "recovery",
                "prompt": "You told a grown-up about something online and they looked upset. What does that usually mean?",
                "choices": [
                    ("They're mad at you", 0, "Almost always, a grown-up's face like that means worried, not angry. They're thinking about how to help."),
                    ("You should stop telling them things", 0, "Please keep telling them! Grown-ups would much rather know than not know."),
                    ("They're worried about you, not angry at you", 2, "Exactly right. Worried and angry can look the same on a face, but they're very different."),
                ],
            },
        ],
    },
    {
        "number": 4,
        "label": "4th Grade",
        "intro": "Today we're practicing how to protect your accounts.",
        "scenarios": [
            {
                "stage": "decide",
                "prompt": "Someone in a game says:\n\"I'll give you a really rare item — just tell me your password first.\"",
                "choices": [
                    ("Give them the password", 0, "Nobody ever needs your password to give you something. A password is like a key to your house — it stays yours."),
                    ("Say no and keep playing", 1, "Good — your password stayed safe. Telling a grown-up makes it even better."),
                    ("Say no and tell a grown-up", 2, "Best move. You protected your account and let someone know what happened."),
                ],
            },
            {
                "stage": "recognize",
                "prompt": "A link in the game chat says:\n\"FREE ROBUX GENERATOR — works 100%!\"",
                "choices": [
                    ("Click it and try it", 0, "Free currency generators aren't real. They're built to take accounts, not give things away."),
                    ("Skip it", 1, "Right call. Mentioning it to a grown-up or teacher helps them warn other kids too."),
                    ("Skip it and tell a grown-up", 2, "Perfect. Now a grown-up can warn other students about the same link."),
                ],
            },
            {
                "stage": "recognize",
                "prompt": "A message comes from your friend's account:\n\"Hey, can I borrow your login real quick?\"",
                "choices": [
                    ("Send it — it's your friend", 0, "It might not be your friend. When an account gets taken over, the messages still look like they came from them."),
                    ("Don't send it, and ask your friend in person tomorrow", 1, "Smart thinking. Checking in person is a great habit. Add a grown-up and it's perfect."),
                    ("Don't send it, and tell a grown-up", 2, "Exactly. If your friend's account was taken over, a grown-up can help them get it back."),
                ],
            },
            {
                "stage": "decide",
                "prompt": "A fun quiz online says: \"Enter your full name, birthday, and street to find out your spirit animal!\"",
                "choices": [
                    ("Fill it in — it's just a quiz", 0, "Quizzes like this are often collecting information, not guessing animals. Your birthday and address are private."),
                    ("Close the quiz", 1, "Good instinct. Those details are worth protecting."),
                    ("Close it and tell a grown-up", 2, "Great choice. Grown-ups like to know which sites are asking kids for that kind of information."),
                ],
            },
            {
                "stage": "report",
                "prompt": "You're not sure whether something online is okay or not. What should you do?",
                "choices": [
                    ("Guess and hope it's fine", 0, "Guessing is stressful! You don't have to figure it out by yourself."),
                    ("Wait and see what happens", 1, "Waiting usually makes things harder to fix. Asking early is better."),
                    ("Ask a grown-up — even if you're not sure it's a problem", 2, "Yes. You never need to be sure before you ask. 'I'm not sure about this' is a great sentence."),
                ],
            },
            {
                "stage": "recovery",
                "prompt": "You typed your password into a website and now you think it might have been a fake one.",
                "choices": [
                    ("Do nothing and hope it's fine", 0, "This is fixable! Changing a password takes about a minute — but only if someone knows to do it."),
                    ("Change the password yourself later", 1, "Good instinct. Doing it with a grown-up right now is even better, because they can check the other accounts too."),
                    ("Tell a grown-up now so you can change it together", 2, "Perfect. Fast is what matters here, and you won't be in trouble for telling."),
                ],
            },
            {
                "stage": "recovery",
                "prompt": "You clicked something bad a few days ago and never told anyone. Is it too late?",
                "choices": [
                    ("Yes, too late — don't bother", 0, "It's never too late. Telling now is still much better than never telling."),
                    ("Wait a bit longer and see", 1, "Waiting doesn't make it better. Today is a good day to say something."),
                    ("No — tell a grown-up today", 2, "Right. Late is still worth it, and nobody will be upset that you came forward."),
                ],
            },
        ],
    },
    {
        "number": 5,
        "label": "5th Grade",
        "intro": "Let's practice spotting tricks that don't look like tricks.",
        "scenarios": [
            {
                "stage": "decide",
                "prompt": "Someone you've played with a few times says:\n\"Let's talk somewhere else. Add me on this other app.\"",
                "choices": [
                    ("Add them on the other app", 0, "Moving to another app is a common move, because the new place usually has fewer safety rules. Staying put is safer."),
                    ("Say no thanks and keep playing", 1, "Good — you stayed where the safety settings are. Telling a grown-up would finish the job."),
                    ("Say no and tell a grown-up", 2, "Exactly right. This is one of the most important things to report."),
                ],
            },
            {
                "stage": "recognize",
                "prompt": "A message says:\n\"I'm a game moderator. There's a problem with your account — send me your password so I can fix it.\"",
                "choices": [
                    ("Send the password", 0, "Real moderators never ask for your password. They already have the tools they need."),
                    ("Refuse and report them in the game", 1, "Great — reporting in the game helps. Telling a grown-up helps even more."),
                    ("Refuse, report them, and tell a grown-up", 2, "Perfect. You handled it in the game and looped in a grown-up."),
                ],
            },
            {
                "stage": "decide",
                "prompt": "Someone offers you a rare item and says:\n\"Just don't tell your parents about this, okay?\"",
                "choices": [
                    ("Agree — it's just an item", 0, "Anytime someone asks you to keep something from your parents, that's the signal to tell them. Good people don't need secrets from your family."),
                    ("Refuse the trade", 1, "Good call. The secret part is the real red flag here."),
                    ("Refuse and tell a parent right away", 2, "That's the best answer. 'Don't tell your parents' is always worth telling your parents about."),
                ],
            },
            {
                "stage": "recognize",
                "prompt": "A player says they'll mail you a free gaming headset. They just need your address.",
                "choices": [
                    ("Send your address", 0, "Your address is one of the most private things you have. Nobody online needs it for a prize."),
                    ("Say no", 1, "Right answer. Keeping your address private is a solid habit."),
                    ("Say no and tell a grown-up", 2, "Exactly. A grown-up should know when someone asks a kid for their address."),
                ],
            },
            {
                "stage": "report",
                "prompt": "A friend tells you something happened to them online and asks you not to tell anyone.",
                "choices": [
                    ("Keep the secret", 0, "Being a good friend sometimes means getting them help, even when it's uncomfortable."),
                    ("Tell them to handle it themselves", 0, "That leaves your friend alone with a hard problem. Friends can do better than that."),
                    ("Tell them you care, and bring it to a grown-up", 2, "That's real friendship. Some things are too big for kids to carry alone."),
                ],
            },
            {
                "stage": "recovery",
                "prompt": "You clicked a link and something downloaded onto the school Chromebook.",
                "choices": [
                    ("Delete it and say nothing", 0, "Deleting might not be enough, and your teacher won't be upset. They deal with this all the time."),
                    ("Close the Chromebook and deal with it later", 1, "Understandable — but the sooner someone knows, the easier it is to fix."),
                    ("Tell your teacher right away", 2, "Perfect. Teachers would much rather hear about it in the first minute than the next week."),
                ],
            },
            {
                "stage": "recovery",
                "prompt": "You're worried you'll get in trouble for clicking something. What's actually true?",
                "choices": [
                    ("You'll be in trouble, so stay quiet", 0, "Almost never true. What grown-ups care about is fixing it, not blaming you."),
                    ("Wait and see if anything bad happens", 1, "Waiting makes the fix harder. Speaking up early is the stronger move."),
                    ("Grown-ups would much rather help now than find out later", 2, "Exactly right. Telling is the thing that gets you out of the problem, not into one."),
                ],
            },
        ],
    },
    {
        "number": 6,
        "label": "6th Grade",
        "intro": "The tricks get better at this age. Let's practice the ones that are hard to spot.",
        "scenarios": [
            {
                "stage": "decide",
                "prompt": "Someone online you've talked to for weeks says:\n\"Don't tell your parents we're talking. It's just between us.\"",
                "choices": [
                    ("Agree — you've known them a while", 0, "How long you've talked doesn't change this one. A request for secrecy from your family is the clearest warning sign there is."),
                    ("Stop talking to them", 1, "Good. Stopping protects you. Telling a parent protects other kids too."),
                    ("Stop talking to them and tell a parent right away", 2, "That's exactly right, and it takes guts. Secrecy is the tool that makes everything else possible."),
                ],
            },
            {
                "stage": "decide",
                "prompt": "Someone you only know online asks you to send a photo of yourself.",
                "choices": [
                    ("Send one — it's just a picture", 0, "Once a photo is sent, you can't take it back or control where it goes. This one is always worth saying no to."),
                    ("Say no and stop replying", 1, "Good decision. Add a grown-up and you've handled it completely."),
                    ("Say no and tell a parent or teacher", 2, "That's the right move every time. Grown-ups need to know when someone asks a kid for photos."),
                ],
            },
            {
                "stage": "recognize",
                "prompt": "A message from a friend's account says:\n\"I got locked out. Can you read me the code that just got texted to you?\"",
                "choices": [
                    ("Read them the code", 0, "That code is what protects your account. Sharing it is how accounts get taken over — and the message may not be from your friend at all."),
                    ("Refuse and call your friend directly", 1, "Excellent instinct. Checking through a different channel is exactly how you verify."),
                    ("Refuse, check with your friend in person, and tell a grown-up", 2, "Perfect. You protected your account and helped your friend find out they were hacked."),
                ],
            },
            {
                "stage": "recognize",
                "prompt": "Someone is being really nice to you online — compliments, gifts in game, checking in every day. Then they start asking you to do small favors.",
                "choices": [
                    ("Do the favors — they've been nice to you", 0, "Being nice first and asking later is a pattern worth knowing about. Kindness with strings attached isn't kindness."),
                    ("Stop responding", 1, "Good. Stepping back is the right instinct when favors start showing up."),
                    ("Stop responding and talk to a parent about it", 2, "Exactly. This pattern is hard to spot from the inside, which is why talking to someone outside it helps so much."),
                ],
            },
            {
                "stage": "report",
                "prompt": "You feel silly bringing something small to a grown-up. Should you still do it?",
                "choices": [
                    ("No — save it for something big", 0, "Small things are exactly what grown-ups want to hear about, because small is easy to handle."),
                    ("Only if it happens again", 1, "Waiting for a pattern means the problem gets bigger first. Earlier is better."),
                    ("Yes — small things are easy to deal with early", 2, "Right. Nobody has ever been annoyed that a kid spoke up too soon."),
                ],
            },
            {
                "stage": "recovery",
                "prompt": "You already shared your password with someone online. What now?",
                "choices": [
                    ("Hope they don't use it", 0, "This is very fixable, but only if someone changes that password soon. Speak up and it's a five-minute problem."),
                    ("Change it yourself and move on", 1, "Good start. A grown-up can also check whether that password was used anywhere else."),
                    ("Tell a grown-up now and change it together", 2, "Perfect. Fast beats perfect here, and you're not in trouble for coming forward."),
                ],
            },
            {
                "stage": "recovery",
                "prompt": "Something happened online a while ago and you never told anyone. You still think about it.",
                "choices": [
                    ("It's been too long — let it go", 0, "If you're still thinking about it, it's still worth telling. There's no expiration date on asking for help."),
                    ("Tell a friend instead", 1, "Talking to a friend is a start, but a grown-up can actually do something about it."),
                    ("Tell a parent, teacher, or counselor — it's never too late", 2, "Exactly. Whatever it is, it's easier to carry once someone else knows about it."),
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Load the Cyber Squad grade content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing grades and scenarios before loading.",
        )

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
                    prompt=s["prompt"],
                    order=s_index,
                    active=True,
                )
                for c_index, (text, points, feedback) in enumerate(s["choices"]):
                    Choice.objects.create(
                        scenario=scenario,
                        text=text,
                        points=points,
                        feedback=feedback,
                        order=c_index,
                    )

            self.stdout.write(
                self.style.SUCCESS(f"{grade.label}: {len(g['scenarios'])} scenarios loaded")
            )