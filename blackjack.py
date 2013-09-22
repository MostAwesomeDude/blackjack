from collections import MutableMapping, MutableSet, namedtuple
from operator import itemgetter

class Node(namedtuple("Node", "value, left, right, red")):
    __slots__ = ()

    def size(self):
        """
        Recursively find size of a tree. Slow.
        """

        if self is NULL:
            return 0
        return 1 + self.left.size() + self.right.size()

    def find(self, value, key):
        """
        Find a value in a node, using a key function.
        """

        while self is not NULL:
            direction = cmp(key(value), key(self.value))
            if direction < 0:
                self = self.left
            elif direction > 0:
                self = self.right
            elif direction == 0:
                return self.value

    def find_prekeyed(self, value, key):
        """
        Find a value in a node, using a key function. The value is already a
        key.
        """

        while self is not NULL:
            direction = cmp(value, key(self.value))
            if direction < 0:
                self = self.left
            elif direction > 0:
                self = self.right
            elif direction == 0:
                return self.value

    def rotate_left(self):
        """
        Rotate the node to the left.
        """

        right = self.right
        new = self._replace(right=self.right.left, red=True)
        top = right._replace(left=new, red=self.red)
        return top

    def rotate_right(self):
        """
        Rotate the node to the right.
        """

        left = self.left
        new = self._replace(left=self.left.right, red=True)
        top = left._replace(right=new, red=self.red)
        return top

    def flip(self):
        """
        Flip colors of a node and its children.
        """

        left = self.left._replace(red=not self.left.red)
        right = self.right._replace(red=not self.right.red)
        top = self._replace(left=left, right=right, red=not self.red)
        return top

    def balance(self):
        """
        Balance a node.

        The balance is inductive and relies on all subtrees being balanced
        recursively or by construction. If the subtrees are not balanced, then
        this will not fix them.
        """

        # Always lean left with red nodes.
        if self.right.red:
            self = self.rotate_left()

        # Never permit red nodes to have red children. Note that if the left-hand
        # node is NULL, it will short-circuit and fail this test, so we don't have
        # to worry about a dereference here.
        if self.left.red and self.left.left.red:
            self = self.rotate_right()

        # Finally, move red children on both sides up to the next level, reducing
        # the total redness.
        if self.left.red and self.right.red:
            self = self.flip()

        return self

    def insert(self, value, key):
        """
        Insert a value into a tree rooted at the given node, and return
        whether this was an insertion or update.

        Balances the tree during insertion.

        An update is performed instead of an insertion if a value in the tree
        compares equal to the new value.
        """

        # Base case: Insertion into the empty tree is just creating a new node
        # with no children.
        if self is NULL:
            return Node(value, NULL, NULL, True), True

        # Recursive case: Insertion into a non-empty tree is insertion into
        # whichever of the two sides is correctly compared.
        direction = cmp(key(value), key(self.value))
        if direction < 0:
            left, insertion = self.left.insert(value, key)
            self = self._replace(left=left)
        elif direction > 0:
            right, insertion = self.right.insert(value, key)
            self = self._replace(right=right)
        elif direction == 0:
            # Exact hit on an existing node (this node, in fact). In this
            # case, perform an update.
            self = self._replace(value=value)
            insertion = False

        # And balance on the way back up.
        return self.balance(), insertion

    def move_red_left(self):
        """
        Shuffle red to the left of a tree.
        """

        self = self.flip()
        if self.right is not NULL and self.right.left.red:
            self = self._replace(right=self.right.rotate_right())
            self = self.rotate_left().flip()

        return self

    def move_red_right(self):
        """
        Shuffle red to the right of a tree.
        """

        self = self.flip()
        if self.left is not NULL and self.left.left.red:
            self = self.rotate_right().flip()

        return self

    def delete_min(self):
        """
        Delete the left-most value from a tree.
        """

        # Base case: If there are no nodes lesser than this node, then this is the
        # node to delete.
        if self.left is NULL:
            return NULL, self.value

        # Acquire more reds if necessary to continue the traversal. The
        # double-deep check is fine because NULL is red.
        if not self.left.red and not self.left.left.red:
            self = self.move_red_left()

        # Recursive case: Delete the minimum node of all nodes lesser than this
        # node.
        left, value = self.left.delete_min()
        self = self._replace(left=left)

        return self.balance(), value

    def delete_max(self):
        """
        Delete the right-most value from a tree.
        """

        # Attempt to rotate left-leaning reds to the right.
        if self.left.red:
            self = self.rotate_right()

        # Base case: If there are no selfs greater than this self, then this is
        # the self to delete.
        if self.right is NULL:
            return NULL, self.value

        # Acquire more reds if necessary to continue the traversal. NULL is
        # red so this check doesn't need to check for NULL.
        if not self.right.red and not self.right.left.red:
            self = self.move_red_right()

        # Recursive case: Delete the maximum self of all selfs greater than this
        # self.
        right, value = self.right.delete_max()
        self = self._replace(right=right)

        return self.balance(), value

    def delete(self, value, key):
        """
        Delete a value from a tree.
        """

        # Base case: The empty tree cannot possibly have the desired value.
        if self is NULL:
            raise KeyError(value)

        direction = cmp(key(value), key(self.value))

        # Because we lean to the left, the left case stands alone.
        if direction < 0:
            if (not self.left.red and
                self.left is not NULL and
                not self.left.left.red):
                self = self.move_red_left()
            # Delete towards the left.
            left = self.left.delete(value, key)
            self = self._replace(left=left)
        else:
            # If we currently lean to the left, lean to the right for now.
            if self.left.red:
                self = self.rotate_right()

            # Best case: The node on our right (which we just rotated there) is a
            # red link and also we were just holding the node to delete. In that
            # case, we just rotated NULL into our current node, and the node to
            # the right is the lone matching node to delete.
            if direction == 0 and self.right is NULL:
                return NULL

            # No? Okay. Move more reds to the right so that we can continue to
            # traverse in that direction. At *this* spot, we do have to confirm
            # that node.right is not NULL...
            if (not self.right.red and
                self.right is not NULL and
                not self.right.left.red):
                self = self.move_red_right()

            if direction > 0:
                # Delete towards the right.
                right = self.right.delete(value, key)
                self = self._replace(right=right)
            else:
                # Annoying case: The current node was the node to delete all
                # along! Use a right-handed minimum deletion. First find the
                # replacement value to rebuild the current node with, then delete
                # the replacement value from the right-side tree. Finally, create
                # the new node with the old value replaced and the replaced value
                # deleted.
                rnode = self.right
                while rnode is not NULL:
                    rnode = rnode.left

                right, replacement = self.right.delete_min()
                self = self._replace(value=replacement, right=right)

        return self.balance()


