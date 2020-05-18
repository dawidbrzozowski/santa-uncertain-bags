from argparse import ArgumentParser

from utils.evaluation import ScoreEvaluator
from utils.files_io import load_json, KagglePreparer

DEFAULT_BAGS_AMOUNT = 1000
MIN_GIFT_IN_BAG = 3

GIFT_AMOUNTS = 'data/gift_amounts.json'
DEFAULT_GIFT_WEIGHTS = 'data/def_gift_weights.json'


class BagPacker:
    def __init__(self, gift_amounts, gift_weights):
        self.gift_amounts = gift_amounts
        self.gift_weights = gift_weights
        self.curr_bag_weight = 0
        self.max_bag_weight = None

    def pack_bags(self, max_bag_weight, bags_amount=DEFAULT_BAGS_AMOUNT):
        bags = []
        self.max_bag_weight = max_bag_weight
        for _ in range(bags_amount):
            try:
                bags.append(self._pack_bag())
            except IndexError:
                break
        return bags

    def _pack_bag(self):
        self.curr_bag_weight = 0
        allowed_gifts = self._get_allowed_gifts_descending_weight()
        bag = self._try_packing_bag(init_bag=[], allowed_gifts=allowed_gifts)
        while len(bag) < MIN_GIFT_IN_BAG:
            bag = self._repack(bag, allowed_gifts)
        return bag

    def _try_packing_bag(self, init_bag, allowed_gifts):
        bag = init_bag
        for gift_type in allowed_gifts:
            while self._is_place_in_bag_for_gift_type(gift_type) and self.gift_amounts[gift_type] > 0:
                self.curr_bag_weight += self.gift_weights[gift_type]
                bag.append(gift_type)
                self.gift_amounts[gift_type] -= 1
        return bag

    def _repack(self, bag, allowed_gifts):
        allowed_gifts = self._unpack(bag, allowed_gifts)
        return self._try_packing_bag(bag, allowed_gifts)

    def _unpack(self, bag, allowed_gifts):
        unpacked_gift = self._pop_gift(bag)
        allowed_gifts.remove(unpacked_gift)
        if not len(allowed_gifts):
            gift_unpacked = self._pop_gift(bag)
            allowed_gifts = self._prepare_next_allowed_gifts(gift_unpacked)
        return allowed_gifts

    def _pop_gift(self, bag):
        gift_unpacked = bag.pop(-1)
        self.curr_bag_weight -= self.gift_weights[gift_unpacked]
        self.gift_amounts[gift_unpacked] += 1
        return gift_unpacked

    def _get_allowed_gifts_descending_weight(self):
        return sorted([gift_type for gift_type in self.gift_weights if self.gift_amounts[gift_type] >= 0],
                      key=self.gift_weights.get, reverse=True)

    def _prepare_next_allowed_gifts(self, gift_type):
        available_gifts_descending = self._get_allowed_gifts_descending_weight()
        if not gift_type == available_gifts_descending[-1]:
            gift_type_idx = available_gifts_descending.index(gift_type)
            return available_gifts_descending[gift_type_idx + 1:-1]
        else:
            return []

    def _is_place_in_bag_for_gift_type(self, gift_type):
        return True if self.curr_bag_weight + self.gift_weights[gift_type] < self.max_bag_weight else False


def main(args):
    gift_amounts = load_json(GIFT_AMOUNTS)
    # temporarily we are using static weights based on mean weights.
    gift_weights = load_json(DEFAULT_GIFT_WEIGHTS)
    p = BagPacker(gift_amounts, gift_weights)
    bags = p.pack_bags(args.max_bag_weight)
    score_eval = ScoreEvaluator()
    print(f'Score: {score_eval.calculate_score(bags)}')

    if args.save_path:
        kaggle_preparer = KagglePreparer()
        kaggle_preparer.save(args.save_path, bags)


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--max_bag_weight', type=int, required=False, default=40,
                           help='Max bag weight, that will be used during packing bags algorithm.')
    argparser.add_argument('--save_path', type=str, required=False,
                           help='If you want to save output for Kaggle evaluation, provide path for save.')
    arguments = argparser.parse_args()
    main(arguments)
