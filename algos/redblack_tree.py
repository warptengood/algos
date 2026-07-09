from __future__ import annotations

from enum import Enum, auto
from typing import Generic, Iterable, Iterator, Protocol, TypeVar


class Comparable(Protocol):
    def __lt__(self, other: object, /) -> bool: ...


T = TypeVar("T", bound=Comparable)


class Color(Enum):
    RED = auto()
    BLACK = auto()


class Node(Generic[T]):
    __slots__ = ("key", "color", "parent", "left", "right")

    def __init__(
        self,
        key: T,
        color: Color,
        parent: Node[T],
        left: Node[T],
        right: Node[T],
    ) -> None:
        self.key = key
        self.color = color
        self.parent = parent
        self.left = left
        self.right = right


class RedBlackTree(Generic[T]):
    """A self-balancing binary search tree, usable as an ordered set.

    Invariants that keep the tree balanced:

    1. Every node is red or black.
    2. The root is black.
    3. Every leaf (the shared ``_nil`` sentinel) is black.
    4. A red node's children are black (no two reds in a row).
    5. Every root-to-leaf path crosses the same number of black nodes.

    All leaves are a single shared black *sentinel* (``_nil``) rather than
    ``None``. This gives every real node non-null children with a real
    ``parent`` pointer, so insertion and deletion fix-ups never special-case
    "off the edge of the tree". Only ``<`` is used to order keys, so any type
    with ``__lt__`` works.
    """

    def __init__(self, items: Iterable[T] | None = None) -> None:
        # One shared sentinel stands in for every leaf; its key is never read.
        self._nil: Node[T] = Node.__new__(Node)
        self._nil.color = Color.BLACK
        self._nil.parent = self._nil.left = self._nil.right = self._nil
        self._root: Node[T] = self._nil
        self._size = 0
        if items is not None:
            for item in items:
                self.insert(item)

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def __contains__(self, key: object) -> bool:
        return self._find(key) is not self._nil

    def __iter__(self) -> Iterator[T]:
        # In-order traversal yields keys in ascending order.
        def walk(node: Node[T]) -> Iterator[T]:
            if node is self._nil:
                return
            yield from walk(node.left)
            yield node.key
            yield from walk(node.right)

        return walk(self._root)

    def __repr__(self) -> str:
        return f"{type(self).__name__}([{', '.join(map(repr, self))}])"

    def insert(self, key: T) -> None:
        """Add ``key``. No-op if it is already present (this is a set)."""
        parent = self._nil
        node = self._root
        while node is not self._nil:
            parent = node
            if key < node.key:
                node = node.left
            elif node.key < key:
                node = node.right
            else:
                return  # already present

        new_node = Node(key, Color.RED, parent, self._nil, self._nil)
        if parent is self._nil:
            self._root = new_node
        elif key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        self._size += 1
        self._resolve_red_violation(new_node)

    def erase(self, key: T) -> None:
        """Remove ``key``. No-op if it is absent."""
        node = self._find(key)
        if node is self._nil:
            return
        self._size -= 1

        # Reduce to deleting a node with at most one child: swap in the
        # in-order successor's key, then delete the successor instead.
        if node.left is not self._nil and node.right is not self._nil:
            successor = self._minimum(node.right)
            node.key = successor.key
            node = successor

        child = node.left if node.left is not self._nil else node.right
        self._transplant(node, child)

        # Removing a red node can't break any invariant. Removing a black one
        # leaves its path a black short: an adopted red child just repaints
        # black, otherwise the deficit ("double black") needs resolving.
        if node.color is Color.BLACK:
            if child.color is Color.RED:
                child.color = Color.BLACK
            else:
                self._resolve_double_black(child)

    def _find(self, key: object) -> Node[T]:
        node = self._root
        while node is not self._nil:
            if key < node.key:  # type: ignore[operator]
                node = node.left
            elif node.key < key:  # type: ignore[operator]
                node = node.right
            else:
                return node
        return self._nil

    def _minimum(self, node: Node[T]) -> Node[T]:
        while node.left is not self._nil:
            node = node.left
        return node

    def _transplant(self, node: Node[T], replacement: Node[T]) -> None:
        # Splice `replacement` into `node`'s spot. `replacement` may be the
        # sentinel; setting its parent is intentional so a "double black" on
        # the sentinel can still find its way up during the delete fix-up.
        parent = node.parent
        if parent is self._nil:
            self._root = replacement
        elif node is parent.left:
            parent.left = replacement
        else:
            parent.right = replacement
        replacement.parent = parent

    def _rotate(self, pivot: Node[T], to_left: bool) -> None:
        # Rotate `pivot` down and its child up. `to_left` selects the
        # direction; a left rotation pulls up the right child, and vice versa.
        rising = pivot.right if to_left else pivot.left
        assert rising is not self._nil

        # The rising node's inner subtree swings over to become pivot's child.
        inner = rising.left if to_left else rising.right
        if to_left:
            pivot.right = inner
        else:
            pivot.left = inner
        if inner is not self._nil:
            inner.parent = pivot

        # Splice `rising` into pivot's former position.
        rising.parent = pivot.parent
        if pivot.parent is self._nil:
            self._root = rising
        elif pivot is pivot.parent.left:
            pivot.parent.left = rising
        else:
            pivot.parent.right = rising

        # Hang `pivot` beneath `rising`.
        if to_left:
            rising.left = pivot
        else:
            rising.right = pivot
        pivot.parent = rising

    def _resolve_red_violation(self, node: Node[T]) -> None:
        # `node` is red and may clash with a red parent. Walk the violation
        # upward, recoloring where the uncle is red and rotating where it isn't.
        while node.parent.color is Color.RED:
            parent = node.parent
            grandparent = parent.parent
            parent_is_left = parent is grandparent.left
            uncle = grandparent.right if parent_is_left else grandparent.left

            if uncle.color is Color.RED:
                # Push blackness down from the grandparent; recurse upward.
                parent.color = uncle.color = Color.BLACK
                grandparent.color = Color.RED
                node = grandparent
            else:
                # Straighten a "triangle" into a "line", then rotate the
                # grandparent over and recolor.
                if (node is parent.left) != parent_is_left:
                    self._rotate(parent, parent_is_left)
                    node, parent = parent, node
                parent.color = Color.BLACK
                grandparent.color = Color.RED
                self._rotate(grandparent, not parent_is_left)

        self._root.color = Color.BLACK

    def _resolve_double_black(self, node: Node[T]) -> None:
        # `node` carries one unit of surplus blackness. Shed it by borrowing
        # from the sibling's subtree, or push it up toward the root.
        while node is not self._root and node.color is Color.BLACK:
            parent = node.parent
            node_is_left = node is parent.left
            sibling = parent.right if node_is_left else parent.left

            # Case 1: red sibling. Rotate it up so `node` gets a black sibling,
            # then fall through to one of the black-sibling cases below.
            if sibling.color is Color.RED:
                sibling.color = Color.BLACK
                parent.color = Color.RED
                self._rotate(parent, node_is_left)
                sibling = parent.right if node_is_left else parent.left

            near = sibling.left if node_is_left else sibling.right
            far = sibling.right if node_is_left else sibling.left

            if near.color is Color.BLACK and far.color is Color.BLACK:
                # Case 2: sibling's children are both black. Repaint the
                # sibling red and lift the deficit to the parent.
                sibling.color = Color.RED
                node = parent
            else:
                if far.color is Color.BLACK:
                    # Case 3: only the near child is red. Rotate the sibling to
                    # turn this into Case 4.
                    near.color = Color.BLACK
                    sibling.color = Color.RED
                    self._rotate(sibling, not node_is_left)
                    sibling = parent.right if node_is_left else parent.left
                    far = sibling.right if node_is_left else sibling.left

                # Case 4: the far child is red. One rotation settles the debt.
                sibling.color = parent.color
                parent.color = Color.BLACK
                far.color = Color.BLACK
                self._rotate(parent, node_is_left)
                node = self._root  # done

        node.color = Color.BLACK
