import random

import pytest

from algos.redblack_tree import Color, RedBlackTree


def assert_rb_invariants(tree, expected_keys):
    """Verify the five red-black invariants plus BST order and the dunder API.

    Returns the tree's black-height so callers can spot-check if they like.
    """
    nil = tree._nil
    assert nil.color is Color.BLACK
    assert nil.left is nil and nil.right is nil, "sentinel must self-reference"

    # Rule 2: the root is black (an empty tree's root is the black sentinel).
    if tree._root is not nil:
        assert tree._root.color is Color.BLACK, "root must be black"

    keys = []

    def black_height(node):
        if node is nil:
            return 1
        # BST ordering.
        if node.left is not nil:
            assert node.left.key < node.key, "left child out of order"
        if node.right is not nil:
            assert node.key < node.right.key, "right child out of order"
        # Rule 4: a red node has no red child.
        if node.color is Color.RED:
            assert node.left.color is Color.BLACK
            assert node.right.color is Color.BLACK
        # Rule 5: equal black-height on both sides.
        left_bh = black_height(node.left)
        right_bh = black_height(node.right)
        assert left_bh == right_bh, "black-height mismatch"
        return left_bh + (1 if node.color is Color.BLACK else 0)

    def inorder(node):
        if node is nil:
            return
        inorder(node.left)
        keys.append(node.key)
        inorder(node.right)

    bh = black_height(tree._root)
    inorder(tree._root)

    assert keys == sorted(expected_keys), "contents / BST order wrong"
    assert list(tree) == sorted(expected_keys), "__iter__ must be ascending"
    assert len(tree) == len(expected_keys), "__len__ out of sync"
    assert bool(tree) is (len(expected_keys) > 0)
    return bh


def test_empty_tree():
    tree = RedBlackTree()
    assert len(tree) == 0
    assert not tree
    assert list(tree) == []
    assert 5 not in tree
    assert_rb_invariants(tree, set())


def test_single_insert_and_erase():
    tree = RedBlackTree()
    tree.insert(42)
    assert 42 in tree and len(tree) == 1
    assert_rb_invariants(tree, {42})
    tree.erase(42)
    assert 42 not in tree
    assert_rb_invariants(tree, set())
    assert tree._root is tree._nil


def test_insert_is_a_set_no_duplicates():
    tree = RedBlackTree()
    for _ in range(3):
        tree.insert(7)
    assert len(tree) == 1
    assert_rb_invariants(tree, {7})


def test_erase_absent_key_is_noop():
    tree = RedBlackTree([1, 2, 3])
    tree.erase(99)
    tree.erase(99)  # idempotent
    assert_rb_invariants(tree, {1, 2, 3})


def test_contains():
    tree = RedBlackTree([10, 20, 30])
    assert 20 in tree
    assert 25 not in tree


def test_constructor_from_iterable_dedups_and_sorts():
    tree = RedBlackTree([5, 3, 8, 1, 4, 3, 5])
    assert list(tree) == [1, 3, 4, 5, 8]
    assert len(tree) == 5


def test_repr_roundtrips_sorted():
    tree = RedBlackTree([3, 1, 2])
    assert repr(tree) == "RedBlackTree([1, 2, 3])"


def test_ascending_inserts_stay_balanced():
    tree = RedBlackTree()
    for value in range(1, 33):
        tree.insert(value)
    assert_rb_invariants(tree, set(range(1, 33)))


def test_descending_inserts_stay_balanced():
    tree = RedBlackTree()
    for value in range(32, 0, -1):
        tree.insert(value)
    assert_rb_invariants(tree, set(range(1, 33)))


def test_generic_over_str_and_float():
    words = RedBlackTree(["pear", "apple", "fig", "cherry"])
    assert list(words) == ["apple", "cherry", "fig", "pear"]
    assert "fig" in words

    floats = RedBlackTree([3.5, 1.1, 2.2, 1.1])
    assert list(floats) == [1.1, 2.2, 3.5]


@pytest.mark.parametrize("seed", range(30))
def test_randomized_mixed_operations_hold_invariants(seed):
    rng = random.Random(seed)
    tree = RedBlackTree()
    present = set()
    for _ in range(120):
        if present and rng.random() < 0.45:
            value = rng.choice(list(present))
            tree.erase(value)
            present.discard(value)
        else:
            value = rng.randint(1, 60)
            tree.insert(value)
            present.add(value)
        assert_rb_invariants(tree, present)


@pytest.mark.parametrize("seed", range(30))
def test_randomized_delete_everything_empties_tree(seed):
    rng = random.Random(seed)
    values = rng.sample(range(1, 200), rng.randint(1, 60))
    tree = RedBlackTree(values)
    present = set(values)
    assert_rb_invariants(tree, present)

    order = list(present)
    rng.shuffle(order)
    for value in order:
        tree.erase(value)
        present.discard(value)
        assert_rb_invariants(tree, present)
    assert tree._root is tree._nil
