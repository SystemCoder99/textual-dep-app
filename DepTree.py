from textual.app import App, ComposeResult
from textual.widgets import Tree, Button, SelectionList, Label
from textual.widgets.selection_list import Selection
from textual.widgets._tree import TreeNode
from textual.containers import Horizontal, Vertical
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, Generic, Iterable, NewType, TypeVar, cast
import rich.repr
from rich.style import NULL_STYLE, Style
from rich.text import Text, TextType

TreeDataType = TypeVar("TreeDataType")
"""The type of the data for a given instance of a [Tree][textual.widgets.Tree]."""

TOGGLE_STYLE = Style.from_meta({"toggle": True})

class DepTree(Tree):
    
    def __init__(
        self,
        label: TextType,
        data: TreeDataType | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(
            label,
            data,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.ICON_NODE = "🚝 "
        self.ICON_NODE_EXPANDED = self.ICON_NODE
        
    def render_label(
        self,
        node: TreeNode[TreeDataType],
        base_style: Style,
        style: Style,
    ) -> Text:
        """Render a label for the given node. Override this to modify how labels are rendered.

        Args:
            node (TreeNode[TreeDataType]): A Tree Node
            base_style (Style): The Base Style of the widget
            style (Style): The additional style for the label

        Returns:
            Text: A Rich Text object containing the label.
        """        
        
        node_label = node._label.copy()
        node_label.stylize(style)
        
        if node._allow_expand:
            icon_exp = self.ICON_NODE_EXPANDED
            
            if node_label.plain == "root":
                icon_exp = "🌳 "
                
            prefix = (
                icon_exp,
                base_style + TOGGLE_STYLE,
            )
            node_label.stylize((style + Style(color="green", italic=True)))
        else:
            if node_label.plain in [" ➕ ", " 🔃 "]:
                prefix = ("", base_style)
            else:
                prefix = ("🛑 ", base_style)
        
        return Text.assemble(prefix, node_label)
    
    def process_label(self, label: TextType) -> Text:
        """Process a `str` of `Text` value into a label.
        
        May be overridden in a subclass to change how labels are rendered.

        Args:
            label (TextType): The Label to process.

        Returns:
            Text: A Rich text object.
        """        
        if isinstance(label, str):
            text_label = Text.from_markup(label)
        else:
            text_label = label
        
        if not isinstance(text_label, Button):
            return text_label.split()[0]
        if text_label.id == "add_deps":
            return " ➕ "
        elif text_label.id == "reset_deps":
            return " 🔃 "
    
class TreeApp(App):
    def __init__(self, subprojects):
        self.subprojects = subprojects
        super().__init__()
        
    def compose(self) -> ComposeResult:
        with Horizontal(id="parent_container"):
            tree: DepTree[dict] = DepTree("root")
            tree.root.expand()
            for project in self.subprojects:
                proj = tree.root.add(project, expand=True)
                proj.add_leaf(Button("Default", id="add_deps"))
            yield tree
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit_dep_choice":
            parent_id = int(self.query_one(Label).id.split('_')[-1])
            tree = self.query_one(DepTree)
            selected = self.query_one(SelectionList).selected
            hori = self.query_one(Horizontal)
            vert = self.query_one("#vertical")
            vert.remove()
            
            parent_node = tree.get_node_by_id(parent_id)
            parent_node.remove_children()
            parent_node.add_leaf(Button("Default", id="reset_deps"))
            for proj in selected:
                parent_node.add_leaf(proj)
            
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if event.node.label.plain in [" ➕ ", " 🔃 "]:
            parent = event.node.parent
            label_id = f"label_for_{str(parent.id)}"
            hor = self.query_one("#parent_container")
            vert = Vertical(
                Label(f"Choosing dependencies for {parent}", id=label_id),
                SelectionList(
                    *[
                        Selection(subproj, subproj)
                        for subproj in self.subprojects
                        if subproj != parent.label.plain
                    ],
                    id="selections"
                ),
                Button("Submit Deps", id="submit_dep_choice"),
                id="vertical"
            )
            hor.mount(vert)
            
            
if __name__ == "__main__":
    app = TreeApp(["sub-one","sub-two","sub-three","sub-four","sub-five"])
    print(app.run())