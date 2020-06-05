import random

from utils.files_io import load_json

random.seed(12)

DEFAULT_GIFT_WEIGHTS = 'data/def_gift_weights.json'


class WeightSearch:
    def __init__(self):
        self.weights = load_json(DEFAULT_GIFT_WEIGHTS)['avg']
        self.prev_weights = self.weights.copy()

    def take_random_step(self, step):
        self.prev_weights = self.weights.copy()
        for gift_type in self.weights:
            self._generate_new_weight_for(gift_type, step)

    def step_back(self):
        self.weights = self.prev_weights.copy()

    def _generate_new_weight_for(self, gift_type, step):
        random_move = (random.random() * 2 - 1) * self.weights[gift_type] * step
        self.weights[gift_type] = self.weights[gift_type] + random_move
