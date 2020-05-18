from collections import defaultdict
import csv
import json


def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)


class KagglePreparer:
    def save(self, file_name, bags):
        bags_with_ids = self._add_ids_to_gifts(bags)
        with open(file_name, "w", newline="") as f:
            f.write('Gifts\n')
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(bags_with_ids)

    def _add_ids_to_gifts(self, bags):
        id_controller = IdController()
        bags_with_ids = []
        for bag in bags:
            bag_with_ids = []
            for gift in bag:
                gift_with_id = id_controller.convert_gift_to_kaggle_format(gift)
                bag_with_ids.append(gift_with_id)
            bags_with_ids.append(bag_with_ids)
        return bags_with_ids


class IdController:
    def __init__(self):
        self.ids = defaultdict(int)

    def convert_gift_to_kaggle_format(self, gift: str):
        gift_with_index = f'{gift}_{self.ids[gift]}'
        self.ids[gift_with_index] += 1
        return gift_with_index
