from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DirectoryTree
from textual.widgets._tree import TOGGLE_STYLE, Tree, TreeNode
from rich.style import Style
from dataclasses import dataclass
from rich.text import Text, TextType
from pathlib import Path
from asyncio import Queue
from typing import TYPE_CHECKING, Callable, ClassVar, Iterable, Iterator


@dataclass
class DirEntry:
    """Attaches directory information to a [`DirectoryTree`][textual.widgets.DirectoryTree] node."""

    path: Path
    """The path of the directory entry."""
    loaded: bool = False
    """Has this been loaded?"""
    
class CustomTree(DirectoryTree):
    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "directory-tree--extension",
        "directory-tree--file",
        "directory-tree--folder",
        "directory-tree--hidden",
        "directory-tree--subproject",
    }
    
    DEFAULT_CSS = """
    DirectoryTree {
        
        & > .directory-tree--folder {
            text-style: bold;
        }

        & > .directory-tree--extension {
            text-style: italic;
        }

        & > .directory-tree--hidden {
            color: $text 50%;
        }

        &:ansi {
        
            & > .tree--guides {
               color: transparent;              
            }
        
            & > .directory-tree--folder {
                text-style: bold;
            }

            & > .directory-tree--extension {
                text-style: italic;
            }

            & > .directory-tree--hidden {
                color: ansi_default;
                text-style: dim;
            }
        }
    }

    """
    
    def __init__(
        self,
        path: str | Path,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        selected: list = [],
    ) -> None:
        """Initialise the directory tree.

        Args:
            path: Path to directory.
            name: The name of the widget, or None for no name.
            id: The ID of the widget in the DOM, or None for no ID.
            classes: A space-separated list of classes, or None for no classes.
            disabled: Whether the directory tree is disabled or not.
        """
        super().__init__(
            path,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.selected = selected
        
    def render_label(
        self, node: TreeNode[DirEntry], base_style: Style, style: Style
    ) -> Text:
        """Render a label for the given node.

        Args:
            node: A tree node.
            base_style: The base style of the widget.
            style: The additional style for the label.

        Returns:
            A Rich Text object containing the label.
        """
        node_label = node._label.copy()
        if node_label.plain in self.selected:
            style = style + Style(color="green", italic=True)
        node_label.stylize(style)

        # If the tree isn't mounted yet we can't use component classes to stylize
        # the label fully, so we return early.
        if not self.is_mounted:
            return node_label

        if node._allow_expand:
            prefix = (
                self.ICON_NODE_EXPANDED if node.is_expanded else self.ICON_NODE,
                base_style + TOGGLE_STYLE,
            )
            node_label.stylize_before(
                self.get_component_rich_style("directory-tree--folder", partial=True)
            )
        else:
            prefix = (
                self.ICON_FILE,
                base_style,
            )
            node_label.stylize_before(
                self.get_component_rich_style("directory-tree--file", partial=True),
            )
            node_label.highlight_regex(
                r"\..+$",
                self.get_component_rich_style(
                    "directory-tree--extension", partial=True
                ),
            )
        
        if node_label.plain.startswith("."):
            node_label.stylize_before(
                self.get_component_rich_style("directory-tree--hidden")
            )

        text = Text.assemble(prefix, node_label)
        return text
    

class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield CustomTree('monorepo-sample', selected=["sub-one"])
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = StopwatchApp()
    app.run()