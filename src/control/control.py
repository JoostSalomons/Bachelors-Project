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
import openai
import os
import random

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please set it in your environment variables.")

client = openai.Client(api_key=API_KEY)


class ControlExperiment:
    def __init__(self, session, version):
        self.session = session
        self.version = version
        self.game_helper = LLMGameHelper()
        self.speech_recognition_session = SpeechRecognitionSession(self.session, self.version)
        self.conversation = openai.conversations.create()



    def control_experiment(self):
        start_time = time.time()
        time_limit_seconds = 3 * 60
        prompts = [
            "Stel een vraag die verder gaat met het gesprek"
            "Stel een nieuwe vraag aan een kind van 7-10 jaar"
        ]
        yield say_normally(self.session, f"Hallo! Ik ben de Alpha Mini robot")
        yield say_normally(self.session, f"Ik ben een robot. Wat weet jij over robots?")
        time_limit_responses = 10
        while time.time() - start_time <= time_limit_seconds:
            wait_for_response_time = time.time()
            while time.time() - wait_for_response_time <= time_limit_responses:
                user_input = yield self.speech_recognition_session.recognize_speech()
                if user_input is not None:
                    prompt = yield generate_conversation_using_llm(user_input,self.conversation)
                    yield say_normally(self.session, prompt)
                    wait_for_response_time = time.time()
            print("too long response")
            conversation_continuation = random.choice(prompts)

            yield say_normally(self.session, conversation_continuation)