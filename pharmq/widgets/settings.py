from pathlib import Path

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Checkbox,
    Label,
    ListView,
    RadioButton,
    RadioSet,
    Static,
)

from pharmq.utils.data_loader import load_csv_data


class CategorySelect(Static):  # Changed from Vertical to Grid
    """A custom multi-select category container with grid layout."""

    DEFAULT_CSS = """
    CategorySelect {
        padding: 1;
    }

    CategorySelect Checkbox {
        width: 100%;
        # height: 4;
        padding: 0 0;
        margin: 0 0;

        # border: solid $primary;
    }

    CategorySelect .all-categories-row{
        height: auto; 
    }
    """

    class CategoryToggled(Message):
        """Message sent when a category is toggled."""

        def __init__(self, category: str, selected: bool) -> None:
            super().__init__()
            self.category = category
            self.selected = selected

    # selected_categories: reactive[set[str] | None] = reactive(None)

    def __init__(self) -> None:
        super().__init__()
        self.categories = get_categories()
        self.selected_categories = set(cat.id for cat in self.categories)

    def compose(self) -> ComposeResult:
        """Create checkboxes in a grid layout."""
        # "All Categories" takes full width
        # with Horizontal(classes="all-categories-row"):
        yield Checkbox("All Categories", id="cat-all", value=True)

        for category in self.categories:
            yield Checkbox(category.title, id=f"cat-{category.id}", value=True)

    def sync_selected(self, selected_categories: set[str]) -> None:
        """Sync selected categories with the given set."""
        self.selected_categories = selected_categories
        has_non_selected = False
        for child in self.query(Checkbox):
            assert child.id
            category = child.id.replace("cat-", "")
            with child.prevent(Checkbox.Changed):
                child.value = category in selected_categories
                if not child.value:
                    has_non_selected = True

        # Update "All Categories" checkbox
        all_checkbox = self.query_one("#cat-all", Checkbox)
        with all_checkbox.prevent(Checkbox.Changed):
            all_checkbox.value = not has_non_selected

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox changes."""

        checkbox_id = event.checkbox.id
        if checkbox_id == "cat-all":
            # Update all other checkboxes
            for child in self.query(Checkbox):
                if child.id != "cat-all":
                    child.value = event.value
        else:
            # Update selected categories set
            assert checkbox_id
            category = checkbox_id.replace("cat-", "")
            if event.value:
                self.selected_categories.add(category)
            else:
                self.selected_categories.discard(category)
                all_checkbox = self.query_one("#cat-all", Checkbox)
                with all_checkbox.prevent(Checkbox.Changed):
                    all_checkbox.value = False

        # self.post_message(self.Updated(self.selected_categories))

    class Updated(Message):
        def __init__(self, categories: set[str]) -> None:
            super().__init__()
            self.categories = categories


class SettingsButton(Button):
    """A button that opens the settings modal."""

    # CSS_PATH = str(Path(__file__).parent / "settings.css")

    DEFAULT_CSS = """
    SettingsButton {
        align: left middle;
        # min-width: 4;
        max-width: 6;
        # width: 4;
        # padding: 1;
        # margin-right: 1;
        # border: none;
        # background: transparent;
        # height: 3;
    }
    
    SettingsButton:hover {
        background: $boost;
    }
    """

    def __init__(self) -> None:
        super().__init__("⚙", variant="default", id="settings-button")
        # super().__init__("123", variant="default", id="settings-button")
        # super().__init__("⚙️️", id="settings-button")
        self.can_focus = False

    @on(Button.Pressed)
    def on_click(self, event:Button.Pressed) -> None:
        """Show the settings modal when clicked."""
        self.app.push_screen(SettingsModal())

        event.stop()


def get_categories():
    data = load_csv_data()
    return list(data.values())


class SettingsModal(ModalScreen):
    """Settings modal with checkboxes for quiz configuration."""

    # CSS_PATH = str(Path(__file__).parent / "settings.tcss")
    def compose(self) -> ComposeResult:
        with Vertical(id="settings-dialog"):
            yield Label("Settings", id="settings-title")

            with Vertical(id="settings-content"):
                # General settings
                # yield Label("General Settings", classes="settings-section-title")
                # yield Checkbox("Show category in quiz", id="show-category", value=True)
                # yield Checkbox(
                #     "Allow duplicate options", id="allow-duplicates", value=False
                # )
                # yield Checkbox(
                #     "Show correct answer immediately", id="show-answer", value=True
                # )

                # Category selection
                yield Label("Quiz Categories", classes="settings-section-title")
                # with Container() as con:
                # con.styles.height = '60'
                yield CategorySelect()

            with Horizontal(id="settings-buttons"):
                yield Button("Save", variant="primary", id="save-button")
                yield Button("Cancel", variant="default", id="cancel-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-button":
            pass
        else:
            assert event.button.id == "save-button"

            select = self.query_one(CategorySelect)
            self.post_message(CategorySelect.Updated(select.selected_categories))

            # TODO: Save settings and update app state

        self.app.pop_screen()
        event.stop()

    CSS = """
    #settings-dialog {
        overflow-y: auto;
        background: $panel;
        padding: 1;
        border: solid $primary;
        min-width: 40;
        max-width: 70%;
        margin: 1 2;
        height: auto;
    }

    #settings-title {
        text-align: center;
        text-style: bold;
        padding: 1;
        border-bottom: solid $primary;
    }

    #settings-content {
        padding: 1;
        height: auto;
    }

    #settings-content Checkbox {
        margin: 1 0;
        padding: 0 1;
    }

    #settings-buttons {
        height: auto;
        padding: 1;
        align-horizontal: right;
    }

    #settings-buttons Button {
        margin-left: 1;
        min-width: 8;
    }


    #settings-content Checkbox {
        margin: 1 0;
        padding: 0 1;
    }

    CategorySelect {
        margin: 1 0;
        padding: 0 1;
        border: solid $primary;
    }

    CategorySelect Checkbox {
        width: 100%;
    }

    CategorySelect Checkbox:hover {
        background: $boost;
    }
    """
