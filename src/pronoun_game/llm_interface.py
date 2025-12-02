from src.utils import generate_message_using_llm
from nltk.tokenize import RegexpTokenizer
class LLMGameHelper:
    def __init__(self):
        self.standard_prompt_addition = ("Gebruik simpele en duidelijke taal die een"
                                         " 7 tot 10 jaar oud kind kan begrijpen.")

    def check_with_tokenize(self, word, input):
        if word in RegexpTokenizer(r"\b\w+(?:'\w+)?\b").tokenize(input.lower()):
            return True
        else:
            return False

    def check_answer(self, user_input, answer: str):
        #Cut the part after the pronoun describing its function
        correct_pronoun = answer.split('_')[0]
        print(correct_pronoun)
        print("The correct answer was " + str(correct_pronoun) + "The given answer was" + str(user_input))
        prompt = (
            f"De gebruiker heeft bij het raden van een persoonlijk voornaamwoord het volgende "
            f"antwoord gegeven: '{user_input}'. De volgende persoonlijke voornaamwoorden zijn correct:'{correct_pronoun}'. "
            "Geef als antwoord alleen 'juist', 'onjuist' of 'onzeker'."
        )
        correctness =  generate_message_using_llm(prompt)
        # print("Correctness is: " + correctness)
        # print(RegexpTokenizer(r"\b\w+(?:'\w+)?\b").tokenize(correctness.lower())[0])
        # if 'juist'in RegexpTokenizer(r"\b\w+(?:'\w+)?\b").tokenize(correctness.lower()):
        #     correct = True
        # else:
        #     correct = False
        correct = self.check_with_tokenize('juist', correctness)
        #Check sentence?
        return correct

    def recognize_yes_or_no(self, user_input: str) -> str:
        """
        Determines if the user's response is 'yes' or 'no'.

        Args:
            user_input (str): User's input.

        Returns:
            str: Either 'yes' or 'no' based on the input.
        """
        prompt = (
            f"De gebruiker heeft het volgende gezegd: {user_input}. Het is jouw taak om te bepalen of diegene"
            f"'ja' of 'nee' heeft gezegd. Reageer alleen met 'ja' of 'nee' gebaseerd op de input. Als het"
            f"onduidelijk is, reageer dan de meest waarschijnlijke optie. "
        )
        response = generate_message_using_llm(prompt)
        if self.check_with_tokenize(word='ja', input=response):
            return 'yes'
        elif self.check_with_tokenize(word='nee', input=response):
            return 'no'
        else:
            return 'unclear'


if __name__ == "__main__":
    GameHelper = LLMGameHelper()
    prompt = "ik denk van wel"
    yes_or_no = GameHelper.recognize_yes_or_no(prompt)
    print(yes_or_no)