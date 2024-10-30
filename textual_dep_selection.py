from textual.app import App, ComposeResult
from textual.widgets import Collapsible, Footer, Label, Markdown, Button
from textual.screen import Screen
from textual.containers import VerticalScroll, Horizontal
from textual import on
from textual.events import Mount
from textual.widgets import Footer, Header, Pretty, SelectionList
from textual.widgets.selection_list import Selection


class DepSelect(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
    
    def __init__(self, selected, target_project):
        super().__init__()
        self.selected = selected
        self.target = target_project

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield SelectionList[str](
                *[
                    Selection(project, project)
                    for project in self.selected
                    if project != self.target
                ]
            )
            yield Pretty([])
        yield Button("Submit", variant="primary", id="deps")
    
    def on_mount(self) -> None:
        self.query_one(SelectionList).border_title = f"Select {self.target}'s dependencies:"
        self.query_one(Pretty).border_title = "Selected Dependencies"

    @on(Mount)
    @on(SelectionList.SelectedChanged)
    def update_selected_view(self) -> None:
        self.query_one(Pretty).update(self.query_one(SelectionList).selected)
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "deps":
            self.dismiss(self.query_one(Pretty))
        else:
            self.dismiss([])


class CollapsibleApp(App[None]):
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
        
        self.push_screen(DepSelect(self.subprojects, event.button.id), process_deps)


if __name__ == "__main__":
    app = CollapsibleApp(["sub-one","sub-two","sub-three","sub-four","sub-five"])
    app.run()