from enum import Enum


class ItemCondition(Enum):
    unknown = 'item.item_condition.unknown'
    good = 'item.item_condition.good'
    ok = 'item.item_condition.ok'
    mostly_ok = 'item.item_condition.mostly_ok'
    damaged = 'item.item_condition.damaged'
    in_repair = 'item.item_condition.in_repair'
    unhygienic = 'item.item_condition.unhygienic'
    other = 'item.item_condition.other'
