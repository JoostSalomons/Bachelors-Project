from autobahn.twisted.component import Component, run
from src.speech_processing.speech_to_text import SpeechToText
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
import pandas as pd
from src.pronoun_game.pronoun_game import PronounGame
SENTENCE_FILE = 'sentences.csv'
VERSION = 'experiment'
def read_sentences(file_location):
    sentences = pd.read_csv(file_location)
    return sentences

@inlineCallbacks
def main(session, details): #session, details as args

    yield session.call("rom.optional.behavior.play", name="BlocklySafeStand")
    yield session.call("rie.dialogue.config.language", lang="nl")
    yield session.call("rie.dialogue.say", text="hallo", lang="nl")
    sentences = read_sentences(SENTENCE_FILE)

    # #Practice stuff
    if VERSION == "experiment":
        yield session.call("rie.dialogue.say", "Hallo! Wat leuk dat je meedoet aan dit experiment. We gaan zometeen"
                                               "een aantal oefeningen doen. Laten we eerst proberen of alles werkt."
                                               "Als het niet lukt zal de onderzoeker je helpen.")
        game = PronounGame(session, VERSION, sentences)
        yield game.pronoun_practice()
    # #Pronoun Game

    yield print("Practice done")
    #yield session.call("rom.optional.behavior.play", name="BlocklyCrouch")
    yield session.leave()
# Create wamp connection
wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"]
    }],
    realm="rie.69297d8f82c3bec9b227217a",
)

wamp.on_join(main)

if __name__ == "__main__":
    #main()
    run([wamp])