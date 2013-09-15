from collections import namedtuple

Node = namedtuple("Node", "value, left, right, red")

NULL = Node(None, None, None, False)


def find(node, value, comparator):
    """
    Find a value in a node, using a custom comparator.
    """

    while node is not NULL:
        direction = comparator(value, node.value)
        if direction < 0:
            node = node.left
        elif direction > 0:
            node = node.right
        elif direction == 0:
            return node.value
        else:
            raise RuntimeError("Comparator returned bad value")


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


def insert(node, value, comparator):
    """
    Insert a value into a tree rooted at the given node.

    Balances the tree during insertion.

    An update is performed instead of an insertion if a value in the tree
    compares equal to the new value.
    """

    # Root case: Insertion into the empty tree is just creating a new node
    # with no children.
    if node is NULL:
        return Node(value, NULL, NULL, True)

    # Fix double-reds early.
    if node.left.red and node.right.red:
        node = flip(node)

    # Recursive case: Insertion into a non-empty tree is insertion into
    # whichever of the two sides is correctly compared.
    direction = comparator(value, node.value)
    if direction < 0:
        left = insert(node.left, value, comparator)
        node = node._replace(left=left)
    elif direction > 0:
        right = insert(node.right, value, comparator)
        node = node._replace(right=right)
    elif direction == 0:
        # Exact hit on an existing node. In this case, perform an update.
        node = node._replace(value=value)
    else:
        raise RuntimeError("Comparator returned bad value")

    # Always lean left with red nodes.
    if node.right.red:
        node = rotate_left(node)

    # Never permit red nodes to have red children.
    # XXX test this case; it might dereference NULL's children?
    if node.left.red and node.left.left.red:
        node = rotate_right(node)

    return node


class BJ(object):
    """
    A red-black tree.
    """

    root = NULL
