from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll, Container
from textual.events import Mount
from textual.widgets import Footer, Header, Pretty, SelectionList, Button, Collapsible
from textual.widgets.selection_list import Selection
from textual.screen import Screen
from rich.pretty import Pretty as prettyRenderable
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

class ReversePretty(prettyRenderable):
    
    def __init__(
        self,
        _object,
        highlighter = None,
        *,
        indent_size: int = 4,
        justify = None,
        overflow = None,
        no_wrap: Optional[bool] = False,
        indent_guides: bool = False,
        max_length: Optional[int] = None,
        max_string: Optional[int] = None,
        max_depth: Optional[int] = None,
        expand_all: bool = False,
        margin: int = 0,
        insert_line: bool = False,
        ):
        
        super().__init__(_object, highlighter, indent_size=indent_size, justify=justify, overflow=overflow, no_wrap=no_wrap,
                         indent_guides=indent_guides, max_length=max_length, max_string=max_string, max_depth=max_depth,
                         expand_all=expand_all, margin=margin, insert_line=insert_line)
        self._object = _object
    
    def return_origin_object(self):
        return self._object

class PrettyWidget(Pretty):
    def __init__(
        self,
        object,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialise the `Pretty` widget.

        Args:
            object: The object to pretty-print.
            name: The name of the pretty widget.
            id: The ID of the pretty in the DOM.
            classes: The CSS classes of the pretty.
        """
        self.origin = object
        super().__init__(
            object,
            name=name,
            id=id,
            classes=classes,
        )
        
    def return_origin(self):
        return self.origin
    
    def update(self, object: Any) -> None:
        """Update the content of the pretty widget.

        Args:
            object: The object to pretty-print.
        """
        self._renderable = ReversePretty(object)
        self.origin = object
        self.clear_cached_dimensions()
        self.refresh(layout=True)
        

class SelectionListApp(Screen):
    CSS_PATH = "selection_list_selected.tcss"

    def __init__(self, select_from, target):
        self.select_from = select_from
        self.target = target
        super().__init__()
        self.selections = [
            Selection(project, project)
            for project in self.select_from
            if project != target
        ]
        
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield SelectionList[str](  
                *self.selections
            )
            with VerticalScroll():
                with Container(id="pretty"):
                    yield PrettyWidget([])
                with Container(id="button-con"):
                    yield Button("Submit", variant="primary", id="deps")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(SelectionList).border_title = "Identified Subprojects"
        self.query_one(PrettyWidget).border_title = "Selected as Dependencies"

    @on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_selected_view(self) -> None:
        self.query_one(PrettyWidget).update(self.query_one(SelectionList).selected)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "deps":
            self.dismiss(self.query_one(PrettyWidget).return_origin())
        else:
            self.dismiss([])


class CollapsibleApp(Screen):
    """An example of collapsible container."""

    BINDINGS = [
        ("c", "collapse_or_expand(True)", "Collapse All"),
        ("e", "collapse_or_expand(False)", "Expand All"),
    ]
    
    def __init__(self, subprojects):
        self.subprojects = subprojects
        super().__init__()

    def compose(self) -> ComposeResult:
        """Compose app with collapsible containers."""
        for project in self.subprojects:
            col_id = f"col_{project}"
            button_id = f"{project}"
            with Collapsible(collapsed=False, title=project, id=col_id):
                yield Button(f"Add Dependency to {project}", variant="primary", id=button_id)
        yield Footer()
        
    def action_collapse_or_expand(self, collapse: bool) -> None:
        for child in self.walk_children(Collapsible):
            child.collapsed = collapse
    
    def on_button_pressed(self, event: Button.Pressed):
        
        def process_deps(list_selected):
            with open('tmptext.txt', 'w') as f:
                f.write(str(list_selected))
                
        if event.button.id != "deps":
            process_deps(self.run_worker(self.dep_select_screen(self.subprojects, event.button.id)))
    
    def dep_select_screen(self, subprojects, button):
        return self.app.push_screen(SelectionListApp(subprojects, button))


class DepApp(App):
    
    def __init__(self, subprojects):
        self.subprojects = subprojects
        super().__init__()
    
    def on_mount(self):
        self.install_screen(CollapsibleApp(self.subprojects), name="base")
        self.push_screen("base")
                

if __name__ == "__main__":
    app = DepApp(["sub-one","sub-two","sub-three","sub-four","sub-five"])
    app.run()
