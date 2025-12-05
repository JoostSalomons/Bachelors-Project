from nltk.tokenize import RegexpTokenizer
from typing import Generator
from twisted.internet.defer import DeferredList, inlineCallbacks
from autobahn.twisted.util import sleep
from src.robot_movements.gesture_library import head_nod_with_arms, arms_up_and_out, arms_up, arms_down
from alpha_mini_rug import perform_movement
from src.robot_movements.say_animated import say_animated
import random
@inlineCallbacks
def say_practice_sentence(session, sentence: str):
    yield session.call("rie.dialogue.config.language", lang="nl")
    yield perform_movement(session, frames = arms_up, mode="linear", force=True)
    sentence_parts = sentence.split("_")
    yield session.call("rie.dialogue.say", sentence_parts[0])
    yield perform_movement(session, frames = arms_down, mode="linear", force=True)
    #yield perform_movement(session=session, frames=frames, force=True)
    yield session.call("rie.dialogue.say", sentence_parts[1])

@inlineCallbacks
def respond_to_correct_answer(session, correct_sentence, correct_pronoun):
    full_sentence = correct_sentence.replace("_", correct_pronoun)
    sentence = full_sentence.split(".")[1]
    congratulary_sentences = [
        "Goed gedaan! De juiste zin was inderdaad "
    ]
    response = random.choice(congratulary_sentences) + sentence
    yield say_animated(session, response)
    return

def respond_to_wrong_answer(session):
    sad_sentences = [
        "Helaas! Dat was het verkeerde antwoord. Maar we kunnen het nog een keer proberen!"
    ]
    yield say_animated(session, random.choice(sad_sentences))
    return

def respond_to_wrong_answer_and_give_correct(session, correct_sentence, correct_pronoun):
    sad_sentences = [
        "Helaas! Dat was het verkeerde antwoord. Het juiste antwoord was:"
    ]

    full_sentence = correct_sentence.replace("_", correct_pronoun)
    sentence = full_sentence.split(".")[1]
    response = random.choice(sad_sentences) + correct_pronoun + sentence
    yield say_animated(session, response)
    return

def say_normally(session, text: str):
    yield session.call("rie.dialogue.say", text)
    return

if __name__ == "__main__":
    say_practice_sentence(0, "De computer is van _")