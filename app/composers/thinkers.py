"""
TechincalComposer: Look for the techniques that were used in the paper, he appretiate how these techniques were used to answer specific question/hypothesis, and find how they can be applicable for users interests, he likes to quickly think computationally and say things like "oh, we'll need a module that does this, and another one that receives this, and use this or that tool..."

PhilosopherComposer: He takes a step up and look things from a bigger picture, he's a generalists and thinks what big questions this paper is tackling. He's also a critical thinker, and believes in science and progress when the right questions are made, he thinks we all will be benefited from clarity in our thinking and always forces us to clearly define the concepts we use and the pre-assumptions we made.

FirstPrinciplesComposer: He looks for generalizations. He read the paper and try to find general rules and expose them in a simple and reminiscent way.

HistoryOfScienceComposer: He's always reminding episodes of great scientists when they're are relevant for the current paper. Somehow is always relating some part of the paper with very inspiring anechdotes. 

MailComposer: He's a storyteller, he knows how to tell a story and make it engaging using one main principle: expectations. He knows how to generate expectations in the reader and then he satisfies them, but always let him wanting more.   
"""
from abc import ABC, abstractmethod
from app.llms import GeminiProvider
import os
from dotenv import load_dotenv

load_dotenv()

class Composer(ABC):
    @abstractmethod
    def compose(self, paper):
        pass

class TechnicalComposer(Composer):
    def compose(self, paper, user_interest, temperature=0.0):
        llm = GeminiProvider(model_name="gemini-1.5-pro-latest", api_key=os.getenv("API_KEY"), temperature=temperature)
        personality = """
        You look for the techniques that were used in a paper, you appretiate how these techniques were used to answer specific question/hypothesis, you find how they can be applicable for users interests, you like to quickly think computationally and say things like 'oh, we'll need a module that does this, and another one that receives this, and use this or that tool...'
        You're an engineer and you're very good at understanding how to implement things.
"""
        prompt = f"""This is your personality: '''{personality}'''

        These are the user's interests: '''{user_interest}'''

        And this is the paper: '''{paper}'''
        """

        response = llm.generate_query(prompt)
        return response



class PhilosopherComposer(Composer):
    def compose(self, paper, user_interest, temperature=1.0):
        llm = GeminiProvider(model_name="gemini-1.5-pro-latest", api_key=os.getenv("API_KEY"), temperature=temperature)
        personality = """
        You take a step up and look things from a bigger picture, you're a generalist and think what big questions this paper is tackling. You're also a critical thinker, and you believe in science and progress when the right questions are made, you think we all will be benefited from clarity in our thinking and you always force us to clearly define the concepts we use and the pre-assumptions we made.
"""
        prompt = f"""This is your personality: '''{personality}'''

        These are the user's interests: '''{user_interest}'''

        And this is the paper: '''{paper}'''
        """
        response = llm.generate_query(prompt)
        return response

class FirstPrinciplesComposer(Composer):
    def compose(self, paper, user_interest, temperature=0.0):
        llm = GeminiProvider(model_name="gemini-1.5-pro-latest", api_key=os.getenv("API_KEY"), temperature=temperature)
        personality = """
        You look for generalizations. You read the paper and try to find general rules and expose them in a simple and reminiscent way.
"""
        prompt = f"""This is your personality: '''{personality}'''

        These are the user's interests: '''{user_interest}'''

        And this is the paper: '''{paper}'''
        """
        response = llm.generate_query(prompt)
        return response

class HistoryOfScienceComposer(Composer):
    def compose(self, paper, user_interest, temperature=0.0):
        llm = GeminiProvider(model_name="gemini-1.5-pro-latest", api_key=os.getenv("API_KEY"), temperature=temperature)
        personality = """
        You're always reminding episodes of great scientists when they're are relevant for the current paper. Somehow is always relating some part of the paper with very inspiring anecdotes.
"""
        prompt = f"""This is your personality: '''{personality}'''

        These are the user's interests: '''{user_interest}'''

        And this is the paper: '''{paper}'''
        """
        response = llm.generate_query(prompt)
        return response

class MailComposer(Composer):
    def compose(self, paper, technical_analysis, philosopher_analysis, first_principles_analysis, history_of_science_analysis, 
                user_interest, temperature=2.0):
        llm = GeminiProvider(model_name="gemini-1.5-pro-latest", api_key=os.getenv("API_KEY"), temperature=temperature)
        personality = """
        You're a storyteller, you know how to tell a story and make it engaging using one main principle: expectations. You know how to generate expectations in the reader and then you satisfies them.
        Importantly, you're an erudite and a little bit arrogant, you are not agraid of getting into technical details although you know explain them in a simple way. You're serious.
"""
        prompt = f"""This is your personality: '''{personality}'''

        These are the user's interests: '''{user_interest}'''

        This paper may be relevant for the user's interests: '''{paper}'''

        And this is what you're different colleagues has written about the paper:

        Technical analysis: '''{technical_analysis}'''

        Philosopher analysis: '''{philosopher_analysis}'''

        First principles analysis: '''{first_principles_analysis}'''

        History of science analysis: '''{history_of_science_analysis}'''

        Now with that information you've gathered, you're ready orchestate a compelling mail that uses the central information of each one of the analyses (don't rewrite them too much, and keep the essence of each analysis). That is the technical analysis, the philosophical questions, the first principles generalizations and the history. You'll create expectations with simple words, and inspire the user to put hands on to build something amazing.
        """
        response = llm.generate_query(prompt)
        return response

class ComposerContext:
    def __init__(self, composer: Composer):
        self._composer = composer

    def set_composer(self, composer: Composer):
        self._composer = composer

    def compose_analysis(self, paper, user_interest):

        return self._composer.compose(paper, user_interest)


