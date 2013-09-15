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

    # Finally, fix double-reds by moving the red link up to the next level.
    if node.left.red and node.right.red:
        node = flip(node)

    return node


def insert(node, value, comparator):
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
        return NULL

    # Acquire more reds if necessary to continue the traversal.
    if not node.left.red and not node.left.left.red:
        node = move_red_left(node)

    # Recursive case: Delete the minimum node of all nodes lesser than this
    # node.
    node = node._replace(left=delete_max(node.left))

    return balance(node)


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
        return NULL

    # Acquire more reds if necessary to continue the traversal.
    if not node.right.red and not node.right.left.red:
        node = move_red_right(node)

    # Recursive case: Delete the maximum node of all nodes greater than this
    # node.
    node = node._replace(right=delete_max(node.right))

    return balance(node)


def delete(node, value, comparator):
    """
    Delete a value from a tree.
    """

    direction = comparator(value, node.value)

    # Because we lean to the left, the left case stands alone.
    if direction < 0:
        if not node.left.red and not node.left.left.red:
            node = move_red_left(node)
        # Delete towards the left.
        left = delete(node.left, value, comparator)
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
        # traverse in that direction.
        if not node.right.red and not node.right.left.red:
            node = move_red_right(node)

        if direction > 0:
            # Delete towards the right.
            right = delete(node.right, value, comparator)
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
    """

    root = NULL
