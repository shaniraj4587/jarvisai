"""
TIME INFORMATION UTILITY
========================

Returns a short, readable string with the current date and time.
This is injected into the system prompt so the LLM can answer
questions like "what day is it?" and similar time-aware prompts.

Used by:
- GroqService
- RealtimeGroqService
"""

import datetime


def get_time_information() -> str:
    """
    Return a formatted multi-line string containing:
    - day name
    - date
    - month
    - year
    - current time (24-hour format)
    """

    now = datetime.datetime.now()

    return (
        f"Current Real-time Information:\n"
        f"Day: {now.strftime('%A')}\n"  # Example: Monday
        f"Date: {now.strftime('%d')}\n"  # Example: 05
        f"Month: {now.strftime('%B')}\n"  # Example: February
        f"Year: {now.strftime('%Y')}\n"  # Example: 2026
        f"Time: "
        f"{now.strftime('%H')} hours, "
        f"{now.strftime('%M')} minutes, "
        f"{now.strftime('%S')} seconds\n"
    )
