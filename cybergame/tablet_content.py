"""The pretend tablet: what is on it, round by round.

Intermediate and Advanced play these rounds on a full pretend tablet: a
lock screen, a home screen of apps, and real-feeling Messages, Phone,
Contacts, Mail, Web and a game. Nothing tells the kid which button is the
answer. They use the tablet the way they would use their own, and the
round ends when they do something that matters (or tap "I'm finished").

Intermediate shows pointer tips on the buttons and a hint line under the
tablet. Advanced shows nothing extra. Same rounds, same scoring.

WHY SOME ROUNDS ARE SAFE
The Girl Scouts worked out after a few questions that every answer was
"tell a parent and don't do anything." So two rounds here are ordinary
and safe (a text from Mom's saved number, a note from the teacher's real
address), and the right move is to just answer or read it. Doing nothing,
or reporting your own mom, loses stars there.

HOW A ROUND IS SCORED
Every tap that matters has an action key ("tell", "click_link", ...).
Each round lists its outcomes: (emoji, what-you-did, stars, feedback, key).
  - most keys END the round the moment they happen
  - keys listed in "partials" don't: they are remembered, and if the kid
    taps "I'm finished" the best one counts (e.g. reporting in the game)
  - "done" is what "I'm finished" scores when nothing better happened
Stars: 3 best, 1-2 safe but not the best, 0 not safe.

WORDING
Never "grown-up" or "adult" on its own: point a kid at a family member or
a teacher. Brand names stay made up or misspelled (Pixel Park, R0bux).
The school, the teacher and every number and address are made up; phone
numbers use 555-01xx, which is reserved for fiction.
"""

from copy import deepcopy

SCHOOL = "Maple Creek Elementary"
TEACHER_EMAIL = "mrivera@maplecreek-elementary.org"

# Saved contacts on every round's tablet. These are the "real" numbers.
CONTACTS = [
    {"id": "dad", "name": "Dad", "phone": "(520) 555-0111", "color": "#2f8fe8", "text": True},
    {"id": "grandma", "name": "Grandma", "phone": "(520) 555-0123", "color": "#7a5cff", "text": True},
    {"id": "mom", "name": "Mom", "phone": "(520) 555-0110", "color": "#ff5c8a", "text": True},
    {"id": "teacher", "name": "Ms. Rivera", "note": "Teacher", "phone": "(520) 555-0140",
     "email": TEACHER_EMAIL, "color": "#1f9d57", "text": False},
    {"id": "office", "name": "School Office", "note": SCHOOL, "phone": "(520) 555-0100",
     "color": "#ff8a3d", "text": False},
]

# Old texts so the Messages app looks lived-in.
THREADS = [
    {"id": "t_mom", "contact": "mom", "time": "Yesterday", "messages": [
        {"from": "them", "text": "Don't forget your lunchbox! 🍎", "time": "Yesterday 7:40 AM"},
        {"from": "me", "text": "Ok mom"},
    ]},
    {"id": "t_dad", "contact": "dad", "time": "Tuesday", "messages": [
        {"from": "me", "text": "Can we get pizza Friday?", "time": "Tuesday 6:02 PM"},
        {"from": "them", "text": "Deal 🍕"},
    ]},
    {"id": "t_grandma", "contact": "grandma", "time": "Sunday", "messages": [
        {"from": "them", "text": "Happy birthday sweetheart!! 🎂🎈 Love, Grandma", "time": "Sunday 9:15 AM"},
        {"from": "me", "text": "Thank you Grandma!! ❤️"},
    ]},
]

# What a contact texts back when the kid sends a plain "Hi!".
HELLO_BACK = {"mom": "Hi sweetie! 😊", "dad": "Hey bud! 👋", "grandma": "Hello dear! 💕"}

EMAILS = [
    {"id": "e_news", "from_name": "Pixel Park", "from_addr": "news@pixelpark-game.com",
     "subject": "Season 3 is here! 🎮", "preview": "New pets, new worlds, and a brand new map.",
     "time": "Mon", "body": ["Season 3 of Pixel Park is here!",
                             "Log in from the game to see the new pets and the new map.",
                             "Remember: Pixel Park staff will never ask for your password."]},
    {"id": "e_spelling", "from_name": "Ms. Rivera", "from_addr": TEACHER_EMAIL,
     "subject": "Spelling words this week", "preview": "Here are this week's words. Practice a little each night!",
     "time": "Mon", "body": ["Hi everyone!",
                             "This week's words: planet, rocket, orbit, gravity, comet.",
                             "Practice a little each night. Quiz on Friday!",
                             "Ms. Rivera"]},
]

