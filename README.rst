=========
Blackjack
=========

Blackjack is a simple implementation of the classic red-black tree as a
standard Python data structure. A set and a dictionary are included::

    >>> from blackjack import BJ, Deck
    >>> bj = BJ()
    >>> bj
    BJ([])
    >>> bj.add(42)
    >>> 42 in bj
    True
    >>> d = Deck()
    >>> d[1] = 2
    >>> d[3] = 4
    >>> d.keys()
    [1, 3]
    >>> d.values()
    [2, 4]

Usage
=====

Blackjacks and decks behave just like normal Python sets and dictionaries, but
have different performance characteristics and different requirements for
keys. All keys must be comparable, but need not be hashable::

    >>> bj = BJ()
    >>> bj.add([1])
    >>> bj.add([1,2])
    >>> bj.add([1,2,3])
    >>> bj
    BJ([[1], [1, 2], [1, 2, 3]])

This does impact heterogeneity somewhat, but shouldn't be a problem for most
common uses. On the other hand, the average and worst-case times for access,
membership testing, insertion, and deletion are all logarithmic, which makes
blackjacks ideal for storing mappings of data with untrusted keys::

    $ python -mtimeit \
    > -s 'l = [(x*(2**64 - 1), hash(x*(2**64 - 1))) for x in xrange(10000)]' \
    > 'dict(l)'
    10 loops, best of 3: 4.11 sec per loop
    $ python -mtimeit \
    -s 'l = [(x*(2**64 - 1), hash(x*(2**64 - 1))) for x in xrange(10000)]
    from blackjack import Deck' \
    'Deck(l)'
    10 loops, best of 3: 2.07 sec per loop

Even on small- to medium-sized sets of data, blackjacks quickly become more
effective than dictionaries in the face of untrusted input.

This package only contains the ``blackjack`` module; tests are in the module
and may be run with any standard test runner::

    $ trial blackjack | tail -n1
    PASSED (successes=17)

Technical information
=====================

The specific trees used are left-leaning red-black trees. Red children are
opportunistically reduced during balancing if nodes will be recreated anyway;
this tends to shorten overall tree height by reducing the number of red
children. Complexities are as follows:

==========  ========== ========
Operation   Time       Space
==========  ========== ========
Lookup      O(log n)   O(1)
Membership  O(log n)   O(1)
Insertion   O(log n)   O(log n)
Deletion    O(log n)   O(log n)
Update      O(log n)   O(log n)
Sort        O(1)       O(1)
Length      O(1)       O(1)
==========  ========== ========

Sorting according to the provided key function is constant because the tree's
traversal order is presorted. Length is recorded and updated on mutation.
Nodes are persistent and altering the tree generally requires a logarithmic
space commitment to create new nodes.
