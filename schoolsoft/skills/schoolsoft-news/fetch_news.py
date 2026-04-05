#!/usr/bin/env python3
"""Fetch and display news from SchoolSoft as guardian (vardnadshavare)."""

import html
import os
import re
import sys
import textwrap

import requests
from bs4 import BeautifulSoup, NavigableString

BASE = "https://sms.schoolsoft.se"


def get_config():
    username = os.environ.get("SCHOOLSOFT_USERNAME")
    password = os.environ.get("SCHOOLSOFT_PASSWORD")
    school = os.environ.get("SCHOOLSOFT_SCHOOL")

    missing = []
    if not username:
        missing.append("SCHOOLSOFT_USERNAME")
    if not password:
        missing.append("SCHOOLSOFT_PASSWORD")
    if not school:
        missing.append("SCHOOLSOFT_SCHOOL")

    if missing:
        print(f"Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        print("Set them in ~/.claude/settings.json under env, or in your shell profile.", file=sys.stderr)
        sys.exit(1)

    return username, password, school


def login(username, password, school):
    """Authenticate and return an authenticated requests.Session."""
    # Step 1: Get app key via mobile app API
    resp = requests.post(
        f"{BASE}/{school}/rest/app/login",
        data={
            "identification": username,
            "verification": password,
            "logintype": "4",
            "usertype": "2",
        },
        timeout=15,
    )
    if resp.status_code == 401:
        print("Login failed: invalid credentials.", file=sys.stderr)
        sys.exit(1)
    resp.raise_for_status()
    data = resp.json()

    app_key = data["appKey"]
    student = data["students"][0]
    student_id = student["userId"]
    org_id = student["orgs"][0]["orgId"]

    # Step 2: Get token
    resp = requests.get(
        f"{BASE}/{school}/rest/app/token",
        headers={
            "appversion": "2.3.2",
            "appos": "android",
            "appkey": app_key,
            "deviceid": "",
        },
        timeout=15,
    )
    resp.raise_for_status()
    token = resp.json()["token"]

    # Step 3: Create authenticated web session via token login
    session = requests.Session()
    login_url = (
        f"https://sms1.schoolsoft.se/{school}/jsp/app/TokenLogin.jsp"
        f"?token={token}&orgid={org_id}"
        f"&childid={student_id}&usertype=2"
        f"&redirect=https%3A%2F%2Fsms.schoolsoft.se%2F{school}"
        f"%2Fjsp%2Fstudent%2Fright_student_startpage.jsp"
    )
    session.get(login_url, allow_redirects=True, timeout=15)

    return session, school, data["name"], student["name"]


def clean_text(element):
    """Extract clean text from a BeautifulSoup element, preserving paragraph breaks."""
    if element is None:
        return ""

    parts = []
    for child in element.descendants:
        if isinstance(child, NavigableString):
            text = str(child)
            text = html.unescape(text)
            parts.append(text)
        elif child.name in ("br", "p", "div"):
            parts.append("\n")

    text = "".join(parts)
    # Collapse multiple whitespace (but keep newlines)
    text = re.sub(r"[^\S\n]+", " ", text)
    # Collapse 2+ newlines into 1
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def wrap_text(text, width=80):
    """Word-wrap text while preserving paragraph breaks."""
    lines = text.split("\n")
    wrapped = []
    for line in lines:
        line = line.strip()
        if line:
            wrapped.append(textwrap.fill(line, width=width))
        else:
            wrapped.append("")
    return "\n".join(wrapped)


def fetch_news(session, school):
    """Fetch and parse news from the student news page."""
    url = f"{BASE}/{school}/jsp/student/right_student_news.jsp"
    resp = session.get(url, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    articles = []

    for group in soup.find_all("div", class_="accordion-group"):
        heading = group.find("div", class_="accordion-heading-left")
        if not heading:
            continue

        # Title
        title_el = heading.find("div", recursive=False)
        title = title_el.get_text(strip=True) if title_el else ""

        # Body
        body_el = group.find("div", class_="accordion_inner_left")
        body = clean_text(body_el)

        # Fallback to preview if no body
        if not body:
            preview_el = heading.find("div", class_="preview-block")
            body = clean_text(preview_el)

        # Metadata — labels are <label> elements, values are next sibling <div>
        meta = {}
        info_el = group.find("div", class_="inner_right_info")
        if info_el:
            for label in info_el.find_all("label"):
                label_text = label.get_text(strip=True)
                value_div = label.find_next_sibling("div")
                if not value_div:
                    continue
                value = value_div.get_text(strip=True)
                if label_text == "Från":
                    meta["from"] = value
                elif label_text == "Publicerad":
                    meta["published"] = value

        articles.append({"title": title, "body": body, "meta": meta})

    return articles


def main():
    username, password, school = get_config()

    try:
        session, school, guardian, student = login(username, password, school)
    except requests.exceptions.RequestException as e:
        print(f"Network error during login: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"SchoolSoft Nyheter — {guardian} (vardnadshavare for {student})")
    print()

    try:
        articles = fetch_news(session, school)
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching news: {e}", file=sys.stderr)
        sys.exit(1)

    if not articles:
        print("Inga nyheter hittades.")
        return

    for i, article in enumerate(articles, 1):
        title = article["title"]
        meta = article["meta"]
        body = article["body"]

        print(f"{'─' * 60}")
        print(f"  {title}")
        parts = []
        if meta.get("published"):
            parts.append(f"Publicerad: {meta['published']}")
        if meta.get("from"):
            parts.append(f"Från: {meta['from']}")
        if parts:
            print(f"  {' | '.join(parts)}")
        print(f"{'─' * 60}")
        print(wrap_text(body))
        print()

    print(f"Totalt {len(articles)} nyheter.")


if __name__ == "__main__":
    main()
