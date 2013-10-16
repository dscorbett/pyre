class Tier:
    def __init__(self, arity):
        self.arity = arity
        self.children = set()

    def add_child(self, child):
        if child.is_ancestor(self):
            raise RuntimeError
        self.children.add(child)

    def is_ancestor(self, other):
        if self is other:
            return True
        for child in self.children:
            if child.is_ancestor(other):
                return True
        return False


class Hierarchy:
    def __init__(self):
        self.tiers = {}

    def __getitem__(self, tier_name):
        return self.tiers[tier_name]

    def add_tier(self, name, arity=1):
        self.tiers[name] = Tier(arity)

    def connect_tiers(self, parent_name, child_name):
        try:
            self.tiers[parent_name].add_child(self.tiers[child_name])
        except RuntimeError:
            raise RuntimeError('%s is already a descendant of %s' %
                               (parent_name, child_name))

    def is_child(self, parent_name, child_name):
        return self.tiers[child_name] in self.tiers[parent_name].children


class Node:
    def __init__(self, tier_name, value, parents=[], children=[], older=None,
                 younger=None):
        self.tier_name = tier_name
        self.value = value
        self.parents = parents
        self.children = children
        self.older = older
        self.younger = younger

    def get_relative(self, tier_name, get_descendent, reverse):
        rel = 'children' if get_descendent else 'parents'
        for node in (reversed if reverse else iter)(self.__dict__[rel]):
            if node.tier_name == tier_name:
                return node
            if node.__dict__[rel]:
                return node.get_youngest_descendent(tier_name)
        return None


class Graph:
    def __init__(self, hierarchy):
        self.hierarchy = hierarchy
        self.graph = set()

    def add_node(self, tier_name, parents=None, children=None, value=0):
        tier = self.hierarchy[tier_name]
        if parents is None:
            parents = []
        if children is None:
            children = []
        for parent in parents:
            if not self.hierarchy.is_child(parent.tier_name, tier_name):
                raise RuntimeError('[%s] is not a parent of [%s]' %
                                   (parent.tier_name, tier_name))
        for child in children:
            if not self.hierarchy.is_child(tier_name, child.tier_name):
                raise RuntimeError('[%s] is not a child of [%s]' %
                                   (child.tier_name, tier_name))
        # TODO: what if there are no parents/children?
        p_older, p_younger = self.find_siblings(tier_name, parents, True)
        c_older, c_younger = self.find_siblings(tier_name, children, False)
        if p_older is not c_older and p_younger is not c_younger:
            raise RuntimeError('Parents and children disagree on siblings')
        # TODO: make sure all parents/children are siblings
        node = Node(tier_name, value, parents, children, p_older, p_younger)
        if parents:
            for parent in parents[:-1]:
                parent.children.append(node)
            parents[-1].children.insert(0, node)
        if children:
            for child in children[:-1]:
                child.parents.append(node)
            children[-1].parents.insert(0, node)
        self.graph.add(node)
        return node

    def find_siblings(self, tier_name, relatives, get_descendent):
        older = None
        younger = None
        if relatives:
            older = relatives[0].get_relative(tier_name, get_descendent, True)
            younger = relatives[-1].get_relative(tier_name, get_descendent,
                                                 False)
        return older, younger

    def add_node_with_sibling(self, tier_name, add_after, sibling,
                              share_parents, share_children, value=0):
        if tier_name != sibling.tier_name:
            raise RuntimeError('[%s] cannot be a sibling of [%s]' %
                               (tier_name, sibling.tier_name))
        kwargs = {'older' if add_after else 'younger': sibling}
        node = Node(tier_name, value, **kwargs)
        if share_parents and sibling.parents:
            parent = sibling.parents[-1 if add_after else 0]
            node.parents = [parent]
            if add_after:
                parent.children.append(node)
            else:
                parent.children.insert(0, node)
        if share_children and sibling.children:
            child = sibling.children[-1 if add_after else 0]
            node.children = [child]
            if add_after:
                child.parents.append(node)
            else:
                child.parents.insert(0, node)
        self.make_sibling(sibling, node, add_after)
        self.graph.add(node)
        return node

    def make_sibling(self, base, new_node, add_after):
        if add_after:
            if base.younger:
                base.younger.older = new_node
            base.younger = new_node
        else:
            if base.older:
                base.older.younger = new_node
            base.older = new_node


h = Hierarchy()
h.add_tier("root", 3)
h.add_tier("nasal", 2)
h.connect_tiers("root", "nasal")
h.add_tier("place")
h.add_tier("labial")
h.connect_tiers("root", "place")
h.connect_tiers("place", "labial")
g = Graph(h)
r1 = g.add_node('root', value=1)
l1 = g.add_node('labial')
l2 = g.add_node('labial')
p1 = g.add_node('place', [r1], [l1, l2])
p2 = g.add_node_with_sibling('place', True, p1, True, False)
g.make_sibling(l1, l2, True)
l3 = g.add_node('labial', [p1, p2])
