"""Runs the summarize prompt over each chapter via the claude CLI."""


def summarize(chapter: str) -> dict:
    prompt = build_prompt(chapter)
    return ask_json(prompt)