GAME_CHAT = [
    {"kind": "system", "text": "Welcome to Pixel Park! Season 3 is live."},
    {"kind": "public", "who": "Bluebird42", "text": "anyone want to trade carrots?"},
    {"kind": "public", "who": "Zed_The_Great", "text": "lol my pet is so slow"},
    {"kind": "public", "who": "Bluebird42", "text": "ill trade 3 carrots for a hat"},
]


def tablet(key, prompt, outcomes, *, recap, lesson, nudge, stage="decide", **setup):
    """One tablet round, in the shape seed_content loads.

    `outcomes` rows are (emoji, what the kid did, stars, feedback, key).
    The rest of the keyword arguments become the tablet's setup, merged
    over the shared contacts, texts, emails and game chat above.
    """
    threads = {t["id"]: deepcopy(t) for t in THREADS}
    for t in setup.pop("threads", []):
        threads[t["id"]] = t
    emails = setup.pop("emails", []) + deepcopy(EMAILS)
    game = {"chat": deepcopy(GAME_CHAT), **setup.pop("game", {})}

    full = {
        "key": key,
        "time": "4:05",
        "day": "Thursday",
        "start": "home",
        "recap": recap,
        "lesson": lesson,
        "nudge": nudge,
        "contacts": deepcopy(CONTACTS),
        "hello_back": HELLO_BACK,
        # threads that came in today sort to the top
        "threads": sorted(threads.values(), key=lambda t: not t.get("unread")),
        "emails": emails,
        "game": game,
        "web": setup.pop("web", {}),
        "partials": [],
        **setup,
    }
    return {
        "kind": "tablet", "prompt": prompt, "stage": stage,
        "sender": "", "sender_emoji": "", "art": "", "question": "What do you do?",
        "hint": nudge, "setup": full,
        "choices": [(e, text, pts, fb, k) for e, text, pts, fb, k in outcomes],
    }


# ---------------------------------------------------------------------------
# 1. "Hey it's Dad, I got a new phone"
# ---------------------------------------------------------------------------

FAKE_DAD_NUMBER = "+1 (520) 555-0182"
FAKE_DAD_TEXT = "Hey it's Dad 😊 I just got a new phone. Can you come outside and meet me?"

FAKE_DAD = tablet(
    "fake_dad",
    "A text from a new number: \"Hey it's Dad, I got a new phone. Come outside.\"",
    [
        ("📞", "Called or texted Mom or Dad from Contacts", 3,
         "That's exactly right. The number saved in your Contacts is the real one, so that's how you check.", "tell"),
        ("🚫", "Blocked the number", 1,
         "Blocking is safe. But Mom or Dad need to know someone is pretending to be Dad.", "block"),
        ("⏹️", "Didn't answer, didn't tell", 1,
         "Not answering was smart. Next step: tell Mom or Dad using their saved number.", "done"),
        ("🚨", "Called 911", 1,
         "911 is for when someone is hurt or in danger right now. Call Mom or Dad at their saved number first.", "call_911"),
        ("🚶", "Went outside to meet", 0,
         "Anyone can type \"it's Dad.\" That number wasn't his. Never go outside because of a text you can't check.", "go_outside"),
        ("💬", "Texted back \"Who is this?\"", 0,
         "Even \"Who is this?\" is a reply. It tells them a real kid has this phone. Don't answer at all.", "ask_who"),
        ("📲", "Called the new number back", 0,
         "Calling back is still talking to them. Check with the number already saved in Contacts.", "call_unknown"),
    ],
    stage="recognize",
    recap="A text from a number you didn't know said, \"Hey it's Dad, I got a new phone. Come outside.\"",
    lesson="A new number that says \"it's Dad\" is a stranger until Dad says so. "
           "Check by calling or texting the number already saved in your Contacts.",
    nudge="Who is this text really from? Is that number saved in your Contacts?",
    time="3:41",
    notify={"delay": 1600, "app": "messages", "open": "t_unknown", "sound": "text",
            "title": FAKE_DAD_NUMBER, "body": FAKE_DAD_TEXT},
    threads=[{
        "id": "t_unknown", "number": FAKE_DAD_NUMBER, "time": "3:41 PM", "unread": True, "arrives": True,
        "messages": [{"from": "them", "text": FAKE_DAD_TEXT, "time": "Today 3:41 PM"}],
        "replies": [{"text": "OK, coming!", "act": "go_outside"},
                    {"text": "Who is this?", "act": "ask_who"}],
        "call": "call_unknown", "block": "block", "junk": "block", "delete": "block",
    }],
    calls={
        "mom": {"answer": True, "act": "tell",
                "says": "Hi sweetie! No, Dad didn't get a new phone. Stay inside. "
                        "I'm calling him right now. Thank you for checking with me!"},
        "dad": {"answer": True, "act": "tell",
                "says": "Hey kiddo, that wasn't me. My number hasn't changed. "
                        "Stay inside, okay? I'm really glad you called."},
        "default": {"answer": True, "act": "tell",
                    "says": "Thank you for telling me. Stay inside, and let's get your family on the phone."},
        "unknown": {"act": "call_unknown"},
        "911": {"act": "call_911"},
    },
    tell={"text": "Someone texted me from a new number saying they're Dad. They want me to go outside.",
          "act": "tell",
          "replies": {"mom": "Thank you for telling me! That's not Dad. Stay inside, I'm calling him now ❤️",
                      "dad": "That wasn't me, bud. Stay inside. Proud of you for checking 👍",
                      "default": "Thank you for telling me. Stay inside! ❤️"}},
    partials=["block"],
)


