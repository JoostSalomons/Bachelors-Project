import time
from typing import Generator, Optional, Dict
from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.util import sleep
# from src.robot_movements.say_animated import say_animated
from src.utils import generate_message_using_llm, generate_conversation_using_llm
from alpha_mini_rug import perform_movement
from src.speech_processing.speech_session import SpeechRecognitionSession
from src.pronoun_game.llm_interface import LLMGameHelper
from src.pronoun_game.acuro_card_recognition import aruco_scan,aruco_scan_specific_card
from src.robot_responses.responses import say_practice_sentence, respond_to_correct_answer,\
    respond_to_wrong_answer, respond_to_wrong_answer_and_give_correct, say_normally
from src.robot_movements.gesture_library import arms_up, arms_down
from src.robot_movements.say_animated import say_animated
import openai
import os
import random

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please set it in your environment variables.")

client = openai.Client(api_key=API_KEY)


class ControlExperiment:
    def __init__(self, session, version, skip_intro):
        self.session = session
        self.version = version
        self.game_helper = LLMGameHelper()
        self.speech_recognition_session = SpeechRecognitionSession(self.session, self.version)
        self.conversation = openai.conversations.create()
        self.skip_intro = skip_intro


    @inlineCallbacks
    def control_experiment(self):
        conversation = [[]]
        time_limit_seconds = 1 * 60
        prompts = [
            "Het kind heeft niet gereageerd op de vraag. Zeg dat je het niet goed hebt gehoord. Herhaal daarna de vraag "
            "of stel een nieuwe vraag."
        ]
        yield say_animated(self.session, "Hallo, ik ben de Alpha Mini robot. We gaan nu een gesprek houden. Als ik"
                                         " klaar ben met praten moet je even wachten en dan kan je reageren.")
        starting_prompt = yield generate_conversation_using_llm(f"Zeg het volgende om het gesprek te beginnen: "
                                                          f"Ik ben een robot. Wat weet jij over robots?",
                                                          self.conversation.id)
        #yield say_animated(self.session, "Hallo. Ik ben de Alpha mini Robot")
        conversation.append(['', starting_prompt]) #[child_contribution, robot_contribution]
        yield say_animated(self.session, starting_prompt)
        time_limit_responses = 1
        start_time = time.time()
        while time.time() - start_time <= time_limit_seconds:
            wait_for_response_time = time.time()
            while (time.time() - wait_for_response_time <= time_limit_responses) and\
                    (time.time() - start_time <= time_limit_seconds):
                user_input = yield self.speech_recognition_session.recognize_speech()
                print(1)
                if user_input is not None:
                    print(2)
                    yield say_animated(self.session, "Bedankt voor jouw antwoord")
                    print(3)
                    prompt = yield generate_conversation_using_llm(user_input,self.conversation.id)
                    conversation.append([user_input, prompt])
                    yield say_animated(self.session, prompt)
                    wait_for_response_time = time.time()
            if time.time() - start_time <= time_limit_seconds:
                print("too long response")
                conversation_continuation = random.choice(prompts)
                new_message = yield generate_conversation_using_llm(conversation_continuation, self.conversation.id)
                conversation.append(['', new_message])
                print(conversation)
                yield say_animated(self.session, new_message)
                print("Blub")
        return conversation