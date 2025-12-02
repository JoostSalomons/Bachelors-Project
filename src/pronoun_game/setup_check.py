from autobahn.twisted.component import Component, run
from src.speech_processing.speech_to_text import SpeechToText
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from src.pronoun_game.acuro_card_recognition import aruco_scan_specific_card
def try_aruco_reading(session):
    practice_card = 0
    card_scanned = aruco_scan_specific_card(session, practice_card)
    if card_scanned !=
    return

def try_speech_to_text(session):
    return