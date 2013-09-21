from collections import namedtuple
from operator import itemgetter

Node = namedtuple("Node", "value, left, right, red")

NULL = Node(None, None, None, False)


def find(node, value, key):
    """
    Find a value in a node, using a key function.
    """

    while node is not NULL:
        direction = cmp(key(value), key(node.value))
        if direction < 0:
            node = node.left
        elif direction > 0:
            node = node.right
        elif direction == 0:
            return node.value


def rotate_left(node):
    """
    Rotate the node to the left.
    """

    right = node.right
    new = node._replace(right=node.right.left, red=True)
    top = right._replace(left=new, red=node.red)
    return top


def rotate_right(node):
    """
    Rotate the node to the right.
    """

    left = node.left
    new = node._replace(left=node.left.right, red=True)
    top = left._replace(right=new, red=node.red)
    return top


def flip(node):
    """
    Flip colors of a node and its children.
    """

    left = node.left._replace(red=not node.left.red)
    right = node.right._replace(red=not node.right.red)
    top = node._replace(left=left, right=right, red=not node.red)
    return top


def balance(node):
    """
    Balance a node.

    The balance is inductive and relies on all subtrees being balanced
    recursively or by construction.
    """

    # Always lean left with red nodes.
    if node.right.red:
        node = rotate_left(node)

    # Never permit red nodes to have red children. Note that if the left-hand
    # node is NULL, it will short-circuit and fail this test, so we don't have
    # to worry about a dereference here.
    if node.left.red and node.left.left.red:
        node = rotate_right(node)

    # Finally, move red children on both sides up to the next level, reducing
    # the total redness.
    if node.left.red and node.right.red:
        node = flip(node)

    return node


def insert(node, value, key):
    """
    Insert a value into a tree rooted at the given node.

    Balances the tree during insertion.

    An update is performed instead of an insertion if a value in the tree
    compares equal to the new value.
    """

    # Base case: Insertion into the empty tree is just creating a new node
    # with no children.
    if node is NULL:
        return Node(value, NULL, NULL, True)

    # Recursive case: Insertion into a non-empty tree is insertion into
    # whichever of the two sides is correctly compared.
    direction = cmp(key(value), key(node.value))
    if direction < 0:
        left = insert(node.left, value, key)
        node = node._replace(left=left)
    elif direction > 0:
        right = insert(node.right, value, key)
        node = node._replace(right=right)
    elif direction == 0:
        # Exact hit on an existing node. In this case, perform an update.
        node = node._replace(value=value)

    # And balance on the way back up.
    return balance(node)


def move_red_left(node):
    """
    Shuffle red to the left of a tree.
    """

    node = flip(node)
    if node.right.left.red:
        node = node._replace(right=rotate_right(node.right))
        node = flip(rotate_left(node))

    return node


def move_red_right(node):
    """
    Shuffle red to the right of a tree.
    """

    node = flip(node)
    if node.left.left.red:
        node = flip(rotate_right(node))

    return node


def delete_min(node):
    """
    Delete the left-most value from a tree.
    """

    # Base case: If there are no nodes lesser than this node, then this is the
    # node to delete.
    if node.left is NULL:
        return NULL, node.value

    # Acquire more reds if necessary to continue the traversal.
    if not node.left.red and not node.left.left.red:
        node = move_red_left(node)

    # Recursive case: Delete the minimum node of all nodes lesser than this
    # node.
    left, value = delete_min(node.left)
    node = node._replace(left=left)

    return balance(node), value


def delete_max(node):
    """
    Delete the right-most value from a tree.
    """

    # Attempt to rotate left-leaning reds to the right.
    if node.left.red:
        node = rotate_right(node)

    # Base case: If there are no nodes greater than this node, then this is
    # the node to delete.
    if node.right is NULL:
        return NULL, node.value

    # Acquire more reds if necessary to continue the traversal.
    if not node.right.red and not node.right.left.red:
        node = move_red_right(node)

    # Recursive case: Delete the maximum node of all nodes greater than this
    # node.
    right, value = delete_max(node.right)
    node = node._replace(right=right)

    return balance(node), value


def delete(node, value, key):
    """
    Delete a value from a tree.
    """

    # Base case: The empty tree cannot possibly have the desired value.
    if node is NULL:
        raise KeyError(value)

    direction = cmp(key(value), key(node.value))

    # Because we lean to the left, the left case stands alone.
    if direction < 0:
        if not node.left.red and not node.left.left.red:
            node = move_red_left(node)
        # Delete towards the left.
        left = delete(node.left, value, key)
        node = node._replace(left=left)
    else:
        # If we currently lean to the left, lean to the right for now.
        if node.left.red:
            node = rotate_right(node)

        # Best case: The node on our right (which we just rotated there) is a
        # red link and also we were just holding the node to delete. In that
        # case, we just rotated NULL into our current node, and the node to
        # the right is the lone matching node to delete.
        if direction == 0 and node.right is NULL:
            return NULL

        # No? Okay. Move more reds to the right so that we can continue to
        # traverse in that direction. At *this* spot, we do have to confirm
        # that node.right is not NULL...
        if not node.right.red and node.right.left and not node.right.left.red:
            node = move_red_right(node)

        if direction > 0:
            # Delete towards the right.
            right = delete(node.right, value, key)
            node = node._replace(right=right)
        else:
            # Annoying case: The current node was the node to delete all
            # along! Use a right-handed minimum deletion. First find the
            # replacement value to rebuild the current node with, then delete
            # the replacement value from the right-side tree. Finally, create
            # the new node with the old value replaced and the replaced value
            # deleted.
            rnode = node.right
            while rnode is not NULL:
                replacement = rnode.value
                rnode = rnode.left

            right = delete_min(node.right)
            node = node._replace(value=replacement, right=right)

    return balance(node)


