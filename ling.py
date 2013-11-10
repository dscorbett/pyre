class Feature(object):
    """A node in a feature hierarchy.

    A feature hierarchy is a directed acyclic graph where nodes have
    associated values.

    Parameters:
        name: A string naming the feature.
        arity (optional): The number of possible values a word may have
            which uses this feature.

    Attributes:
        name: The feature's name.
        arity: The feature's arity.
        children: A set of features.
    """
    def __init__(self, name, arity=1):
        self.name = name
        self.arity = arity
        self.children = set()

    def add_child(self, child):
        """Adds a child feature.

        Parameters:
            child: A feature.

        Raises:
            RuntimeError: The child feature is already an ancestor of
                this feature.
        """
        if child.is_ancestor(self):
            raise RuntimeError('[%s] cannot have child [%s]' %
                               (self.name, child.name))
        self.children.add(child)

    def is_ancestor(self, other):
        """Checks whether a feature is another's ancestor.

        A feature is an ancestor of itself, its children, and all of its
        children's descendants.

        Parameters:
            other: A feature.

        Returns:
            True if this feature is an ancestor of the other feature;
            False otherwise.
        """
        if self == other:
            return True
        for child in self.children:
            if child.is_ancestor(other):
                return True
        return False


class Word(object):
    """An instantiation of a feature with a value.

    Parameters:
        feature: A feature.
        value (optional): A natural number.

    Attributes:
        feature: The feature.
        value: The value of the feature.
        children: A list of words. The order of any two children matters
            if and only if one's feature is an ancestor of the other's.

    Raises:
        RuntimeError: The value is not between 0 (inclusive) and the
            feature's arity (exclusive).
    """
    def __init__(self, feature, value=0):
        if value >= feature.arity:
            raise RuntimeError('invalid value for [%s]: %d' %
                               (feature.name, value))
        self.value = value
        self.feature = feature
        self.children = []

    def __str__(self):
        return ('[%s:%d]%s' %
                (self.feature.name, self.value,
                 ''.join(('\n%s' % str(child)) for child in self.children)
                 .replace('\n', '\n  ')))

    def add_child(self, child):
        """Adds a child word.

        Parameters:
            child: A word.

        Raises:
            RuntimeError: The word cannot be a child because it violates
                the feature hierarchy.
        """
        if child.feature not in self.feature.children:
            raise RuntimeError('[%s] cannot have child [%s]' %
                               (self.feature.name, child.feature.name))
        self.children.append(child)


def sound_change(func):
    """Applies a sound change to a word and to its descendants.

    Parameters:
        func: A function from words to lists of words.

    Returns:
        A function which returns a list of words derived from the input
        word by applying the given function on each descendant word once.
    """
    def apply_change(word):
        new_words = []
        new_words.extend(func(word))
        for i in xrange(len(word.children)):
            for new_child in sound_change(func)(word.children[i]):
                new_word = Word(word.feature, word.value)
                new_word.children = list(word.children)
                new_word.children[i] = new_child
                new_words.append(new_word)
        return new_words
    return apply_change


@sound_change
def apply_elision(word):
    """Deletes association lines.

    Parameters:
        word: A word.

    Returns:
        A list of words each of which differs from the input word in
        that one association line has been removed.
    """
    new_words = []
    for child in word.children:
        new_word = Word(word.feature, word.value)
        new_word.children = list(word.children)
        new_word.children.remove(child)
        new_words.append(new_word)
    return new_words


@sound_change
def mutate(word):
    """Changes the values of words.

    Parameters:
        word: A word.

    Returns:
        A list of words each of which differs from the input word in
        that one word has had its value changed.
    """
    new_words = []
    for i in xrange(word.feature.arity):
        if i != word.value:
            new_word = Word(word.feature, i)
            new_word.children = list(word.children)
            new_words.append(new_word)
    return new_words


@sound_change
def epenthesize(word):
    """Adds association lines to new words.

    Parameters:
        word: A word.

    Returns:
        A list of words each of which differs from the input word in
        that one association line has been added to a new word with an
        appropriate value.
    """
    new_words = []
    for feature in word.feature.children:
        for value in xrange(feature.arity):
            for i in xrange(len(word.children) + 1):
                new_word = Word(word.feature, word.value)
                new_word.children = list(word.children)
                new_word.children.insert(i, Word(feature, value))
                new_words.append(new_word)
    return new_words


@sound_change
def metathesize(word):
    """Swaps association lines.

    Parameters:
        word: A word.

    Returns:
        A list of words each of which differs from the input word in
        that two association lines from the same parent word have been
        swapped. Swapped child words' features must be ordered.
    """
    new_words = []
    for i in xrange(len(word.children)):
        for j in xrange(i + 1, len(word.children)):
            if (word.children[i].feature.is_ancestor(word.children[j].feature)
                or (word.children[j].feature
                    .is_ancestor(word.children[i].feature))):
                new_word = Word(word.feature, word.value)
                new_word.children = list(word.children)
                new_word.children[i], new_word.children[j] = (new_word
                                                              .children[j],
                                                              new_word
                                                              .children[i])
                new_words.append(new_word)
    return new_words


# Testing
syllable = Feature("syllable")
segment = Feature("segment", 2)
syllable.add_child(segment)
place = Feature("place")
segment.add_child(place)
labial = Feature("labial")
place.add_child(labial)
nasal = Feature("nasal", 2)
segment.add_child(nasal)

syl1 = Word(syllable)
seg1 = Word(segment, 0)
seg2 = Word(segment, 1)
syl1.add_child(seg1)
syl1.add_child(seg2)
poa1 = Word(place)
poa2 = Word(place)
seg1.add_child(poa1)
seg2.add_child(poa2)
lab1 = Word(labial)
poa1.add_child(lab1)
nas1 = Word(nasal, 0)
nas2 = Word(nasal, 1)
seg1.add_child(nas1)
seg2.add_child(nas2)
