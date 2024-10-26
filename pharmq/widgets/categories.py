from typing import Dict, Unpack

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.widgets import DataTable, Label, Static, Tree

from ..models.category import Category


class SimpleTOC(Tree):
    """Simple table of contents without collapse functionality."""

    # def __init__(self) -> None:
    #     # super().__init__("Categories")
    #     self.show_root = False

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle node selection."""
        if table_id := event.node.data:
            table = self.app.query_one(f"#{table_id}", DataTable)
            table.scroll_visible()


class CategoryTable(Static):
    """A widget to display category data tables with navigation."""

    def __init__(self, categories: Dict[str, Category]) -> None:
        super().__init__()
        self.categories = categories

    def compose(self) -> ComposeResult:
        """Create tables for all categories with TOC"""
        with Horizontal():
            # Left side: Table of Contents
            with Vertical() as left_side:
                left_side.styles.width = "20%"

                title = Label("Table of Contents")
                title.styles.margin = (0, 0, 1, 1)
                yield title

                toc = SimpleTOC("Categories", id="toc")
                toc.show_root = False

                for category in self.categories.values():
                    toc.root.add_leaf(
                        category.title, data=f"category-table-{category.id}"
                    )
                yield toc

            # Right side: Tables
            with ScrollableContainer():
                for category_name, category in self.categories.items():
                    yield Static(
                        f"\n{category_name.upper()}\n", classes="category-header"
                    )
                    table = DataTable(
                        id=f"category-table-{category_name}",
                        zebra_stripes=True,
                        header_height=2,
                    )
                    self.table = table

                    # # Add columns
                    # answer_column = category.data.columns[0]
                    # table.add_columns(answer_column, *category.fields)

                    # # Add rows with multi-line support
                    # row_keys = []
                    # for _, row in category.data.iterrows():
                    #     table_row = [self.format_cell_content(row[answer_column])]
                    #     table_row.extend(
                    #         self.format_cell_content(row[field])
                    #         for field in category.fields
                    #     )
                    #     key = table.add_row(*table_row, height=2)
                    #     row_keys.append(key)

                    # Add columns
                    table.add_columns(category.answer_field, *category.fields)

                    # Add rows with multi-line support
                    row_keys = []
                    for row in category.data:
                        table_row = [
                            self.format_cell_content(row[category.answer_field])
                        ]
                        table_row.extend(
                            self.format_cell_content(row[field])
                            for field in category.fields
                        )
                        key = table.add_row(*table_row, height=2)
                        row_keys.append(key)

                    yield table
                    yield Static("\n")  # Spacing between tables

        self.row_keys = row_keys

    def format_cell_content(self, content: str) -> str:
        """Format cell content with proper line breaks."""
        if content is None:
        # if pd.isna(content):
            return "-"
        return str(content).replace(";", "\n")
        return str(content).replace(";", "\n")
