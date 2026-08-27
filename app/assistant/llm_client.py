import os
import time

import requests
from dotenv import load_dotenv

from app.assistant.prompts import SYSTEM_PROMPT

load_dotenv()

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

print("API Key Loaded:", bool(OPENROUTER_API_KEY))

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

# Transient transport-layer errors (SSL/connection resets) are almost
# always caused by something *outside* the Python process -- a VPN
# client, corporate SSL-inspecting proxy/EDR agent, a flaky Wi-Fi/VPN
# re-key, or (if this module is ever imported before a Flask/gunicorn
# fork) a non-fork-safe OpenSSL state. None of these can be fixed by
# changing the JSON payload, so instead we make the client resilient:
# every attempt gets a brand-new TCP+TLS handshake (no keep-alive),
# we don't trust any ambient proxy env vars unless explicitly set for
# this session, and we retry a couple of times with backoff before
# giving up.
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 1.5


def _post_with_retries(payload):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Force a fresh connection on every attempt instead of letting
        # a middlebox/OS keep a half-broken keep-alive socket around.
        "Connection": "close",
    }

    last_exception = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with requests.Session() as session:
                # Ignore HTTP_PROXY/HTTPS_PROXY/NO_PROXY inherited from
                # the shell/VPN/MDM environment. If a stray proxy env
                # var is silently intercepting traffic for this process
                # but not for a bare one-off script, this removes that
                # asymmetry.
                session.trust_env = False

                response = session.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json=payload,
                    timeout=30,
                )
            return response

        except (requests.exceptions.SSLError,
                 requests.exceptions.ConnectionError) as exc:
            last_exception = exc
            print(
                f"\n[generate_response] Transient transport error on "
                f"attempt {attempt}/{MAX_RETRIES}: {type(exc).__name__}: {exc}"
            )
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)

    raise last_exception


def _build_user_content(prompt: str, context: str | None):
    """
    Combine the raw user message with retrieved restaurant context
    (if any) so the model only ever talks about restaurants that were
    actually retrieved from the dataset, per the retrieval-first
    workflow in PROJECT_PLAN.md.
    """

    if not context:
        return prompt

    return (
        f"User question:\n{prompt}\n\n"
        f"Retrieved restaurant context (only use these, do not invent "
        f"others):\n{context}"
    )


def generate_response(prompt: str, context: str | None = None):

    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY not found in environment variables."
        )

    user_content = _build_user_content(prompt, context)

    payload = {
        "model": "openai/gpt-4.1-mini",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_content,
            }
        ],
        "temperature": 0.7,
    }

    print("\nMODEL:")
    print(payload["model"])

    print("\nUSER CONTENT LENGTH:")
    print(len(user_content))

    print("\nFIRST 500 CHARS OF USER CONTENT:")
    print(user_content[:500])

    try:
        response = _post_with_retries(payload)
    except (requests.exceptions.SSLError,
            requests.exceptions.ConnectionError) as exc:
        print("\n[generate_response] All retries exhausted:")
        print(f"{type(exc).__name__}: {exc}")
        return (
            "Sorry, the language model is currently unavailable. "
            "Please try again in a few moments."
        )

    if response.status_code != 200:
        print("\nStatus Code:")
        print(response.status_code)

        print("\nResponse:")
        print(response.text)

        return (
            "Sorry, the language model is currently unavailable. "
            "Please try again in a few moments."
        )

    result = response.json()

    return result["choices"][0]["message"]["content"]