NULL = Node(None, None, None, False)


class BJ(MutableSet):
    """
    A red-black tree.

    Blackjacks are based on traditional self-balancing tree theory, and have
    logarithmic time and space bounds on all mutations in the worst case, and
    linear bounds on iteration.

    Blackjacks are mutable sets. See ``collections.MutableSet`` for a precise
    definition of what this class is capable of.

    Iteration on blackjacks is always ordered according to the key function
    used to create the blackjack.

    In addition to the standard methods, blackjacks can also pop their minimum
    and maximum values easily, and the ``find()`` method can retrieve the
    stored value for a key value.
    """

    root = NULL
    _len = 0

    def __init__(self, iterable=None, key=None):
        if key is None:
            self._key = lambda v: v
        else:
            self._key = key

        if iterable is not None:
            for item in iterable:
                self.add(item)

    def __repr__(self):
        return "BJ([%s])" % ", ".join(repr(i) for i in self)

    def __contains__(self, value):
        return self.root.find(value, self._key) is not None

    def __len__(self):
        return self._len

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
        self.root, insertion = self.root.insert(value, self._key)
        self._len += insertion

    def discard(self, value):
        self.root = self.root.delete(value, self._key)
        self._len -= 1

    def find(self, value):
        """
        Find the actual stored value for a given key value.
        """

        return self.root.find(value, self._key)

    def pop_max(self):
        """
        Remove the maximum value and return it.
        """

        if self.root is NULL:
            raise KeyError("pop from an empty blackjack")

        self.root, value = self.root.delete_max()
        self._len -= 1
        return value

    def pop_min(self):
        """
        Remove the minimum value and return it.
        """

        if self.root is NULL:
            raise KeyError("pop from an empty blackjack")

        self.root, value = self.root.delete_min()
        self._len -= 1
        return value