# ---------------------------------------------------------------------------
# 2. "You won a free trip to Hawaii!"
# ---------------------------------------------------------------------------

PRIZE = tablet(
    "phish_prize",
    "An email: \"You won a free trip to Hawaii! Click in the next 10 minutes.\"",
    [
        ("⚠️", "Reported it as phishing", 3,
         "Yes! Report tells the email company it's a scam, so it gets blocked for everyone.", "report"),
        ("🙋", "Told a family member", 2,
         "Telling is smart! In email, also tap Report so it gets blocked.", "tell"),
        ("🗑️", "Deleted it", 1,
         "Deleting is safe. Reporting is even better: it warns the email company.", "delete"),
        ("⏹️", "Didn't click anything", 1,
         "Good, you didn't click. Next time find the Report button.", "done"),
        ("🚨", "Called 911", 0,
         "911 is only for emergencies, when someone is hurt or in danger. A trick email isn't one.", "call_911"),
        ("🔗", "Clicked \"Claim my trip\"", 0,
         "Prize links like this steal passwords and information. You can't win a contest you never entered.", "click_link"),
        ("↩️", "Replied to the email", 0,
         "Replying tells the scammer your email is real, so they send more.", "reply_scam"),
    ],
    stage="recognize",
    recap="An email said you won a free trip to Hawaii, if you clicked in the next 10 minutes.",
    lesson="A prize you never entered, a hurry-up timer and a strange address are all signs of "
           "phishing. Don't click anything. Tap Report.",
    nudge="Look at who sent it. Did you enter a contest? Real emails don't rush you.",
    time="4:12",
    notify={"delay": 1600, "app": "mail", "open": "e_prize", "sound": "mail",
            "title": "Prize Center", "body": "🌴 YOU WON A FREE TRIP TO HAWAII!!!"},
    emails=[{
        "id": "e_prize", "from_name": "Prize Center", "from_addr": "winner@prize-claims-4u.co",
        "subject": "🌴 YOU WON A FREE TRIP TO HAWAII!!!", "preview": "Click here to claim your prize before it expires...",
        "time": "4:12 PM", "unread": True, "arrives": True, "loud": True,
        "body": ["CONGRATULATIONS!!! 🎉🎉🎉",
                 "You were picked out of 1,000,000 kids to win a FREE trip to Hawaii for your whole family!",
                 "Click the button in the next 10 MINUTES or your prize goes to someone else!"],
        "link": {"text": "CLAIM MY TRIP 🌴", "act": "click_link"},
        "replies": [{"text": "How do I get my prize?", "act": "reply_scam"},
                    {"text": "Is this real?", "act": "reply_scam"}],
        "report": "report", "delete": "delete",
    }],
    calls={
        "default": {"answer": True, "act": "tell",
                    "says": "Thanks for telling me! That's a trick email. Don't click anything. "
                            "You can tap Report on it so it gets blocked."},
        "911": {"act": "call_911"},
    },
    tell={"text": "I got an email that says I won a free trip to Hawaii.", "act": "tell",
          "replies": {"default": "That's a trick! Don't click anything. Tap Report on the email 👍"}},
    partials=["tell", "delete"],
)


