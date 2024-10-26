import random
from typing import Dict

import pandas as pd
from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.reactive import reactive
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    Static,
    TabbedContent,
    TabPane,
)

from pharmq.models.quiz import QuizGenerator
from pharmq.models.settings import Settings
from pharmq.widgets.quiz_option import QuizOptionWidget
from pharmq.widgets.settings import CategorySelect, SettingsButton, SettingsModal

from .models.category import Category
from .utils.data_loader import load_csv_data
from .widgets.categories import CategoryTable
from .widgets.quiz import QuizQuestionWidget, create_characteristics_table

# def on_button_pressed(self, event: Button.Pressed) -> None:
#     """Handle button presses."""
#     button_id = event.button.id

#     if button_id == "settings-button":
#         self.push_screen(SettingsModal())
#         return


class DrugQuizApp(App):
    """A quiz application for drug-related questions."""

    CSS_PATH = "styles.tcss"

    current_question = reactive(None)
    current_answer = reactive(None)
    current_category = reactive(None)
    all_options = reactive([])
    question_answered = reactive(False)
    categories: Dict[str, Category] = load_csv_data()

    quiz_generator = QuizGenerator(categories)

    selected_categories: reactive[set[str] | None] = reactive(None)
    # debug_selected_categories = reactive(None, always_update=True, recompose=True)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        # with Header():
        yield Header()
        # yield Label(id="dbg")
        # with ScrollableContainer():
        # with TabbedContent(initial="categories-tab"):
        with TabbedContent() as tabs:
            with TabPane("Quiz", id="quiz-tab"):
                yield Container(QuizQuestionWidget(), id="quiz")
            with TabPane("Categories", id="categories-tab"):
                yield CategoryTable(self.categories)

    def on_mount(self) -> None:
        """Generate the first question when the app starts."""
        if not self.categories:
            self.query_one("#category", Static).update(
                Text("No data files found in ./data directory", style="bold red")
            )
            return
        self.generate_question()

    @on(CategorySelect.Updated)
    def update_categories(self, ev: CategorySelect.Updated):
        # assert 0, ev.categories
        self.selected_categories = ev.categories
        self.debug_selected_categories = ",".join(ev.categories)
        # self.query_one("#dbg", Label).update(self.debug_selected_categories)

    def generate_question(self) -> None:
        """Generate a new question from a random category."""
        self.question_answered = False

        question = self.quiz_generator.generate_question(self.selected_categories)

        quiz_widget = self.query_one(QuizQuestionWidget)
        quiz_widget.set_question(question)

        category_text = Text("Category: ", style="grey50")
        category_text.append(self.categories[question.category_name].title, style="grey70")
        self.query_one("#category", Static).update(category_text)

        # Create and update table display
        # characteristics_table = create_characteristics_table(row, category.fields)
        characteristics_table = create_characteristics_table(question.characteristics)
        self.query_one("#question", Static).update(characteristics_table)
        self.query_one("#feedback", Static).update("")
        self.query_one("#next", Button).disabled = True

    @on(QuizOptionWidget.Linked)
    def link_option(self, event: QuizOptionWidget.Linked) -> None:
        """Link a QuizOption to the correct index."""

        tabs = self.query_one(TabbedContent)
        tabs.active = "categories-tab"

        option = event.option
        table = self.query_one(f"#category-table-{option.category_name}", DataTable)

        table.scroll_visible(duration=0.75)
        table.move_cursor(row=option.row_index, scroll=True)

    @on(QuizQuestionWidget.Answered)
    def check_answer(self, event: QuizQuestionWidget.Answered):
        self.question_answered = True

        # Enable next question button
        self.query_one("#next", Button).disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""

        button_id = event.button.id

        if button_id == "next":
            self.generate_question()
            return

        assert False


if __name__ == "__main__":
    app = DrugQuizApp()
    app.run()
