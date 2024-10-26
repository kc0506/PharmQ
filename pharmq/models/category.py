from typing import NamedTuple

import pandas as pd

# class Subgroup(NamedTuple):
#     category_id: str
#     category_title: str
#     id: str
#     title: str
#     data: pd.DataFrame
#     fields: list[str]


class Category(NamedTuple):
    # id: str
    # title: str
    # subgroups: list[Subgroup]
    id: str
    data: pd.DataFrame
    fields: list[str]

    @property
    def title(self):
        lut = {
            "cortico_inhibitor": "Corticosteroid Inhibitors",
            "nsaid": "NSAID",
        }

        if self.id in lut:
            return lut[self.id]
        return self.id.title()
