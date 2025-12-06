import time
from typing import Generator, Optional, Dict
from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.util import sleep
from src.robot_movements.say_animated import say_animated
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
MAX_TIME_EXPERIMENT = 1 * 60
class PronounGame:
    def __init__(self, session, version, sentences, skip_intro):
        self.session = session
        self.version = version
        self.game_helper = LLMGameHelper()
        self.speech_recognition_session = SpeechRecognitionSession(self.session, self.version)
        self.sentences = sentences
        self.pronouns = ['hij', 'hem', 'zijn', 'zij', 'haar', 'hen', 'hun']
        self.pronoun_performance = [{"type": "3_sing_masc", "cards_tested": 0, "mistakes": 0, "correct": 0},
                                    {"type": "3_sing_fem", "cards_tested": 0, "mistakes": 0, "correct": 0},
                                    {"type": "3_plur", "cards_tested": 0, "mistakes": 0, "correct": 0}]
        self.skip_intro = skip_intro
        self.cards_already_done = []
        self.aruco_choice = True
        self.card_to_pick = None
        self.mistakes = [[]]

    @inlineCallbacks
    def try_aruco_reading(self, practice_card=0):
        if practice_card == 0:
            yield say_animated(self.session, "We gaan eerst oefenen met het scannen van de kaarten. Kan je de kaart scannen met"
                                   "een jongen en een computer? Mijn camera zit bij mijn hoofd. Hij heeft het nummer nul op de "
                                             "voorkant staan. "
                                   "Ik moet de achterkant van de kaart scannen. Leg na het scannen de kaart altijd terug"
                                             "met het plaatje of de tekst naar boven")
        attempts = 1
        while attempts <= MAX_ATTEMPTS_ARUCO:
            card_scanned = yield aruco_scan_specific_card(self.session, practice_card)
            if card_scanned == practice_card:
                yield say_animated(self.session, "Goed gedaan! Dat was inderdaad de kaart die ik zocht.")
                return
            elif card_scanned == -1:
                input = input("Did the child get it correct?: y/n")
                if input == "y":
                    yield say_animated(self.session, "Goed gedaan! Dat was inderdaad de kaart die ik zocht.")
                    return
                else:
                    yield say_animated(self.session, "Helaas! Het was niet gelukt om de kaarten te scannen. Daarom"
                                           "zal ik nu alleen het nummer noemen en dan zoek jij de kaart op!")
                    return
            else:
                yield say_animated(self.session, "Oeps! Ik heb per ongeluk een andere kaart gescand. Let erop dat alle"
                                           "kaarten die je niet gebruikt met het plaatje naar boven liggen en probeer het"
                                           "dan opnieuw. De instructeur zal je helpen")
                attempts += 1

    @inlineCallbacks
    def practice_sentences(self, card) -> Dict:
        possible_indices_sentences = [1, 3, 5]
        picked_sentences = random.sample(possible_indices_sentences, 3)
        round_data = {
            "wrong_guesses": 0,
            "correct_guesses": 0,
            "mistakes": [[]]
        }
        for i in picked_sentences:
            wrong_guesses_for_sentence = 0
            print("Picked sentence: " + str(i))
            selected_sentence = self.sentences.iloc[card, i]
            correct_answer = self.sentences.iloc[card, i + 1]
            print(selected_sentence)
            skip_sentence = False
            correct = False
            while not correct:
                # Check sentence
                if not skip_sentence:
                    yield say_practice_sentence(self.session, selected_sentence)
                card_scanned = yield aruco_scan(self.session)
                while card_scanned < 100:
                    yield say_normally(self.session, "Ik heb per ongeluk een plaatje gescand. Zorg dat alle plaatjes"
                                                     " omhoog liggen en probeer dan opnieuw")
                    yield sleep(1)
                    yield say_practice_sentence(self.session, selected_sentence)
                    card_scanned = yield aruco_scan(self.session)
                pronoun_guessed = self.pronouns[card_scanned-100]
                correct = self.game_helper.check_with_tokenize(pronoun_guessed, correct_answer)
                if correct:
                    yield respond_to_correct_answer(self.session, selected_sentence, correct_answer)
                    round_data["correct_guesses"] += 1
                else:
                    print("Gegeven antwoord is: " + str(pronoun_guessed) + "\nWat moet ik doen?: o(opnieuw)/g(goed)/f(fout)")
                    given_input = input()
                    if given_input == 'opnieuw':
                        skip_sentence=True
                    elif given_input == 'goed':
                        yield respond_to_correct_answer(self.session, selected_sentence, correct_answer)
                        round_data["correct_guesses"] += 1
                    else:
                        if wrong_guesses_for_sentence == 0:
                            yield respond_to_wrong_answer(self.session)
                            wrong_guesses_for_sentence += 1
                            round_data["wrong_guesses"] += 1
                            round_data["mistakes"].append([selected_sentence, correct_answer, pronoun_guessed])
                        else:
                            yield respond_to_wrong_answer_and_give_correct(self.session, selected_sentence, correct_answer)
                            round_data["wrong_guesses"] += 1
                            round_data["mistakes"].append([selected_sentence, correct_answer, pronoun_guessed])
                            correct = True
        return round_data
    @inlineCallbacks
    def child_picks_aruco(self):
        yield say_normally(self.session, "Kies maar een kaart om te oefenen en"
                                         " scan hem voor mijn hoofd.")
        card = yield aruco_scan(self.session)
        while card is None or card in self.cards_already_done or card >= 100:
            if card is None:
                yield self.session.call("rie.dialogue.say", text="Ik heb niks gevonden "
                                                                 "Probeer opnieuw", lang="nl")
            elif card in self.cards_already_done:
                yield say_normally(self.session, "Die kaart hebben we al geoefend. Probeer opnieuw")
            elif card >= 100:
                yield say_normally(self.session, "Ik heb per ongeluk een woordkaart gescand. Probeer opnieuw")
            card = yield aruco_scan(self.session)
        return card
    def update_pronoun_performance(self, card,round_data):
        self.pronoun_performance[card % 3]["cards_tested"] += 1
        self.pronoun_performance[card % 3]["mistakes"] += round_data["wrong_guesses"]
        self.pronoun_performance[card % 3]["correct"] += round_data["correct_guesses"]
        for mistake in round_data["mistakes"]:
            self.mistakes.append(mistake)

    @inlineCallbacks
    def pronoun_practice(self):

        #Practice aruco reading
        if not self.skip_intro:
            yield self.try_aruco_reading()
            #Practice with card reading
            yield perform_movement(self.session, frames = arms_up, mode="linear", force=True)
            yield say_normally(self.session,"Nu gaan we oefenen met de kaarten. Ik vertel je iets over het plaatje. In "
                                            "die zin is een lege plek. Bij de lege plek doe ik mijn armen zo")
            yield perform_movement(self.session, frames = arms_down, mode="linear", force=True)
            yield say_normally(self.session, "naar beneden. Daarna scan jij de kaart met het woord dat op de lege plek hoort"
                                             ". "
                                             " Laten we het proberen met de kaart die je net hebt gepakt! De zin is: ")
            practice_sentence = self.sentences.iloc[0, 1]
            print(practice_sentence)
            yield say_practice_sentence(self.session, practice_sentence)
            yield say_normally(self.session, "De kaart die ik zoek is: hij")
            _ = yield self.try_aruco_reading(practice_card=100)

        # Regular loop
        #round_data = yield self.practice_sentences(1)
        yield say_normally(self.session, "We gaan nu oefenen met de andere kaarten")
        start_time = time.time()
        while time.time() - start_time <= MAX_TIME_EXPERIMENT:
            if self.aruco_choice:
                card = yield self.child_picks_aruco()
            # Practice sentences
            print("Picked card: " + str(card))
            yield say_normally(self.session, "Ik heb kaart" + str(card) + "gescand. Laten we daarmee gaan oefenen!")
            yield sleep(1)
            self.cards_already_done.append(card)
            round_data = yield self.practice_sentences(card)
            self.update_pronoun_performance(card,round_data)

        return self.pronoun_performance, self.mistakes
