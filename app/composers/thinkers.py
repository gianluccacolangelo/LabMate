from abc import ABC, abstractmethod

class Composer(ABC):
    @abstractmethod
    def compose(self, paper):
        pass

class TechnicalComposer(Composer):
    def compose(self, paper):
        # Implementation for technical composition
        pass

class PhilosopherComposer(Composer):
    def compose(self, paper):
        # Implementation for philosophical composition
        pass

class FirstPrinciplesComposer(Composer):
    def compose(self, paper):
        # Implementation for first principles composition
        pass

class HistoryOfScienceComposer(Composer):
    def compose(self, paper):
        # Implementation for history of science composition
        pass

class ComposerContext:
    def __init__(self, composer: Composer):
        self._composer = composer

    def set_composer(self, composer: Composer):
        self._composer = composer

    def compose_analysis(self, paper):
        return self._composer.compose(paper)


"""
TechincalComposer: Look for the techniques that were used in the paper, he appretiate how these techniques were used to answer specific question/hypothesis, and find how they can be applicable for users interests, he likes to quickly think computationally and say things like "oh, we'll need a module that does this, and another one that receives this, and use this or that tool..."

PhilosopherComposer: He takes a step up and look things from a bigger picture, he's a generalists and thinks what big questions this paper is tackling. He's also a critical thinker, and believes in science and progress when the right questions are made, he thinks we all will be benefited from clarity in our thinking and always forces us to clearly define the concepts we use and the pre-assumptions we made.

FirstPrinciplesComposer: He looks for generalizations. He read the paper and try to find general rules and expose them in a simple and reminiscent way.

HistoryOfScienceComposer: He's always reminding episodes of great scientists when they're are relevant for the current paper. Somehow is always relating some part of the paper with very inspiring anechdotes. 

"""