#! /usr/bin/env python

"""
A Feature has:
    values set(String) :
        the set of legal values of this feature
A Feature implements:
    add(value String) :
        Add the given value to the set of legal values.
    update(values set(String)) :
        Add the given values to the set of legal values.
    contains(value String) :
        Return whether the given value is legal for this feature.
    discard(value String) :
        Remove the given value, if boolean.
    clear() :
        Remove all values.

A Constrant has:
    boolean1 Boolean
    feature1 String
    value1 String
    boolean2 Boolean
    feature2 String
    value2 String

A ConstraintSet has:
    constraints set(Constraint) :
        the set of constraints, each of which rebooleans an implication of the
        form "The <absence/presence> of <value> in <feature> implies the
        <absence/presence> of <value> in <feature>", where the first feature is
        comes before the second when sorted alphabetically
A ConstraintSet implements:
    overwrite(constraint Constraint) :
        Add the given constraint to the set, overwriting the original in case
        of conflict.
    add(constraint Constraint) :
        Add the given constraint to the set, raising an error in case of
        conflict.
    discard(constraint Constraint) :
        Discard the given constraint, without raising an error if it is not
        present.
"""

class Feature:
    def __init__(self, values=set()):
        self._values = set(values)

    def __eq__(self, other):
        return isinstance(other, Feature) and self._values == other._values
    
    def __hash__(self):
        return hash(frozenset(self._values))

    def __repr__(self):
        return 'Feature(%s)' % self._values

    def add(self, value):
        self._values.add(value)
        return self

    def update(self, values):
        self._values.update(values)
        return self

    def contains(self, value):
        return value in self._values

    def discard(self, value):
        self._values.discard(value)
        return self

    def clear(self):
        self._values.clear()
        return self

class FeatureSet:
    def __init__(self, features={}):
        self._features = dict(features)

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError('key must be a string')
        return self._features[key]

    def contains(self, feature):
        return feature in self._features

    def update(self, key, value):
        self._features.update({key: value})

features = FeatureSet()

class Constraint:
    def __init__(self, feature1, value1, feature2, value2, boolean1=True,
                 boolean2=True, featureset=features):
        if not featureset.contains(feature1):
            raise KeyError('no feature [%s] found' % feature1)
        if not featureset.contains(feature2):
            raise KeyError('no feature [%s] found' % feature2)
        if feature1 == feature2:
            raise StandardError('a feature cannot imply itself')
        if not featureset[feature1].contains(value1):
            raise KeyError('[%s] is not a value in [%s]' %
                                (value1, feature1))
        if not featureset[feature2].contains(value2):
            raise KeyError('[%s] is not a value in [%s]' %
                                (value2, feature2))
        self.features = featureset
        if feature2 < feature1:
            self.boolean1 = not boolean2
            self.feature1 = feature2
            self.value1 = value2
            self.boolean2 = not boolean1
            self.feature2 = feature1
            self.value2 = value1
        else:
            self.boolean1 = boolean1
            self.feature1 = feature1
            self.value1 = value1
            self.boolean2 = boolean2
            self.feature2 = feature2
            self.value2 = value2

    def __str__(self):
        if self.boolean1: s = ''
        else: s = '!'
        s = '%s%s::%s => ' % (s, self.feature1, self.value1)
        if not self.boolean2: s = '%s!' % s
        s = '%s%s::%s' % (s, self.feature2, self.value2)
        return s

    def __eq__(self, other):
        return (isinstance(other, Constraint) and
                self.boolean1 == other.boolean1 and
                self.boolean2 == other.boolean2 and
                self.feature1 == other.feature1 and
                self.feature2 == other.feature2 and
                self.value1 == other.value1 and
                self.value2 == other.value2)

    def __hash__(self):
        return (hash(self.boolean1) ^ hash(self.feature1) ^ hash(self.value1) ^
                hash(self.boolean2) ^ hash(self.feature2) ^ hash(self.value2))  

class ConstraintSet:
    def __init__(self, constraints=set()):
        self._features = features
        self._constraints = constraints

    def __str__(self):
        return '[\n%s\n]' % '\n'.join(['%s' % c for c in self._constraints])

    def overwrite(self, constraint):
        return self.add(constraint, raise_error=False)

    def add(self, constraint, raise_error=True):
        for c in self._constraints.copy():
            if ((c.feature1 == constraint.feature1) and
                (c.feature2 == constraint.feature2) and
                (c.value1 == constraint.value1) and
                (c.value2 == constraint.value2)):
                if raise_error and ((c.boolean1 == constraint.boolean1) ^
                                    (c.boolean2 == constraint.boolean2)):
                    raise StandardError('%s violates %s' % (c, constraint))
                self.discard(c)
                break
        self._constraints.add(constraint)
        return self

    def discard(self, constraint):
        self._constraints.discard(constraint)

constraints = ConstraintSet()