class BJ(object):
    """
    A red-black tree.

    Blackjacks are iterable ordered collections.
    """

    root = NULL

    def __init__(self, iterable=None, key=None):
        if key is None:
            self._key = lambda v: v
        else:
            self._key = key

        if iterable is not None:
            for item in iterable:
                self.add(item)

    def __contains__(self, value):
        return find(self.root, value, self._key) is not None

    def __len__(self):
        stack = [self.root]
        acc = 0

        while stack:
            node = stack.pop()
            if node is not NULL:
                stack.append(node.left)
                stack.append(node.right)
                acc += 1

        return acc

    def __iter__(self):
        node = self.root
        stack = []

        while stack or node is not NULL:
            if node is not NULL:
                stack.append(node)
                node = node.left
            else:
                node = stack.pop()
                yield node.value
                node = node.right

    def add(self, value):
        self.root = insert(self.root, value, self._key)

    def discard(self, value):
        self.root = delete(self.root, value, self._key)

    def find(self, value):
        return find(self.root, value, self._key)

    def pop_max(self):
        self.root, value = delete_max(self.root)
        return value

    def pop_min(self):
        self.root, value = delete_min(self.root)
        return value


class Deck(object):

    def __init__(self, mapping=None):
        self._bj = BJ(mapping, key=itemgetter(0))

    def __getitem__(self, key):
        return self._bj.find(key)[1]

    def __setitem__(self, key, value):
        self._bj.add((key, value))

    def __delitem__(self, key):
        self._bj.discard(key)

    def iteritems(self):
        return iter(self._bj)

    def iterkeys(self):
        for k, v in self.iteritems():
            yield k

    def itervalues(self):
        for k, v in self.iteritems():
            yield v

    def items(self):
        return list(self.iteritems())

    def keys(self):
        return list(self.iterkeys())

    def values(self):
        return list(self.itervalues())


from unittest import TestCase


class TestTrees(TestCase):

    def test_balance_right(self):
        node = Node(1, NULL, Node(2, NULL, NULL, True), False)
        balanced = Node(2, Node(1, NULL, NULL, True), NULL, False)
        self.assertEqual(balance(node), balanced)

    def test_balance_four(self):
        node = Node(2, Node(1, NULL, NULL, True), Node(3, NULL, NULL, True),
                    False)
        balanced = Node(2, Node(1, NULL, NULL, False),
                        Node(3, NULL, NULL, False), True)
        self.assertEqual(balance(node), balanced)

    def test_balance_left_four(self):
        node = Node(3, Node(2, Node(1, NULL, NULL, True), NULL, True), NULL,
                    False)
        balanced = Node(2, Node(1, NULL, NULL, False),
                        Node(3, NULL, NULL, False), True)
        self.assertEqual(balance(node), balanced)


class TestBlackjack(TestCase):

    def test_len_single(self):
        bj = BJ([1])
        self.assertEqual(1, len(bj))

    def test_len_many(self):
        bj = BJ(range(10))
        self.assertEqual(10, len(bj))

    def test_contains_single(self):
        bj = BJ([1])
        self.assertTrue(1 in bj)

    def test_contains_several(self):
        bj = BJ([1, 2, 3])
        self.assertTrue(1 in bj)
        self.assertTrue(2 in bj)
        self.assertTrue(3 in bj)

    def test_iter_single(self):
        l = [1]
        bj = BJ(l)
        self.assertEqual(list(iter(bj)), l)

    def test_iter_several(self):
        l = range(10)
        bj = BJ(l)
        self.assertEqual(list(iter(bj)), l)

    def test_discard(self):
        bj = BJ([1])
        bj.discard(1)
        self.assertTrue(1 not in bj)

    def test_discard_missing_empty(self):
        bj = BJ()
        self.assertRaises(KeyError, bj.discard, 2)

    def test_discard_missing(self):
        bj = BJ([1])
        self.assertRaises(KeyError, bj.discard, 2)

    def test_hashproof(self):
        """
        Generate around 32MiB of numeric data and insert it into a single
        tree.

        This is a time-sensitive test that should complete in a few seconds
        instead of taking hours.

        See http://bugs.python.org/issue13703#msg150620 for context.
        """

        g = ((x*(2**64 - 1), hash(x*(2**64 - 1))) for x in xrange(1, 1000))
        bj = BJ(g)