# ---------------------------------------------------------------------------
# 3. SAFE: Mom's real text
# ---------------------------------------------------------------------------

MOM_PICKUP = "Hi sweetie! Practice is canceled today. I'll pick you up at 3:00 by the front office ❤️"

SAFE_MOM = tablet(
    "safe_mom",
    "A text from Mom's saved number: practice is canceled, pickup at 3.",
    [
        ("💬", "Answered Mom: \"OK! See you at 3\"", 3,
         "Right! It came from Mom's saved contact, it has no link, and it doesn't ask for anything secret. "
         "It's safe to answer.", "reply_ok"),
        ("📞", "Called to double-check", 2,
         "Checking is never bad! But this came from Mom's saved number, so you could just answer.", "call_check"),
        ("❓", "Asked \"Who is this?\"", 1,
         "It's Mom! Her name shows at the top because her number is saved in your Contacts.", "ask_who"),
        ("⏹️", "Didn't answer Mom", 0,
         "Mom was waiting to hear back! A normal text from her saved number is safe to answer.", "done"),
        ("🚫", "Blocked Mom", 0,
         "That was really Mom! Her name was at the top because her number is saved.", "block_mom"),
        ("🚨", "Called 911", 0,
         "911 is only for emergencies, when someone is hurt or in danger.", "call_911"),
    ],
    recap="Mom texted from her saved number: practice is canceled and she'll pick you up at 3.",
    lesson="Not every message is a trick! A text from a saved contact, with no link, "
           "no secret and nothing scary, is okay to answer.",
    nudge="Who sent this one? Not every message is a trick.",
    time="2:47",
    notify={"delay": 1600, "app": "messages", "open": "t_mom", "sound": "text",
            "title": "Mom", "body": MOM_PICKUP},
    threads=[{
        "id": "t_mom", "contact": "mom", "time": "2:47 PM", "unread": True, "arrives": True,
        "messages": [
            {"from": "them", "text": "Don't forget your lunchbox! 🍎", "time": "Yesterday 7:40 AM"},
            {"from": "me", "text": "Ok mom"},
            {"from": "them", "text": MOM_PICKUP, "time": "Today 2:47 PM"},
        ],
        "replies": [{"text": "OK! See you at 3 ❤️", "act": "reply_ok", "back": "Love you! See you soon 😘"},
                    {"text": "Who is this?", "act": "ask_who", "back": "It's Mom, silly! 😄"}],
        "block": "block_mom",
    }],
    calls={
        "mom": {"answer": True, "act": "call_check", "says": "Hi sweetie! Yep, that was me. See you at 3!"},
        "default": {"answer": True, "act": "call_check", "says": "Yep, Mom's picking you up today. See you later!"},
        "911": {"act": "call_911"},
    },
    tell={"text": "Mom says practice is canceled and she'll pick me up at 3.", "act": "call_check",
          "replies": {"default": "Sounds good! 👍"}},
)


# ---------------------------------------------------------------------------
# 4. A game friend wants to meet up
# ---------------------------------------------------------------------------

