from __future__ import annotations

import math
import numpy as np
from typing import List
from assessment.outcome import Outcome


class Assessment:
    def __init__(
        self,
        uncertainty=0.,
        illegal=0.,
        lose=0.,
        draw=0.,
        win=0.,
        probabilities: List[float] = None,
        inverse: Assessment = None
    ):
        if inverse:
            self._inverse = inverse
            inverse._inverse = self

            self.uncertainty = inverse.uncertainty

            self.illegal = inverse.illegal
            self.lose = inverse.win
            self.draw = inverse.draw
            self.win = inverse.lose

            self.probabilities = np.array([self.illegal, self.lose, self.draw, self.win])

        else:
            self.uncertainty = uncertainty

            if probabilities:
                self.probabilities = np.copy(probabilities)
                self.draw = probabilities[Outcome.DRAW]
                self.illegal = probabilities[Outcome.ILLEGAL]
                self.lose = probabilities[Outcome.LOSE]
                self.win = probabilities[Outcome.WIN]
            else:
                self.draw = draw
                self.illegal = illegal
                self.lose = lose
                self.win = win

                self.probabilities = np.zeros(4)
                self.probabilities[Outcome.DRAW] = draw
                self.probabilities[Outcome.ILLEGAL] = illegal
                self.probabilities[Outcome.LOSE] = lose
                self.probabilities[Outcome.WIN] = win

            self._inverse = None

        # I had to think a long time about how I wanted this comparison to work.  The ideal state for this class is to
        # have a one-hot encoding for a particular outcome.  Most of this class's instances are going to be generated
        # by a neural network's softmaxed output.  Near the beginning of the training, I can expect most of these scores
        # to be close.  Even at the end, these values will never reach a one-hot encoding.  This means that I need to
        # account for the predicted probabilities during the comparisons.
        #
        # I decided that a hierarchical comparison made good sense.  We can divide the predictions into two basic
        # classes: acceptable outcomes (win and draw) and unacceptable outcomes (lose and illegal, though truly illegal
        # outcomes will be masked during selection).  Every move that has a higher acceptable sum is better then every
        # move that has a lower acceptable sum.  If two assessments have nearly equivalent acceptable outcome sums, then
        # the one that has the higher win probability is better.  If there is still a tie, then the one that has the
        # higher lose probability is better (because playing an illegal move is even worse than losing for training
        # purposes).
        self.acceptable = self.win + self.draw
        self.unacceptable = self.illegal + self.lose

    def __eq__(self, other):
        return (
            isinstance(other, Assessment) and
            Assessment._compare(self.uncertainty, other.uncertainty) and
            all(map(Assessment._compare, self.probabilities))
        )

    def __ne__(self, other):
        return not (self == other)

    @staticmethod
    def _compare(lhs, rhs):
        return math.isclose(lhs, rhs, rel_tol=0.005, abs_tol=0.0005)

    def __ge__(self, other: Assessment):
        return not (self < other)

    def __gt__(self, other: Assessment):
        if Assessment._compare(self.acceptable, other.acceptable):
            if Assessment._compare(self.win, other.win):
                if Assessment._compare(self.lose, other.lose):
                    result = False
                else:
                    result = self.lose > other.lose
            else:
                result = self.win > other.win
        else:
            result = self.acceptable > other.acceptable
        return result

    def __le__(self, other: Assessment):
        return not (self > other)

    def __lt__(self, other: Assessment):
        # See __gt__() for an explanation behind this hierarchical reasoning.
        if Assessment._compare(self.unacceptable, other.unacceptable):
            if Assessment._compare(self.illegal, other.illegal):
                if Assessment._compare(self.draw, other.draw):
                    result = False
                else:
                    result = self.draw > other.draw
            else:
                result = self.illegal > other.illegal
        else:
            result = self.unacceptable > other.unacceptable
        return result

    def as_certain_as(self, other: Assessment):
        return Assessment._compare(self.uncertainty, other.uncertainty)

    def at_least_as_certain_as(self, other: Assessment):
        return not self.less_certain_than(other)

    def less_certain_than(self, other: Assessment):
        return not self.as_certain_as(other) and self.uncertainty > other.uncertainty

    def more_certain_than(self, other: Assessment):
        return not self.as_certain_as(other) and self.uncertainty < other.uncertainty

    def no_more_certain_than(self, other: Assessment):
        return not self.more_certain_than(other)

    @property
    def inverse(self):
        if not self._inverse:
            self._inverse = Assessment(inverse=self)
        return self._inverse


Illegal = Assessment(uncertainty=0., illegal=1.)
_ = Illegal.inverse

Draw = Assessment(uncertainty=0., draw=1.)
_ = Draw.inverse

Lose = Assessment(uncertainty=0., lose=1.)
Win = Lose.inverse
