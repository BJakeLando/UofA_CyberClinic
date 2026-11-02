# Cyber Squad

A cyber-safety game for kids in grades 3 to 6 and Girl Scout troops. Players
learn to spot scams, fake messages, and unsafe meetups, and to tell a family
member or teacher instead of engaging.

## Run it locally

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    export DJANGO_DEBUG=True
    python manage.py migrate
    python manage.py seed_content
    python manage.py runserver

Run the tests with `python manage.py test cybergame`.

---

© 2026 Lando Technologies LLC. All rights reserved. See [LICENSE](LICENSE).
