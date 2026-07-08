"""
1. Every node is either black or red.
2. The root is always black.
3. Every `None` (leaf) node is black.
4. Red nodes cannot be adjacent.
5. Every path from a node to a leaf must contain the same number of black nodes.
"""


class Node:
    def __init__(self, key: int, parent: Node | None = None) -> None:
        self.key = key
        # False - Red, True - Black
        self.color = False
        self.parent: Node | None = parent
        self.left: Node | None = None
        self.right: Node | None = None

class RedBlackTree:
    def __init__(self):
        self._root: Node = None

    def _insert(self, cur_node: Node | None, parent: Node | None, new_node: Node) -> Node:
        if cur_node is None:
            cur_node = new_node
            cur_node.parent = parent
            return cur_node
        if cur_node.key < new_node.key:
            cur_node.right = self._insert(cur_node.right, cur_node, new_node)
        elif cur_node.key > new_node.key:
            cur_node.left = self._insert(cur_node.left, cur_node, new_node)
        return cur_node

    def _find(self, cur_node: Node | None, val: int) -> bool:
        if cur_node is None:
            return None
        if cur_node.key == val:
            return cur_node
        if cur_node.key < val:
            return self._find(cur_node.right, val)
        else:
            return self._find(cur_node.left, val)

    def _right_rotate(self, node: Node) -> None:
        assert node.left is not None
        left_child = node.left
        parent = node.parent
        moved_subtree = left_child.right
        left_child.parent = parent

        if parent is not None:
            if parent.left is node:
                parent.left = left_child
            else:
                parent.right = left_child
        else:
            self._root = left_child
        
        node.parent = left_child
        node.left = moved_subtree
        if moved_subtree is not None:
            moved_subtree.parent = node
        left_child.right = node
    
    def _left_rotate(self, node: Node) -> None:
        assert node.right is not None
        right_child = node.right
        parent = node.parent
        moved_subtree = right_child.left
        right_child.parent = parent

        if parent is not None:
            if parent.left is node:
                parent.left = right_child
            else:
                parent.right = right_child
        else:
            self._root = right_child

        node.parent = right_child
        node.right = moved_subtree
        if moved_subtree is not None:
            moved_subtree.parent = node
        right_child.left = node
        
    def _balance_tree(self, node: Node) -> None:
        if node.parent is None:
            node.color = True
            return
        
        if node.parent.color:
            return
        grand_parent = node.parent.parent
        parent = node.parent
        uncle = grand_parent.right if grand_parent.left is parent else grand_parent.left
        
        if uncle is not None and not uncle.color:
            parent.color = True
            uncle.color = True
            grand_parent.color = False
            self._balance_tree(grand_parent)
        else:
            if grand_parent.left is parent and parent.right is node:
                self._left_rotate(parent)
                parent, node = node, parent
            elif grand_parent.right is parent and parent.left is node:
                self._right_rotate(parent)
                parent, node = node, parent

            if grand_parent.left is parent:
                self._right_rotate(grand_parent)
            elif grand_parent.right is parent:
                self._left_rotate(grand_parent)
            
            parent.color = True
            grand_parent.color = False

    def insert(self, val: int) -> None:
        node = self._find(self._root, val)
        if node is None:
            new_node = Node(val)
            self._root = self._insert(self._root, None, new_node)
            self._balance_tree(new_node)
            self._root.color = True

    def erase(self, val: int) -> None:
        node = self._find(self._root, val)
        if node is None:
            return

        to_delete = node
        if node.right is not None:
            cur_leftest = node.right
            while cur_leftest is not None:
                to_delete = cur_leftest
                cur_leftest = cur_leftest.left
        elif node.left is not None:
            cur_rightest = node.left
            while cur_rightest is not None:
                to_delete = cur_rightest
                cur_rightest = cur_rightest.right
        
        node.key = to_delete.key

        to_delete_parent = to_delete.parent

        if to_delete.right is not None or to_delete.left is not None:
            replacement_node = to_delete.right or to_delete.left
            if to_delete_parent.left is to_delete:
                to_delete_parent.left = replacement_node
            else:
                to_delete_parent.right = replacement_node
            replacement_node.parent = to_delete_parent
            
            if not to_delete.color:
                return

            if not replacement_node.color:
                replacement_node.color = True
                return
            
            to_delete = replacement_node
        else:
            if not to_delete.color:
                to_delete = None

        # TODO Fix-up aka resolve double-black problem
        
        



        
        

