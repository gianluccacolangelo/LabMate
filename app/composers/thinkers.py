"""
TechnicalComposer: Look for the techniques that were used in the paper...
PhilosopherComposer: He takes a step up and look things from a bigger picture...
FirstPrinciplesComposer: He looks for generalizations...
HistoryOfScienceComposer: He's always reminding episodes of great scientists...
MailComposer: He's a storyteller...
"""
from abc import ABC, abstractmethod
from app.composers.llms import LLMFactory
import os
from dotenv import load_dotenv

load_dotenv()

class Composer(ABC):
    def __init__(self, llm_provider: str, **llm_kwargs):
        self.llm = LLMFactory.create_provider(llm_provider, os.getenv("API_KEY"), **llm_kwargs)

    @abstractmethod
    def compose(self, paper, user_interest):
        pass

class TechnicalComposer(Composer):
    def __init__(self, llm_provider: str = "gemini", **llm_kwargs):
        super().__init__(llm_provider, **llm_kwargs)

    def compose(self, paper, user_interest):
        personality = """
        You look for the techniques that were used in a paper...
        """
        prompt = f"""This is your personality: '''{personality}'''

        These are the user's interests: '''{user_interest}'''

        And this is the paper: '''{paper}'''
        """
        return self.llm.generate_query(prompt)

class PhilosopherComposer(Composer):
    def __init__(self, llm_provider: str = "gemini", **llm_kwargs):
        super().__init__(llm_provider, **llm_kwargs)

    def compose(self, paper, user_interest):
        personality = """
        You take a step up and look things from a bigger picture...
        """
        prompt = f"""This is your personality: '''{personality}'''

        These are the user's interests: '''{user_interest}'''

        And this is the paper: '''{paper}'''
        """
        return self.llm.generate_query(prompt)

class FirstPrinciplesComposer(Composer):
    def __init__(self, llm_provider: str = "gemini", **llm_kwargs):
        super().__init__(llm_provider, **llm_kwargs)

    def compose(self, paper, user_interest):
        personality = """
        You look for generalizations...
        """
        prompt = f"""This is your personality: '''{personality}'''

        These are the user's interests: '''{user_interest}'''

        And this is the paper: '''{paper}'''
        """
        return self.llm.generate_query(prompt)

class HistoryOfScienceComposer(Composer):
    def __init__(self, llm_provider: str = "gemini", **llm_kwargs):
        super().__init__(llm_provider, **llm_kwargs)

    def compose(self, paper, user_interest):
        personality = """
        You're always reminding episodes of great scientists...
        """
        prompt = f"""This is your personality: '''{personality}'''

        These are the user's interests: '''{user_interest}'''

        And this is the paper: '''{paper}'''
        """
        return self.llm.generate_query(prompt)

class MailComposer(Composer):
    def __init__(self, llm_provider: str = "gemini", **llm_kwargs):
        super().__init__(llm_provider, **llm_kwargs)

    def compose(self, paper, technical_analysis, philosopher_analysis, first_principles_analysis, history_of_science_analysis, 
                user_interest):
        personality = """
        You're a storyteller, you know how to tell a story...
        """
        prompt = f"""This is your personality: '''{personality}'''

        These are the user's interests: '''{user_interest}'''

        This paper may be relevant for the user's interests: '''{paper}'''

        And this is what you're different colleagues has written about the paper:

        Technical analysis: '''{technical_analysis}'''

        Philosopher analysis: '''{philosopher_analysis}'''

        First principles analysis: '''{first_principles_analysis}'''

        History of science analysis: '''{history_of_science_analysis}'''

        Now with that information you've gathered, you're ready orchestate a compelling mail...
        """
        return self.llm.generate_query(prompt)

class ComposerContext:
    def __init__(self, composer: Composer):
        self._composer = composer

    def set_composer(self, composer: Composer):
        self._composer = composer

    def compose_analysis(self, paper, user_interest):
        return self._composer.compose(paper, user_interest)
