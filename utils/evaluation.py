import numpy as np

BAG_CAPACITY = 50
DEFAULT_ITERATIONS = 50


class ScoreEvaluator:
    def __init__(self, bag_capacity=BAG_CAPACITY):
        self.bag_capacity = bag_capacity
        self.gift_weights = None

    def calculate_score(self, bags, iterations=DEFAULT_ITERATIONS):
        score = 0
        for _ in range(iterations):
            self.gift_weights = self._generate_random_weights()
            score += self._calculate_single_score(bags)
        return score / iterations

    def _calculate_single_score(self, bags):
        score = 0
        for bag in bags:
            score += self._calculate_score_for_bag(bag)
        return score

    def _calculate_score_for_bag(self, bag):
        score = 0
        for gift in bag:
            score += self.gift_weights[gift]
        return score if score <= self.bag_capacity else 0

    def _generate_random_weights(self):
        weights = {
            'horse': max(0, np.random.normal(5, 2, 1)[0]),
            'ball': max(0, 1 + np.random.normal(1, 0.3, 1)[0]),
            'bike': max(0, np.random.normal(20, 10, 1)[0]),
            'train': max(0, np.random.normal(10, 5, 1)[0]),
            'coal': 47 * np.random.beta(0.5, 0.5, 1)[0],
            'book': np.random.chisquare(2, 1)[0],
            'doll': np.random.gamma(5, 1, 1)[0],
            'blocks': np.random.triangular(5, 10, 20, 1)[0],
            'gloves': 3.0 + np.random.rand(1)[0] if np.random.rand(1) < 0.3 else np.random.rand(1)[0],
        }
        return weights