GAME_MEETUP = tablet(
    "game_meetup",
    "In Pixel Park, a game friend asks to meet in real life and says not to tell your parents.",
    [
        ("📞", "Told Mom, Dad or a teacher", 3,
         "Yes! Telling a family member or teacher is the most important step. "
         "\"Don't tell your parents\" is the biggest red flag there is.", "tell"),
        ("🚩", "Reported them in the game", 1,
         "Reporting helps the game stop them. Now tell a family member or teacher too.", "report_game"),
        ("🚫", "Blocked them in the game", 1,
         "Blocking is good. Now tell a family member or teacher too.", "block_game"),
        ("🚨", "Called 911", 1,
         "911 is for danger happening right now. Tell a family member or teacher. They can call the police if needed.", "call_911"),
        ("⏹️", "Didn't do anything", 0,
         "This person may ask other kids too. Report them, then tell a family member or teacher.", "done"),
        ("💬", "Said yes or asked where", 0,
         "Never meet someone from a game. People online can pretend to be any age.", "reply_meet"),
        ("🙅", "Answered \"I can't\"", 0,
         "Even \"I can't\" keeps the chat going. Don't answer at all. Go tell someone.", "reply_no"),
        ("➕", "Added them as a friend", 0,
         "Adding them lets them keep messaging you. Report them instead.", "add_friend"),
    ],
    recap="A game friend sent a private message asking to meet up in real life, and said not to tell your parents.",
    lesson="\"Don't tell your parents\" is the biggest red flag. Report them in the game, "
           "then tell a family member or teacher.",
    nudge="Tap a player's name in the chat to see what you can do. Then think: who else should know?",
    time="5:20",
    start="game",
    notify={"delay": 2400, "app": "game", "sound": "game",
            "title": "Pixel Park", "body": "New private message from BlockBuddy"},
    game={
        "pm": {"who": "BlockBuddy",
               "text": "hey ur my best game friend 😊 do u live near the big park? wanna meet up "
                       "saturday?? dont tell ur parents, its our secret"},
        "replies": [{"text": "Sure! Where?", "act": "reply_meet"},
                    {"text": "Which park?", "act": "reply_meet"},
                    {"text": "I can't, my parents won't let me", "act": "reply_no"}],
        "report": "report_game", "block": "block_game", "add": "add_friend",
    },
    calls={
        "default": {"answer": True, "act": "tell",
                    "says": "Thank you for telling me. You did the right thing. Don't answer them. "
                            "We'll report them together."},
        "911": {"act": "call_911"},
    },
    tell={"text": "Someone in Pixel Park asked me to meet up in real life and said not to tell you.",
          "act": "tell",
          "replies": {"mom": "Thank you for telling me! You did exactly the right thing. Don't answer them ❤️",
                      "default": "Thank you for telling me. You did the right thing."}},
    partials=["report_game", "block_game"],
)


# ---------------------------------------------------------------------------
# 5. SAFE: the teacher's real email
# ---------------------------------------------------------------------------

SAFE_TEACHER = tablet(
    "safe_teacher",
    "An email from Ms. Rivera's real school address: library books are due Friday.",
    [
        ("📖", "Read it (it was really Ms. Rivera)", 3,
         "Right! It came from Ms. Rivera's real school address, the same one saved in your Contacts. "
         "No links, nothing secret. It's safe.", "read"),
        ("↩️", "Replied \"Thanks, Ms. Rivera!\"", 3,
         "Nice! It's from her real school address, so replying is fine.", "reply_ok"),
        ("🙋", "Asked a family member about it", 2,
         "Asking is never wrong! This one was safe, though: the address matches Ms. Rivera's in Contacts.", "tell"),
        ("🗑️", "Deleted it without reading", 1,
         "That was a real note from your teacher. Check who it's from before you delete.", "delete"),
        ("⏹️", "Never opened it", 1,
         "That was a real note from your teacher! It's okay to open emails from people in your Contacts.", "done"),
        ("⚠️", "Reported it as phishing", 0,
         "This one was really from Ms. Rivera. Her address matches your Contacts. Report is for tricks.", "report_real"),
        ("🚨", "Called 911", 0,
         "911 is only for emergencies, when someone is hurt or in danger.", "call_911"),
    ],
    recap="Your teacher, Ms. Rivera, emailed a reminder from her real school address.",
    lesson="Check who it's from. If the address matches the one saved in your Contacts and "
           "there's no link and no secret, it's safe.",
    nudge="Is this email from someone you know? Compare the address to Ms. Rivera's in Contacts.",
    time="6:05",
    notify={"delay": 1600, "app": "mail", "open": "e_teacher", "sound": "mail",
            "title": "Ms. Rivera", "body": "Library books due Friday 📚"},
    emails=[{
        "id": "e_teacher", "from_name": "Ms. Rivera", "from_addr": TEACHER_EMAIL,
        "subject": "Library books due Friday 📚", "preview": "Hi everyone! Just a reminder that library books are due...",
        "time": "6:05 PM", "unread": True, "arrives": True,
        "body": ["Hi everyone!",
                 "Just a reminder that library books are due this Friday. If you can't find yours, "
                 "that's okay. Just let me know.",
                 "Have a great night!",
                 "Ms. Rivera"],
        "open": "read",
        "replies": [{"text": "Thanks, Ms. Rivera!", "act": "reply_ok"}],
        "report": "report_real", "delete": "delete",
    }],
    calls={
        "default": {"answer": True, "act": "tell",
                    "says": "Okay! That's a real note from your teacher. Thanks for letting me know."},
        "911": {"act": "call_911"},
    },
    tell={"text": "Ms. Rivera emailed that library books are due Friday.", "act": "tell",
          "replies": {"default": "Thanks for letting me know! 📚"}},
    partials=["read", "delete", "tell"],
)


