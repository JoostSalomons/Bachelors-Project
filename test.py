from autobahn.twisted.component import Component,run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug import perform_movement
@inlineCallbacks
def main(session, details):
    frames = [

        {

            "time": 800,

            "data": {

                "body.arms.right.upper.pitch": -1.7,

                "body.arms.left.upper.pitch": -1.7,

            },

        },

        {

            "time": 1600,

            "data": {

                "body.arms.right.upper.pitch": 0.5,

                "body.arms.left.upper.pitch": 0.5,

            },

        },
    ]
    session.call("rie.dialogue.say", text="Hallo ouders! Ik ben de Alpha Mini Robot voor het onderzoek. Aangenaam kennis te maken!", lang="nl")
    yield session.call("rom.optional.behavior.play", name="BlocklyCrouch")
    yield perform_movement(session, frames = frames, force=True)
    #yield session.call("rom.optional.behavior.play", name="BlocklyHappy")
    session.leave() # Close the connection with the robot

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
    run([wamp])