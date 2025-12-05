from autobahn.twisted.component import Component, run
from src.speech_processing.speech_to_text import SpeechToText
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
import pandas as pd
from src.pronoun_game.pronoun_game import PronounGame
from src.robot_movements.gesture_library import arms_up
from alpha_mini_rug import perform_movement
from src.control.control import ControlExperiment
SENTENCE_FILE = 'sentences.csv'
VERSION = 'control'
def read_sentences(file_location):
    sentences = pd.read_csv(file_location)
    return sentences

@inlineCallbacks
def main(session, details): #session, details as args
    yield session.call("rom.optional.behavior.play", name="BlocklyCrouch")
    yield session.call("rom.actuator.motor.write",
                     frames=[{"time": 400, "data": {"body.head.pitch": 0.1}},
                             {"time": 1200, "data": {"body.head.pitch": -0.1}},
                             {"time": 2000, "data": {"body.head.pitch": 0.1}},
                             {"time": 2400, "data": {"body.head.pitch": 0.0}}],
                     force=True)
    yield session.call("rom.actuator.motor.write",
                     frames=[{"time": 400, "data": {"body.head.pitch": 0.1}},
                             {"time": 1200, "data": {"body.head.pitch": -0.1}},
                             {"time": 2000, "data": {"body.head.pitch": 0.1}},
                             {"time": 2400, "data": {"body.head.pitch": 0.0}}],
                     force=True)
    yield s
    yield perform_movement(session, frames=arms_up)
    #yield session.call("rom.optional.behavior.play", name="BlocklyRobotDance")
    yield session.call("rie.dialogue.config.language", lang="nl")
    yield session.call("rie.dialogue.config.native_voice", use_native_voice = True)
    yield session.call("rie.dialogue.say", text="Robot gestart", lang="nl")
    sentences = read_sentences(SENTENCE_FILE)

    # #Practice stuff
    if VERSION == "experiment":
        yield session.call("rie.dialogue.say", "Hallo! Wat leuk dat je meedoet aan dit experiment. We gaan zometeen"
                                               "een aantal oefeningen doen. Laten we eerst proberen of alles werkt. "
                                               "Als het niet lukt zal de onderzoeker je helpen.")
        game = PronounGame(session, VERSION, sentences)
        yield game.pronoun_practice()
    # #Pronoun Game

    if VERSION == "control":
        control = ControlExperiment(session, VERSION)
        yield control.control_experiment()
    yield print("Practice done")
    #yield session.call("rom.optional.behavior.play", name="BlocklyCrouch")
    yield session.leave()
# Create wamp connection
wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"]
    }],
    realm="rie.6932b673a7cba444073b7174",
)

wamp.on_join(main)

if __name__ == "__main__":
    #main()
    run([wamp])