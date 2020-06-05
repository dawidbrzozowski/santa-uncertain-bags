from argparse import ArgumentParser

from solvers.search_best_weights import WeightSearch
from utils.evaluation import ScoreEvaluator
from utils.files_io import load_json, KagglePreparer, write_json_file

GIFT_AMOUNTS = 'data/gift_amounts.json'
DEFAULT_GIFT_WEIGHTS = 'data/def_gift_weights.json'
DEFAULT_TEMP_WEIGHTS = 'data/temp_weights.json'

MIN_GIFT_IN_BAG = 3
FIND_WEIGHTS_N_ITER = 500
DEFAULT_BAGS_AMOUNT = 1000
EVAL_SCORE_ITERATIONS = 200
DEFAULT_STD_MUL = 0
DEFAULT_STEP_MUL = 0.6
DEFAULT_MAX_BAG_WEIGHT = 46


class BagPacker:
    def __init__(self, gift_amounts, gift_weight_avgs, gift_weight_stds):
        self.gift_amounts = gift_amounts
        self.gift_weight_avgs = gift_weight_avgs
        self.gift_weight_stds = gift_weight_stds
        self.curr_bag_weight = 0
        self.max_bag_weight = None

    def pack_bags(self, max_bag_weight, bags_amount=DEFAULT_BAGS_AMOUNT, std_mul=0):
        bags = []
        self.max_bag_weight = max_bag_weight
        for _ in range(bags_amount):
            try:
                bags.append(self._pack_bag(std_mul))
            except IndexError:
                break
        return bags

    def _pack_bag(self, std_mul):
        self.curr_bag_weight = 0
        all_allowed_gifts = self._get_allowed_gifts_descending_weight(std_mul)
        bag = self._try_packing_bag(std_mul, init_bag=[], allowed_gifts=all_allowed_gifts)
        while len(bag) < MIN_GIFT_IN_BAG:
            bag = self._repack(bag, std_mul)
        return bag

    def _try_packing_bag(self, std_mul, init_bag, allowed_gifts):
        bag = init_bag
        for gift_type in allowed_gifts:
            while self._is_place_in_bag_for_gift_type(gift_type, std_mul) and self.gift_amounts[gift_type] > 0:
                self.curr_bag_weight += self.gift_weight_avgs[gift_type] + self.gift_weight_stds[gift_type] * std_mul
                bag.append(gift_type)
                self.gift_amounts[gift_type] -= 1
        return bag

    def _repack(self, bag, std_mul):
        gift_unpacked = self._pop_gift(bag, std_mul)
        allowed_gifts = self._prepare_next_allowed_gifts(gift_unpacked, std_mul)
        return self._try_packing_bag(std_mul, bag, allowed_gifts)

    def _pop_gift(self, bag, std_mul):
        gift_unpacked = bag.pop(-1)
        self.curr_bag_weight -= self.gift_weight_avgs[gift_unpacked] + self.gift_weight_stds[gift_unpacked] * std_mul
        self.gift_amounts[gift_unpacked] += 1
        return gift_unpacked

    def _get_allowed_gifts_descending_weight(self, std_mul):
        gift_weight_avg_std = dict(self.gift_weight_avgs)
        for key in gift_weight_avg_std:
            gift_weight_avg_std[key] += std_mul * self.gift_weight_stds[key]
        return sorted([gift_type for gift_type in gift_weight_avg_std if self.gift_amounts[gift_type] >= 0],
                      key=gift_weight_avg_std.get, reverse=True)

    def _prepare_next_allowed_gifts(self, gift_type, std_mul):
        available_gifts_descending = self._get_allowed_gifts_descending_weight(std_mul)
        if not gift_type == available_gifts_descending[-1]:
            gift_type_idx = available_gifts_descending.index(gift_type)
            return available_gifts_descending[gift_type_idx + 1:]
        else:
            return []

    def _is_place_in_bag_for_gift_type(self, gift_type, std_mul):
        return True if self.curr_bag_weight + self.gift_weight_avgs[gift_type] + std_mul * self.gift_weight_stds[
            gift_type] < self.max_bag_weight else False


def find_best_weights(bag_capacity, std_mul, step_mul):
    gift_amounts = load_json(GIFT_AMOUNTS)
    gift_stds = load_json(DEFAULT_GIFT_WEIGHTS)['std']
    weight_search = WeightSearch()
    score_eval = ScoreEvaluator()
    best_score = 0
    amount_of_iteration = FIND_WEIGHTS_N_ITER
    for i in range(amount_of_iteration):
        if not i == 0:
            weight_search.take_random_step(((amount_of_iteration - i) / amount_of_iteration) * step_mul)
        bp = BagPacker(dict(gift_amounts), weight_search.weights, gift_stds)
        bags = bp.pack_bags(max_bag_weight=bag_capacity, std_mul=std_mul)
        score = score_eval.calculate_score(bags)
        if score > best_score:
            best_score = score
        else:
            weight_search.step_back()
        print(f'Iteration: {i}, Score:{best_score}')
    print(weight_search.weights)
    write_json_file(DEFAULT_TEMP_WEIGHTS, weight_search.weights)
    bp = BagPacker(dict(gift_amounts), weight_search.weights, gift_stds)
    bags = bp.pack_bags(max_bag_weight=bag_capacity, std_mul=std_mul)
    score = score_eval.calculate_score(bags, 150)
    print(score)


def main(args):
    if args.find_weights:
        find_best_weights(args.max_bag_weight, args.std_mul, args.step_mul)
    else:
        gift_amounts = load_json(GIFT_AMOUNTS)
        gift_weights = load_json(DEFAULT_GIFT_WEIGHTS)
        gift_weight_avgs = gift_weights['avg']
        gift_weight_stds = gift_weights['std']
        p = BagPacker(gift_amounts, gift_weight_avgs, gift_weight_stds)
        bags = p.pack_bags(max_bag_weight=args.max_bag_weight, std_mul=args.std_mul)
        score_eval = ScoreEvaluator()
        print(f'Score: {score_eval.calculate_score(bags, EVAL_SCORE_ITERATIONS)}')

        if args.save_path:
            kaggle_preparer = KagglePreparer()
            kaggle_preparer.save(args.save_path, bags)


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--max_bag_weight', type=int, required=False, default=DEFAULT_MAX_BAG_WEIGHT,
                           help='Max bag weight, that will be used during packing bags algorithm.')
    argparser.add_argument('--std_mul', type=float, required=False, default=DEFAULT_STD_MUL,
                           help='How much impact should standard deviation have on packing bag')
    argparser.add_argument('--step_mul', type=float, required=False, default=DEFAULT_STEP_MUL,
                           help='Step mul for finding weights')
    argparser.add_argument('--save_path', type=str, required=False,
                           help='If you want to save output for Kaggle evaluation, provide path for save.')
    argparser.add_argument('--find_weights', action='store_true', help='Find weights or eval')
    arguments = argparser.parse_args()
    main(arguments)
