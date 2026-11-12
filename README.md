# My Portfolio

A personal portfolio website that showcases my work, interests, and development journey.

## Overview

This project acts as a digital profile for my projects and technical interests. It is designed to present my work clearly and professionally while making it easy for visitors to explore my apps, ideas, and skills.

## What it includes

- Intro and personal branding
- Project highlights
- Technical stack overview
- Contact and navigation sections
- Clean, simple web presentation

## Tech stack

- Python
- Flask
- HTML
- CSS
- JavaScript

## Run locally

Use Python 3.10 or later. Create a fresh environment rather than using the
legacy Windows `.venv` checked into this repository.

```bash
python -m venv .venv-local
source .venv-local/bin/activate
pip install -r requirements.txt
```

On Windows, activate with `.venv-local\Scripts\activate` instead.

Create a `.env` file (ignored by Git) with a randomly generated session key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

```dotenv
SECRET_KEY=replace-with-your-generated-key
# Optional: enable contact form delivery with a Gmail account and app password.
MAIL_USERNAME=
MAIL_PASSWORD=
```

Never commit real credentials. `SECRET_KEY` is required and must stay stable
across server restarts/workers. Without both mail settings, the portfolio still
loads and shows a direct email link instead of an unusable form.

```bash
python app.py
```

Open http://127.0.0.1:5000. For development-only debugging, use
`flask --app app run --debug`; debugging is off by default.

## Deployment

Set `SECRET_KEY`, `MAIL_USERNAME`, and `MAIL_PASSWORD` in the hosting platform's
environment settings. Gmail requires an **app password**, not your normal login
password, and the host must allow outbound SMTP on port 587.

```bash
gunicorn app:app
```

Serve the app over HTTPS. Do not cache HTML containing the contact form: its
CSRF token is session-specific. Contact messages are validated on the server
(name: 100 characters, email: 254, subject: 150, message: 5,000).
Failed delivery returns an explicit error and preserves the draft; successful
delivery redirects to contact to prevent resending on refresh. Replying to a
notification uses the visitor's email address.

## Checks

```bash
python -m unittest discover -s tests -v
node --check static/js/main.js
```

Tests use isolated test configuration and mocked mail delivery; they do not
send email. Optional browser regression checks start their own local server:

```bash
pip install -r requirements-dev.txt
python -m playwright install chromium
python -m unittest discover -s tests -p browser_checks.py -v
```

These cover mobile navigation (including Escape), layouts from 320 to 1440
pixels, reduced motion, JavaScript-disabled rendering, and contact submission.
The interface uses system fonts and inline SVG icons, so it does not depend
on third-party font or icon CDNs.

## Purpose

This portfolio helps communicate who I am as a developer, what I build, and the kind of products I am interested in creating.
