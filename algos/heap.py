from __future__ import annotations

from typing import Iterable, Protocol, TypeVar


class Comparable(Protocol):
    def __lt__(self, other: object, /) -> bool: ...


T = TypeVar("T", bound=Comparable)


class MinHeap:
    """A binary min-heap backed by a flat list.

    For the node at index ``i``, its children live at ``2*i + 1`` and
    ``2*i + 2`` and its parent at ``(i - 1) // 2``. Only ``<`` is ever used
    to compare elements, so any type with ``__lt__`` works.
    """

    def __init__(self, items: Iterable[T] | None = None) -> None:
        self._heap: list[T] = list(items) if items is not None else []
        # Bottom-up heapify in O(n): sift every non-leaf, last parent to root.
        for i in reversed(range(len(self._heap) // 2)):
            self._sift_down(i)

    def __len__(self) -> int:
        return len(self._heap)

    def __bool__(self) -> bool:
        return bool(self._heap)

    def peek(self) -> T:
        if not self._heap:
            raise IndexError("peek from an empty heap")
        return self._heap[0]

    def push(self, value: T) -> None:
        self._heap.append(value)
        self._sift_up(len(self._heap) - 1)

    def pop(self) -> T:
        if not self._heap:
            raise IndexError("pop from an empty heap")
        top = self._heap[0]
        last = self._heap.pop()
        if self._heap:  # heap held more than one element
            self._heap[0] = last
            self._sift_down(0)
        return top

    def _sift_up(self, i: int) -> None:
        # Carve out a hole at i and slide it up until value fits above it.
        heap = self._heap
        value = heap[i]
        while i > 0:
            parent = (i - 1) // 2
            if not value < heap[parent]:
                break
            heap[i] = heap[parent]
            i = parent
        heap[i] = value

    def _sift_down(self, i: int) -> None:
        # Carve out a hole at i and slide it down through its smaller child.
        heap = self._heap
        n = len(heap)
        value = heap[i]
        child = 2 * i + 1
        while child < n:
            right = child + 1
            if right < n and heap[right] < heap[child]:
                child = right
            if not heap[child] < value:
                break
            heap[i] = heap[child]
            i = child
            child = 2 * i + 1
        heap[i] = value
