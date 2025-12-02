import time
from typing import Generator, Optional, Dict
from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.util import sleep
# from src.robot_movements.say_animated import say_animated
from src.utils import generate_message_using_llm
from alpha_mini_rug import perform_movement
from src.speech_processing.speech_session import SpeechRecognitionSession
from src.pronoun_game.llm_interface import LLMGameHelper
from src.pronoun_game.acuro_card_recognition import aruco_scan,aruco_scan_specific_card
from src.robot_responses.responses import say_practice_sentence, respond_to_correct_answer,\
    respond_to_wrong_answer, respond_to_wrong_answer_and_give_correct, say_normally
from src.robot_movements.gesture_library import arms_up, arms_down
import random

MAX_ATTEMPTS_ARUCO = 2
MAX_ATTEMPTS_SPEECH = 2
class PronounGame:
    def __init__(self, session, version, sentences):
        self.session = session
        self.version = version
        self.game_helper = LLMGameHelper()
        self.speech_recognition_session = SpeechRecognitionSession(self.session, self.version)
        self.sentences = sentences

    @inlineCallbacks
    def try_aruco_reading(self, practice_card=0):
        yield say_normally(self.session, "Dan gaan we nu oefenen met het scannen van de kaarten. Kan je de kaart scannen met"
                                   "een jongen en een computer? Hij heeft het nummer nul op de voorkant staan."
                                   "Ik moet de achterkant van de kaart scannen.")
        attempts = 1
        while attempts <= MAX_ATTEMPTS_ARUCO:
            card_scanned = yield aruco_scan_specific_card(self.session, practice_card)
            if card_scanned == practice_card:
                yield say_normally(self.session, "Goed gedaan! Dat was inderdaad de kaart die ik zocht.")
                return False
            elif card_scanned == -1:
                yield say_normally(self.session, "Helaas! Het was niet gelukt om de kaarten te scannen. Daarom"
                                           "zal ik nu alleen het nummer noemen en dan zoek jij de kaart op!")
                return True
            else:
                yield say_normally(self.session, "Oeps! Ik heb per ongeluk een andere kaart gescand. Let erop dat alle"
                                           "kaarten die je niet gebruikt met het plaatje naar boven liggen en probeer het"
                                           "dan opnieuw. De instructeur zal je helpen")
                attempts += 1

    @inlineCallbacks
    def try_speech_to_text(self) -> None:
        yield say_normally(self.session, "We gaan eerst oefenen met heen en weer praten. Je kan pas terugpraten als"
                           "ik klaar ben met praten. Je moet luid en duidelijk praten zodat ik je kan horen"
                           " Zeg nu bijvoorbeeld maar: Hij")
        correct = False
        attempts = 1
        while attempts <= MAX_ATTEMPTS_SPEECH:
            user_input = yield self.speech_recognition_session.recognize_speech()
            correct = self.game_helper.check_answer(user_input, 'hij')
            if correct:
                yield say_normally(self.session,"Goed gedaan! Het is gelukt")
                return
            else:
                yield say_normally(self.session, "Ik kon je nu niet goed verstaan. Probeer luid en duidelijk te praten."
                                                 " Dan kan ik het verstaan. Probeer opnieuw om hij te zeggen")
        return

    def practice_sentences(self, card) -> Dict:
        possible_indices_sentences = [1, 3, 5]
        picked_sentences = random.sample(possible_indices_sentences, 1)
        round_data = {
            "wrong_guesses": 0,
            "mistakes": [[]]
        }
        for i in picked_sentences:
            print("Picked sentence: " + str(i))
            selected_sentence = self.sentences.iloc[card, i]
            correct_answer = self.sentences.iloc[card, i + 1]
            print(selected_sentence)

            correct = False
            while not correct:
                # Check sentence
                yield say_practice_sentence(self.session, selected_sentence)
                user_input = yield self.speech_recognition_session.recognize_speech()
                correct = self.game_helper.check_answer(user_input, correct_answer)
                return round_data
                if correct:
                    yield respond_to_correct_answer(self.session, selected_sentence, correct_answer)
                else:
                    if round_data["wrong_guesses"] == 0:
                        yield respond_to_wrong_answer(self.session)
                        round_data["wrong_guesses"] += 1
                        round_data["mistakes"].append([selected_sentence, correct_answer, user_input])
                    else:
                        yield respond_to_wrong_answer_and_give_correct(self.session, selected_sentence, correct_answer)
                        round_data["wrong_guesses"] += 1
                        round_data["mistakes"].append([selected_sentence, correct_answer, user_input])
                        correct = True
        return round_data

    @inlineCallbacks
    def pronoun_practice(self):
        #Say hello

        #Practice text to speech
        #yield self.try_speech_to_text()

        #Practice aruco reading
        skip_aruco=False
        #skip_aruco = yield self.try_aruco_reading()

        #Practice with card reading
        # yield perform_movement(self.session, frames = arms_up, mode="linear", force=True)
        # yield say_normally(self.session,"Nu gaan we oefenen met de kaarten. Ik vertel je iets over het plaatje. Jij zegt het woord"
        #                    "dat op de lege plek hoort. Bij de lege plek doe ik mijn armen zo")
        # yield perform_movement(self.session, frames = arms_down, mode="linear", force=True)
        # yield say_normally(self.session, "naar beneden. Laten we het proberen met de kaart die je net hebt gepakt!")
        # _ = yield self.practice_sentences(card=0)

        # Regular loop
        round_data = yield self.practice_sentences(1)
        # yield say_normally(self.session, "We gaan nu oefenen met andere kaarten. Kies maar een kaart om te oefenen en"
        #                                  " scan hem voor mijn hoofd.")
        # for i in range (5):
        #     if skip_aruco:
        #         card = 0
        #     else:
        #         card = 0
        #         yield say_normally(self.session, "Ik scan nu naar kaarten")
        #         card = yield aruco_scan(self.session)
        #         while card is None:
        #             yield self.session.call("rie.dialogue.say", text="Probeer opnieuw", lang="nl")
        #             card = yield aruco_scan(self.session)
        #     # Practice sentences
        #     print("Picked card: " + str(card))
        #     yield say_normally(self.session, "Ik heb kaart" + str(card) + "gescand. Laten we daarmee gaan oefenen!")
        #     round_data = yield self.practice_sentences(card)





        return
