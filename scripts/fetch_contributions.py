"""Coleta o calendário público de contribuições (sem token) -> data/contributions.json."""
import json, re, sys
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USER = "felipeJJD"
URL = f"https://github.com/users/{USER}/contributions"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    tips = {}
    for t in soup.find_all("tool-tip"):
        m = re.match(r"\s*(No|\d+)\s+contributions?", t.get_text())
        if m and t.get("for"):
            tips[t["for"]] = 0 if m.group(1) == "No" else int(m.group(1))
    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        days.append({
            "date": td["data-date"],
            "level": int(td.get("data-level", 0)),
            "count": tips.get(td.get("id"), 0),
        })
    days.sort(key=lambda d: d["date"])
    return days


def streaks(days):
    by = {d["date"]: d["count"] for d in days}
    if not by:
        return 0, 0, 0
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)
    # sequência atual: hoje ainda vazio não quebra a sequência
    cur, day = 0, date.fromisoformat(days[-1]["date"])
    if by[day.isoformat()] == 0:
        day -= timedelta(days=1)
    while by.get(day.isoformat(), 0) > 0:
        cur += 1
        day -= timedelta(days=1)
    return sum(by.values()), cur, longest


def main():
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0 (profile-readme)"}, timeout=30)
    r.raise_for_status()
    days = parse(r.text)
    if len(days) < 300:
        sys.exit(f"Calendário inesperado ({len(days)} dias); layout do GitHub mudou?")
    total, cur, longest = streaks(days)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "user": USER, "total": total, "current_streak": cur,
        "longest_streak": longest, "from": days[0]["date"], "to": days[-1]["date"],
        "days": days,
    }, ensure_ascii=False), encoding="utf-8")
    print(f"{len(days)} dias | total={total} | atual={cur} | maior={longest}")


if __name__ == "__main__":
    main()
