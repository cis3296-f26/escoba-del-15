from escoba.ui.element import Element

class Layer(Element):
    # kids keyed by tag so sync can update in place instead of rebuilding (keeps lerps alive)
    def __init__(self):
        super().__init__(focusable=False)
        self._by_tag: dict = {}
        self.children: list[Element] = []
        self.focus_tag = None

    @property
    def idle(self) -> bool:
        return all(child.idle for child in self.children)

    def sync(self, items):
        # each item is (tag, create, apply), create only on first sight, apply every time
        seen = set()
        ordered = []

        for tag, create, apply in items:
            seen.add(tag)
            element = self._by_tag.get(tag)
            if element is None:
                element = create()
                element.tag = tag
                self._by_tag[tag] = element
            apply(element)
            ordered.append(element)

        for tag in list(self._by_tag):
            if tag not in seen:
                del self._by_tag[tag]

        self.children = ordered

    def update(self, dt: float):
        for child in self.children:
            child.update(dt)

    def snap_all(self):
        for child in self.children:
            child.snap()

    def hit(self, pos) -> bool:
        return self.hit_child(pos) is not None

    def hit_child(self, pos) -> Element | None:
        for child in reversed(self.children):
            if child.hit(pos):
                return child
        return None

    def _child_focused(self, child) -> bool:
        focus = self.focus_tag
        if focus is None:
            return False
        if child.tag == focus:
            return True
        # cards are tagged by identity, focus still matches zone + index
        return getattr(child, "zone", None) in ("hand", "table") and (child.zone, child.index) == focus

    def draw(self, surface, resources, focused: bool = False):
        for child in self.children:
            if child.visible:
                child.draw(surface, resources, focused=self._child_focused(child))