# ---------------------------------------------------------------------------
# 6. "YOUR TABLET HAS A VIRUS AND IS LOCKED"
# ---------------------------------------------------------------------------

SCAM_SUPPORT = "1-888-555-0199"

VIRUS = tablet(
    "virus_popup",
    "A scary pop-up: \"Your tablet has a virus and is locked! Tap Update now!\"",
    [
        ("🏠", "Pressed Home, then told a family member", 3,
         "Exactly! A website can't lock your tablet. Home closes it, and telling a family member lets them check.", "tell"),
        ("🏠", "Pressed Home to close it", 1,
         "Good! Home closes the app. Now tell a family member about the pop-up.", "closed"),
        ("⏹️", "Left the pop-up on the screen", 0,
         "Don't leave it there. Press Home to close it, then tell a family member.", "done"),
        ("🔄", "Tapped \"Update now\"", 0,
         "That button is the trick. It can install a real virus. Use Home instead.", "tap_update"),
        ("📞", "Called the \"support\" number", 0,
         "Real tablets never show a number to call. Those people want money or passwords.", "call_scam"),
        ("🚨", "Called 911", 0,
         "911 is only for emergencies, when someone is hurt or in danger. A pop-up isn't one.", "call_911"),
    ],
    stage="recovery",
    recap="A scary pop-up said your tablet had a virus, was locked, and you had to tap Update now.",
    lesson="Websites can't lock your tablet. Don't tap anything in a scary pop-up. "
           "Press Home, then tell a family member.",
    nudge="Real virus warnings don't come from websites. Is there a way out that isn't inside the pop-up?",
    time="7:30",
    start="web",
    web={
        "site": "cartoons-free-hd.net/watch?v=funny-cats",
        "video": "Funny Cat Cartoons 😹 (full episode)",
        "popup": {
            "delay": 2600,
            "title": "⚠️ VIRUS DETECTED!",
            "lines": ["YOUR TABLET HAS (3) VIRUSES AND IS LOCKED!",
                      "Tap UPDATE NOW or all your photos and games will be DELETED."],
            "timer": 59,
            "button": {"text": "UPDATE NOW", "act": "tap_update"},
            "phone": {"text": "📞 Call Support: " + SCAM_SUPPORT, "act": "call_scam"},
        },
        "close": "closed",
    },
    calls={
        "default": {"answer": True, "act": "tell",
                    "says": "Those pop-ups are fake. Good job closing it and telling me!"},
        "911": {"act": "call_911"},
        "dial": {"18885550199": {"act": "call_scam"}},
    },
    tell={"text": "A scary pop-up said my tablet has a virus and is locked. I closed it and didn't tap anything.",
          "act": "tell",
          "replies": {"mom": "Good job closing it! Those pop-ups are fake. I'm proud of you ❤️",
                      "default": "Good job! That pop-up is fake. You did the right thing."}},
    partials=["closed"],
)


# ---------------------------------------------------------------------------
# 7. A threat against the school
#
# Modeled on the "Cat in the Hat" threat posts that hit schools, without
# drawing the character: the picture is an original, blurred shadow-cat,
# and the account name is misspelled like every other brand in the game.
#
# Mom doesn't answer, on purpose. The lesson is to keep going down the list
# until a family member or school staff picks up. Calling 911 is two stars,
# not three: police do want threats reported, but 911 is for danger
# happening right now, and the family member or school calls the police.
# ---------------------------------------------------------------------------

THREAT_NUMBER = "+1 (520) 555-0166"
THREAT_TEXT = ("I know where your school is. Something bad is going to happen there tomorrow. "
               "Send this to 5 friends or you're next.")

