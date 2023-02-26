import json

file = open('data/tree.txt', 'r')
lines = file.readlines()


def parse_line(line):
    dict = {}
    i = 0
    # print(line)
    def parse_key():
        nonlocal i
        # print(i)
        key = ""
        while line[i] != "=":
            key += line[i]
            i = i + 1
        i = i + 1
        return key
    def parse_value():
        nonlocal i
        value = ''
        if line[i] != '"':
            print("Value doesn't started with quote")
        i = i + 1
        while line[i] != '"':
            value += line[i]
            i += 1
        if len(line) > i:
            i += 2
        return value
    while i < len(line):
        key = parse_key()
        dict[key] = parse_value()
    return dict


class TreeNode:
    def __init__(self, condition, set, parent=None):
        self.condition = condition
        self.parent = parent
        self.set = set
        self.left = None
        self.right = None
        self.leaf = False

    def contains(self, set):
        for i in range(len(self.set)):
            if self.set[i] < set[i]:
                return False
        return True

    def add_child(self, child):
        if self.left == None:
            self.left = child
            return False
        elif self.right == None:
            self.right = child
            return True
        else:
            print('Error too many children')
            return True


class TreeLeaf(TreeNode):
    def __init__(self, name, set, parent=None):
        TreeNode.__init__(self, True, set, parent)
        self.name = name
        self.leaf = True


class TreeEncoder(json.JSONEncoder):
    def default(self, object):
        if isinstance(object, TreeLeaf):
            return object.name
        if isinstance(object, TreeNode):
            return {
                'condition': object.condition,
                # 'set': object.set,
                'left': object.left,
                'right': object.right
            }
        return json.JSONEncoder.default(self, object)


def parse_freq(string):
    return list(map(int, string.split(",")))


data = map(parse_line, filter(lambda l: len(l) > 0 and l[0] != '\n',lines) )
current = None
top = None
for entry in data:
    if 'freq' not in entry:
        continue
    set = parse_freq(entry['freq'])
    node = None
    leaf = False
    if 'att' not in entry:
        leaf = True
        node = TreeLeaf(entry['class'], set)
    else:
        node = TreeNode({
            'card': entry['att'],
            'cut': entry['cut']
        }, set)
    if current == None:
        current = node
        top = node
    else:
        while not current.contains(set):
            current = current.parent
            if current == None:
                print('Error run out of parents')
        node.parent = current
        current.add_child(node)
        if not node.leaf:
            current = node
# print(json.dumps(list(data)))
print(json.dumps(top, cls=TreeEncoder))
