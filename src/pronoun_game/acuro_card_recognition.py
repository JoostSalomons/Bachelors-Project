from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from src.robot_responses.responses import say_normally
from src.pronoun_game.llm_interface import LLMGameHelper
ARUCO_READING_TIME = 10 #amount of seconds to scan card
MAX_FAILED_ATTEMPS = 3
card_scanned = None

def on_card(frame):
# This function is called every time the robot sees a card
    global card_scanned
    card_scanned = frame['data']['body'][0][5]
    print("Kaart gescand: ", frame['data']['body'][0][5])

@inlineCallbacks
def aruco_scan(session):
    global card_scanned
    # Wait until we see a card
    print("Scanning for cards")
    aruco_found = False
    frame = session.call("rie.vision.card.read")
    #print(frame[0])
    yield session.subscribe(on_card, "rie.vision.card.stream")
    yield session.call("rie.vision.card.stream")
    yield sleep(ARUCO_READING_TIME)
    yield session.call("rie.vision.card.close")
    return card_scanned
    # Here we subscribe to the card data and start a stream

def aruco_scan_specific_card(session, card_to_scan):
    """'

    returns -1 if no card was found
    """
    global card_scanned
    say_normally(session, "Ik ben op zoek naar kaart" + str(card_to_scan))
    attempts = 0
    while card_scanned == None:
        card_scanned = aruco_scan(session)
        attempts += 1
        if attempts == MAX_FAILED_ATTEMPS:
            return -1
    return card_scanned
