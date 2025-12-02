"""
Description:
    This module provides functionality to generate messages using OpenAI's
    GPT-3.5. It takes a prompt as input and returns a generated response in
    lowercase, ensuring that no inappropriate or offensive content is included.
    The script checks for profanity using Sightengine and regenerates the
    response if needed. The API key must be set in the environment variables
    for the script to work.
"""

import os
import json
import openai
import requests


API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please set it in your environment variables.")

client = openai.Client(api_key=API_KEY)


def check_profanity(text: str, timeout: int = 10) -> dict:
    """
    Checks the given text for profanity using the Sightengine API.
    This approach is based on the Sightengine Profanity Detection API, which
    can identify offensive language, including hate speech, offensive words,
    and inappropriate content.

    For more details on the API and its rules, visit:
    https://sightengine.com/docs/profanity-detection-hate-offensive-text-moderation

    Args:
        text (str): The text to check for profanity.
        timeout (int): Timeout for the request in seconds. Default is 10
            seconds.

    Returns:
        dict: The API response in JSON format, containing information on
        detected profanity.
    """
    data = {'text': text, 'mode': 'rules', 'lang': 'nl'}
    headers = {'Authorization': API_KEY}

    try:
        r = requests.post('https://api.sightengine.com/1.0/text/check.json', data=data, headers=headers, timeout=timeout)
        return json.loads(r.text)
    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
        print(f"Request failed: {e}")
        return {}


def generate_message_using_llm(original_prompt: str) -> str:
    """
    Generates a message based on a given prompt using OpenAI's GPT-3.5 and
    ensures no profanity is included. Also ensures the language is safe
    and appropriate for children.

    Args:
        original_prompt (str): The initial prompt to send to the OpenAI API.

    Returns:
        str: A generated response from the OpenAI API, in lowercase, with no
        profanity.

    Raises:
        RuntimeError: If the LLM response is empty.
    """
    prompt = original_prompt
    avoided_words = []
    system_prompt = (
        "Je bent een vriendelijke, educatieve robot die spreekt tegen kinderen van 7-10 jaar "
        "Houd jouw taalgebruik leuk, veilig en simpel en gebruik nooit ongepaste of enge tekst "
    )

    while True:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        if not completion.choices:
            raise RuntimeError("LLM response is empty.")

        response = completion.choices[0].message.content.strip()

        profanity = check_profanity(response)

        if profanity and profanity.get("profanity", {}).get("matches"):
            matches = profanity["profanity"]["matches"]
            new_words = [match["match"] for match in matches if match["match"] not in avoided_words]

            if new_words:
                avoided_words.extend(new_words)
                avoided_words_str = ", ".join(avoided_words)
                print(avoided_words_str)
                prompt = original_prompt + f" Do not use the word(s): '{avoided_words_str}'."

        else:
            return response.lower()

def generate_conversation_using_llm(original_prompt: str, conversation) -> str:
    """
    Generates a message based on a given prompt using OpenAI's GPT-3.5 and
    ensures no profanity is included. Also ensures the language is safe
    and appropriate for children.

    Args:
        original_prompt (str): The initial prompt to send to the OpenAI API.

    Returns:
        str: A generated response from the OpenAI API, in lowercase, with no
        profanity.

    Raises:
        RuntimeError: If the LLM response is empty.
    """
    prompt = original_prompt
    avoided_words = []
    system_prompt = (
        "Je bent een vriendelijke, educatieve robot die spreekt tegen kinderen van 7-10 jaar "
        "Houd jouw taalgebruik leuk, veilig en simpel en gebruik nooit ongepaste of enge tekst "
    )

    while True:
        completion = client.responses.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            conversation=conversation
        )

        if not completion.choices:
            raise RuntimeError("LLM response is empty.")

        response = completion.choices[0].message.content.strip()

        profanity = check_profanity(response)

        if profanity and profanity.get("profanity", {}).get("matches"):
            matches = profanity["profanity"]["matches"]
            new_words = [match["match"] for match in matches if match["match"] not in avoided_words]

            if new_words:
                avoided_words.extend(new_words)
                avoided_words_str = ", ".join(avoided_words)
                print(avoided_words_str)
                prompt = original_prompt + f" Do not use the word(s): '{avoided_words_str}'."

        else:
            return response.lower()