THREAT = tablet(
    "threat",
    "A text with a creepy picture says something bad will happen at your school.",
    [
        ("📞", "Kept trying until someone answered", 3,
         "Exactly right. Mom didn't answer, so you tried the next person. A threat always needs a family "
         "member or school staff right away. They call the police.", "tell"),
        ("🚨", "Called 911", 2,
         "Police do want to know about threats, so that's not wrong. But 911 is for danger happening right now. "
         "First try Dad, your teacher or the school office. They'll call the police for you.", "call_911"),
        ("⏳", "Tried Mom, then stopped", 1,
         "Good start! When someone doesn't answer, try the next person: Dad, your teacher or the school office.", "tried"),
        ("🚫", "Blocked the number", 1,
         "Blocking is okay, but a threat has to be told right away, and the police may need to see it.", "block"),
        ("⏹️", "Didn't tell anyone", 0,
         "A threat about your school always needs to be told, right away, even if it might be fake.", "done"),
        ("📤", "Forwarded it to friends", 0,
         "Never share a threat. It spreads fear, and police say sharing threats can get kids in real trouble.", "forward"),
        ("💬", "Texted back \"Who is this?\"", 0,
         "Don't reply to a threat at all. Show it to a family member or teacher.", "ask_who"),
        ("💬", "Texted back \"Leave me alone!\"", 0,
         "Even \"leave me alone\" is a reply. Don't answer at all. Show it to a family member or teacher.", "reply_back"),
        ("🗑️", "Deleted it", 0,
         "Don't delete it. The school or police may need to see it. Show it to a family member or teacher right away.", "delete"),
        ("📲", "Called the number back", 0,
         "Never call back. Tell a family member or teacher.", "call_unknown"),
    ],
    stage="report",
    recap="A text from a number you didn't know had a creepy picture and said something bad would happen at your school.",
    lesson="Don't answer, don't share, don't delete. Tell a family member or school staff right away. "
           "If one person doesn't answer, try the next. 911 is for danger happening right now.",
    nudge="This one is serious. Who can you reach right now? If someone doesn't answer, keep going.",
    time="8:14",
    notify={"delay": 1600, "app": "messages", "open": "t_threat", "sound": "text",
            "title": THREAT_NUMBER, "body": "📷 Photo"},
    threads=[{
        "id": "t_threat", "number": THREAT_NUMBER, "time": "8:14 PM", "unread": True, "arrives": True,
        "messages": [{"from": "them", "image": "threat", "time": "Today 8:14 PM"},
                     {"from": "them", "text": THREAT_TEXT}],
        "replies": [{"text": "Who is this??", "act": "ask_who"},
                    {"text": "Leave me alone!", "act": "reply_back"},
                    {"text": "📤 Forward to 5 friends", "act": "forward"}],
        "call": "call_unknown", "block": "block", "junk": "block", "delete": "delete",
    }],
    calls={
        "mom": {"answer": False, "act": "tried"},
        "dad": {"answer": True, "act": "tell",
                "says": "I'm really glad you told me. Don't answer it and don't send it to anyone. "
                        "I'm calling the school and the police right now."},
        "teacher": {"answer": True, "act": "tell",
                    "says": "Thank you for telling me right away. Don't share it. "
                            "I'm calling the principal and the police now."},
        "office": {"answer": True, "act": "tell",
                   "says": SCHOOL + ". Thank you for calling. I'm getting the principal "
                           "and the school police officer right now."},
        "default": {"answer": True, "act": "tell",
                    "says": "Oh sweetheart, thank you for telling me. I'm calling the police and your dad right now."},
        "unknown": {"act": "call_unknown"},
        "911": {"act": "call_911"},
    },
    tell={"text": "I got a scary text with a creepy picture. It says something bad will happen at my school tomorrow.",
          "act": "tell", "no_reply": ["mom"], "no_reply_act": "tried",
          "replies": {"dad": "I'm calling the school and the police right now. Don't answer it and don't share it. Proud of you.",
                      "default": "Thank you for telling me. I'm calling the police right now. Don't answer it or share it."}},
    partials=["tried", "block"],
)


# Play order: tricks and safe ones mixed, every app used.
ROUNDS = [FAKE_DAD, PRIZE, SAFE_MOM, GAME_MEETUP, SAFE_TEACHER, VIRUS, THREAT]
