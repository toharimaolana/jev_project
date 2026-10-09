"""Demo of Jev, TypeSafe AI's System One model (https://typesafe.ai),
using the free "jev-1.13-free" model on OpenCode Zen.

Jev doesn't chat. It answers typed questions about some input ("state"):
  - Choice: pick one option -> chosen key, per-option probabilities, confidence
  - Score:  place the input on an ordered rubric -> probability-weighted position
  - Noul:   yes/no -> probability that the answer is yes (0.0 - 1.0)

OpenCode Zen serves Jev on the same System One API as TypeSafe, so the
official TypeSafe SDK works by pointing it at Zen's base URL.

Setup:
  pip install typesafe-sdk python-dotenv
  Put OPENCODE_API_KEY=... in .env (https://opencode.ai -> Zen -> API keys)

Run:  python demo.py                   # classify the built-in sample tickets
      python demo.py "your own text"   # classify your own message
"""

import os
import sys

from dotenv import load_dotenv
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient, TypeSafeError

BASE_URL = "https://opencode.ai/zen"
MODEL = "jev-1.13-free"

SAMPLE_TICKETS = [
    "Hi, I've been trying to connect my Stripe account for 3 days and the integration keeps failing. I'm losing sales. Please help ASAP.",
    "I was charged twice for my subscription this month. Can you refund one?",
    "Hello! Do you offer a discount for non-profits on the annual plan?",
]

# Questions write here, yaa


def classify(client: TypeSafeClient, ticket: str) -> None:
    response = client.system_one(state=ticket, questions=QUESTIONS)

    department = response.choices["department"]
    frustration = response.scores["frustration"]
    is_urgent = response.nouls["is_urgent"]

    print(f"\nTicket: {ticket}")
    print(f"  Department : {department.choice} "
          f"(confidence {department.confidence:.2f})")
    print("               " + ", ".join(
        f"{key}={p:.2f}" for key, p in department.probabilities.items()))
    # Score is a probability-weighted position on the rubric (0 = first level),
    # so round it to name the nearest level.
    level = frustration.legend[round(frustration.score)]
    print(f"  Frustration: {frustration.score:.2f} on a 0-2 scale -> {level} "
          f"(confidence {frustration.confidence:.2f})")
    print(f"  Urgent     : {'yes' if is_urgent.noul >= 0.5 else 'no'} "
          f"(p={is_urgent.noul:.2f})")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    load_dotenv()
    api_key = os.getenv("OPENCODE_API_KEY")
    if not api_key:
        sys.exit("OPENCODE_API_KEY is missing. Add it to your .env file.")

    tickets = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else SAMPLE_TICKETS

    print(f"Jev demo ({MODEL}): support-ticket classification")
    try:
        with TypeSafeClient(api_key=api_key, base_url=BASE_URL, model=MODEL) as client:
            for ticket in tickets:
                classify(client, ticket)
    except TypeSafeError as e:
        sys.exit(f"[error] {e}")


if __name__ == "__main__":
    main()
