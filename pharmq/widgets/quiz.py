from typing import Mapping

import pandas as pd
from rich.table import Table
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import (
    Container,
    Grid,
    Horizontal,
    ScrollableContainer,
    Vertical,
)
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Label, Static

from pharmq.models.quiz import QuizQuestion
from pharmq.widgets.quiz_option import QuizOptionWidget
from pharmq.widgets.settings import SettingsButton


class QuizQuestionWidget(Static):
    """A widget to display the current question."""

    question: QuizQuestion | None = None

    class Answered(Message):
        pass

    def compose(self) -> ComposeResult:
        # with Vertical(id="quiz-content"):

        with ScrollableContainer():
            yield Static(
                Text("What drug has these characteristics?", style="bold cyan"),
                id="prompt",
            )
            yield Static(id="category")
            with ScrollableContainer():
                yield Static(id="question", classes="question-container")

            with Container(id="controls"):
                with Container(id="options"):
                    yield QuizOptionWidget(id="option_0", option_index=0)
                    yield QuizOptionWidget(id="option_1", option_index=1)
                    yield QuizOptionWidget(id="option_2", option_index=2)
                    yield QuizOptionWidget(id="option_3", option_index=3)
                with Grid():
                    with Widget(id="settings-container"):
                        yield SettingsButton()
                    with Widget(id="feedback-container"):
                        # yield Label()
                        yield Label(id="feedback", classes="feedback")
                    with Widget(id="next-container"):
                        yield Button(
                            "Next Question",
                            id="next",
                            disabled=True,
                        )

    def set_question(self, question: QuizQuestion):
        self.question = question

        for button, option in zip(self.query(QuizOptionWidget), question.options):
            # assert False, (button, option)
            button.remove_class("correct")
            button.remove_class("incorrect")
            button.remove_class("option--disabled")
            button.btn_disabled = False
            button.update(option)

    @on(QuizOptionWidget.Answered)
    def option_clicked(self, event: QuizOptionWidget.Answered):
        assert self.question

        assert event.button.option

        for button in self.query(QuizOptionWidget):
            button.btn_disabled = True

        if event.button.option.text == self.question.answer:
            self.query_one("#feedback", Static).update("✓ Correct!")
            event.button.add_class("correct")
        else:
            self.query_one("#feedback", Static).update("✗ Incorrect!")
            event.button.add_class("incorrect")

            correct_index = self.question.answer_index
            correct_button = self.query(QuizOptionWidget)[correct_index]
            correct_button.add_class("correct")

        self.post_message(self.Answered())


# def create_characteristics_table(row: pd.Series, fields: list[str]) -> Table:
def create_characteristics_table(fields: Mapping[str, str]) -> Table:
    """Create a rich table for characteristics."""
    table = Table(
        show_header=False,
        show_lines=True,
        border_style="green",
        padding=(0, 1),
    )

    table.add_column("Characteristic", style="bold green")
    table.add_column("Description", style="white")

    for field in fields:
        if not pd.isna(fields[field]) and fields[field] != "":
            table.add_row(f"● {field}", str(fields[field]))

    return table
