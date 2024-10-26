import random
from dataclasses import dataclass
from typing import List, Tuple

from .category import Category


@dataclass
class QuizOption:
    """Data for a quiz option."""

    text: str
    category_name: str
    row_index: int
    is_correct: bool = False


@dataclass
class QuizQuestion:
    """Data for a quiz question."""

    category_name: str
    row_index: int
    answer: str
    answer_index: int
    options: List[QuizOption]
    characteristics: dict[str, str]  # field -> value


class QuizGenerator:
    """Quiz generation logic."""

    def __init__(self, categories: dict[str, Category]):
        self.categories = categories

    def generate_question(
        self, selected_categories: set[str] | None = None
    ) -> QuizQuestion:
        """Generate a new question from available categories."""
        # Filter categories
        available_categories = (
            set(self.categories.keys())
            if selected_categories is None
            else selected_categories & set(self.categories.keys())
        )
        if not available_categories:
            available_categories = set(self.categories.keys())

        # Select random category
        category_name: str = random.choice(list(available_categories))
        category: Category = self.categories[category_name]

        # # Select random row
        # answer_column: str = category.data.columns[0]
        # df: pd.DataFrame = category.data
        # row_idx: int = df.sample(n=1).index[0]
        # row: pd.Series = df.iloc[row_idx]
        # answer: str = str(row[answer_column])

        # # Generate incorrect options
        # other_indices: List[int] = df[df[answer_column] != answer].index.tolist()

        # Select random row
        data: list[dict[str, str]] = category.data
        answer_field: str = category.answer_field
        row_idx: int = random.randrange(len(data))
        row: dict[str, str] = data[row_idx]
        answer: str = row[answer_field]

        # Generate incorrect options
        other_indices: List[int] = [
            idx
            for idx, r in enumerate(data)
            if idx != row_idx and r[answer_field] != answer
        ]

        # Create options
        options: List[QuizOption] = [
            QuizOption(
                text=answer,
                category_name=category_name,
                row_index=row_idx,
                is_correct=True,
            )
        ]

        # Add incorrect options
        if len(other_indices) >= 3:
            selected_indices = random.sample(other_indices, 3)
        else:
            # If not enough unique options, allow duplicates
            selected_indices = other_indices + random.choices(
                other_indices or [row_idx], k=3 - len(other_indices)
            )

        for idx in selected_indices:
            options.append(
                QuizOption(
                    # text=str(df.iloc[idx][answer_column]),
                    text=str(data[row_idx][answer_field]),
                    category_name=category_name,
                    row_index=idx,
                    is_correct=False,
                )
            )

        # Shuffle options
        random.shuffle(options)

        answer_index = next(i for i, option in enumerate(options) if option.is_correct)

        # Get characteristics for the question
        characteristics = {
            field: str(row[field]) for field in category.fields if row[field]
        }

        return QuizQuestion(
            category_name=category_name,
            row_index=row_idx,
            answer=answer,
            answer_index=answer_index,
            options=options,
            characteristics=characteristics,
        )
