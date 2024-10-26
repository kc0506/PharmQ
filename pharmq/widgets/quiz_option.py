from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, Static

from pharmq.models.quiz import QuizOption


class QuizOptionWidget(Horizontal):
    """A custom quiz option that splits into two parts when disabled."""

    option: QuizOption | None = None
    btn_disabled = reactive(False)
    is_correct = reactive(False)
    option_index = reactive(0)

    DEFAULT_CSS = """
    QuizOptionWidget {
        width: 100%;
        height: 3;
        # layout: grid;
        # grid-size: 2 1;
        layout: horizontal;
        background: transparent;
    }

    QuizOptionWidget .main {
        width: 100%;
        # width: 50%;
        height: 3;
        content-align: left middle;
        padding: 0 1;
    }

    QuizOptionWidget .link {
        display: none;
    }

    QuizOptionWidget.disabled .link {
        margin-left: 2;
        display: block;
        width: 3;
        dock: right;
        # background: default;
    }

    QuizOptionWidget.correct  .main {
        background: green 50%;
        color: white;
    }

    QuizOptionWidget.incorrect .main {
        background: red 50%;
        color: white;
    }

    # QuizOptionWidget .main{
    #     background: transparent;
    #     border: solid green;
    #     width: 30%;
    # }

    # QuizOptionWidget .main.disabled {
    #     opacity: 0.7;
    # }
    """

    class Answered(Message):
        def __init__(self, option_index: int, button: "QuizOptionWidget") -> None:
            self.option_index = option_index
            self.button = button
            super().__init__()

    class Linked(Message):
        def __init__(self, option: QuizOption) -> None:
            self.option = option
            super().__init__()

    def __init__(
        self,
        option_index: int = 0,
        disabled: bool = False,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self.option_index = option_index
        self.disabled = disabled

    def compose(self) -> ComposeResult:
        """Create the initial single button view."""
        yield Button(
            f"  {chr(65+self.option_index)}.",
            id=f"option-main-{self.option_index}",
            classes="main",
        )
        link_btn = Button(
            "➜",
            # "✈️️",
            id=f"option-link-{self.option_index}",
            classes="link",
        )
        link_btn.can_focus = False
        yield link_btn

    def update(
        self,
        option: QuizOption,
    ) -> None:
        """Update the value of this option."""
        self.option = option
        self.query_one(
            f"#option-main-{self.option_index}", Button
        ).label = f"  {chr(65+self.option_index)}. {option.text}"

    @on(Button.Pressed)
    def on_click(self, event: Button.Pressed) -> None:
        assert self is event.button.parent

        event.stop()

        if "main" in event.button.classes:
            self.post_message(self.Answered(self.option_index, self))
            return

        assert "link" in event.button.classes

        assert self.option
        self.post_message(self.Linked(self.option))

    def watch_btn_disabled(self, disabled: bool) -> None:
        """Handle disabled state changes."""
        # return
        main_button = self.query_one(".main", Button)
        link_button = self.query_one(".link", Button)

        # main_button.styles.border_left = "solid", "green"
        # link_button.styles.border_left = "solid", "red"

        if disabled:
            self.add_class("disabled")
        else:
            self.remove_class("disabled")

        if disabled:
            main_button.add_class("disabled")
            main_button.disabled = True
            link_button.disabled = False
        else:
            main_button.remove_class("disabled")
            main_button.disabled = False
            link_button.disabled = True

        link_button.disabled = False
