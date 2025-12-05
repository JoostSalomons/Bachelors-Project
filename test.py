from autobahn.twisted.component import Component,run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug import perform_movement
from src.robot_movements.gesture_library import arms_up, arms_down, head_nod_with_arms
from src.robot_responses.responses import say_practice_sentence
@inlineCallbacks
def main(session, details):
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    yield perform_movement(session, head_nod_with_arms)
    #yield say_practice_sentence(session, "Hij _ iets")
    yield sleep(5)
    session.leave() # Close the connection with the robot

# Create wamp connection
wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"]
    }],
    realm="rie.692eba7aa7cba444073b5b64",
)
wamp.on_join(main)
if __name__ == "__main__":
    run([wamp])