class Deck(MutableMapping):
    """
    A mutable mapping based on a blackjack.

    Like blackjacks, decks are powered by red-black trees and have the same
    bounds on operations.
    """

    def __init__(self, mapping=None):
        self._bj = BJ(mapping, key=itemgetter(0))

    def __repr__(self):
        return "Deck({%s})" % ", ".join("%r: %r" % i for i in self.iteritems())

    def __len__(self):
        return len(self._bj)

    def __iter__(self):
        return self.iterkeys()

    def __getitem__(self, key):
        # Messy.
        value = self._bj.root.find_prekeyed(key, self._bj._key)
        if value is None:
            raise KeyError(key)
        return value[1]

    def __setitem__(self, key, value):
        self._bj.add((key, value))

    def __delitem__(self, key):
        # Blah. Just do it.
        value = self[key]
        self._bj.discard((key, value))

    def iteritems(self):
        return iter(self._bj)

    def iterkeys(self):
        for k, v in self.iteritems():
            yield k

    def itervalues(self):
        for k, v in self.iteritems():
            yield v


from unittest import TestCase


class TestTrees(TestCase):

    def test_balance_right(self):
        node = Node(1, NULL, Node(2, NULL, NULL, True), False)
        balanced = Node(2, Node(1, NULL, NULL, True), NULL, False)
        self.assertEqual(node.balance(), balanced)

    def test_balance_four(self):
        node = Node(2, Node(1, NULL, NULL, True), Node(3, NULL, NULL, True),
                    False)
        balanced = Node(2, Node(1, NULL, NULL, False),
                        Node(3, NULL, NULL, False), True)
        self.assertEqual(node.balance(), balanced)

    def test_balance_left_four(self):
        node = Node(3, Node(2, Node(1, NULL, NULL, True), NULL, True), NULL,
                    False)
        balanced = Node(2, Node(1, NULL, NULL, False),
                        Node(3, NULL, NULL, False), True)
        self.assertEqual(node.balance(), balanced)


class TestBlackjack(TestCase):

    def test_len_single(self):
        bj = BJ([1])
        self.assertEqual(1, len(bj))

    def test_len_many(self):
        bj = BJ(range(10))
        self.assertEqual(10, len(bj))

    def test_len_many_duplicate(self):
        bj = BJ(range(10))
        bj.add(0)
        bj.add(5)
        bj.add(9)
        self.assertEqual(10, len(bj))

    def test_len_after_discard(self):
        bj = BJ(range(10))
        bj.discard(0)
        self.assertEqual(9, len(bj))

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

        g = ((x*(2**64 - 1), hash(x*(2**64 - 1))) for x in xrange(1, 10000))
        bj = BJ(g)


class TestDeck(TestCase):

    def test_get_set_single(self):
        d = Deck()
        d["test"] = "value"
        self.assertEqual(d["test"], "value")

    def test_get_set_several(self):
        d = Deck()
        d["first"] = "second"
        d["third"] = "fourth"
        d["fifth"] = "sixth"
        self.assertEqual(d["first"], "second")
        self.assertEqual(d["third"], "fourth")
        self.assertEqual(d["fifth"], "sixth")
