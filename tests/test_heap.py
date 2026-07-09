import random

import pytest

from algos.heap import MinHeap


def test_empty_heap_is_falsy_and_empty():
    heap = MinHeap()
    assert len(heap) == 0
    assert not heap
    assert bool(MinHeap([1])) is True


def test_peek_and_pop_on_empty_raise():
    heap = MinHeap()
    with pytest.raises(IndexError):
        heap.peek()
    with pytest.raises(IndexError):
        heap.pop()


def test_push_then_pop_yields_ascending_order():
    heap = MinHeap()
    for value in [5, 1, 4, 2, 8, 3]:
        heap.push(value)
    assert [heap.pop() for _ in range(len(heap))] == [1, 2, 3, 4, 5, 8]


def test_peek_returns_min_without_removing():
    heap = MinHeap([3, 1, 2])
    assert heap.peek() == 1
    assert len(heap) == 3
    assert heap.pop() == 1


def test_constructor_heapifies_iterable():
    data = [9, 3, 7, 1, 8, 2, 6, 4, 5, 0]
    heap = MinHeap(data)
    assert len(heap) == len(data)
    assert [heap.pop() for _ in range(len(heap))] == sorted(data)


def test_duplicates_are_kept():
    heap = MinHeap([2, 1, 2, 1, 2])
    assert len(heap) == 5
    assert [heap.pop() for _ in range(5)] == [1, 1, 2, 2, 2]


def test_works_on_any_comparable_type():
    heap = MinHeap(["cherry", "apple", "banana"])
    assert heap.pop() == "apple"
    assert heap.pop() == "banana"

    tuples = MinHeap([(2, "b"), (1, "z"), (1, "a")])
    assert tuples.pop() == (1, "a")


def test_push_updates_length():
    heap = MinHeap()
    assert len(heap) == 0
    heap.push(10)
    assert len(heap) == 1 and bool(heap)


@pytest.mark.parametrize("seed", range(25))
def test_randomized_pops_are_sorted(seed):
    rng = random.Random(seed)
    data = [rng.randint(-50, 50) for _ in range(rng.randint(0, 60))]
    heap = MinHeap(data)
    popped = [heap.pop() for _ in range(len(heap))]
    assert popped == sorted(data)
    assert len(heap) == 0


@pytest.mark.parametrize("seed", range(25))
def test_randomized_interleaved_push_pop(seed):
    rng = random.Random(seed)
    heap = MinHeap()
    reference = []
    for _ in range(200):
        if reference and rng.random() < 0.4:
            assert heap.peek() == min(reference)
            assert heap.pop() == min(reference)
            reference.remove(min(reference))
        else:
            value = rng.randint(0, 100)
            heap.push(value)
            reference.append(value)
        assert len(heap) == len(reference)
    assert [heap.pop() for _ in range(len(heap))] == sorted(reference)
