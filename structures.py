from queue import LifoQueue


class SyntaxTree(object):
    def __init__(self, operators, regex):
        self.operators = operators
        self.symbols = list(set(
            [char for char in regex if char not in operators if char != '(' and char != ')' and char != 'E']))

        if 'E' in regex:
            print(Colors.OKBLUE + "[INFO] " + Colors.ENDC +
                  "Epsilon in string detected. Removing epsilon")
        self.regex = regex.replace('E', '') if 'E' in regex else regex

        self.postfix = ""
        self.root = None

        # transformations to regex
        self.explicit_concat()
        self.to_postfix()
        self.build_tree()
        self.pos = 1

    def get_precedence(self, c):
        try:
            precedence = self.operators[c]
        except:
            precedence = 0

        return precedence

    def explicit_concat(self):
        for i in range(len(self.symbols)):
            if not((self.symbols[i].isalpha() and self.symbols[i].islower()) or self.symbols[i] == '#'):
                raise AssertionError(
                    Colors.FAIL + "[ERROR] " + Colors.ENDC + "Wrong input. Please enter only lowercase letters and try again!")
        new_regex = ""
        for i in range(len(self.regex)):
            new_regex += self.regex[i]
            try:
                if (self.regex[i] in self.symbols and self.regex[i + 1] in self.symbols) \
                        or (self.regex[i] not in ['|', '('] and self.regex[i + 1] in self.symbols + ['(']):
                    new_regex += '.'
            except:
                pass

        self.regex = new_regex

    def to_postfix(self):
        operator_stack = Stack()

        print(Colors.OKBLUE + "[INFO] " +
              Colors.ENDC + "Transforming regex to postfix")
        for char in self.regex:
            if char in self.symbols:
                self.postfix += char

            elif char == '(':
                operator_stack.push(char)

            elif char == ')':
                try:
                    while operator_stack.top() != '(':
                        self.postfix += operator_stack.pop()

                        if operator_stack.is_empty():
                            raise AssertionError(
                                Colors.FAIL + "[ERROR] " + Colors.ENDC + "Syntax error, missing parenthesis in expression")
                            # exit()

                    operator_stack.pop()
                except Exception as error:
                    raise AssertionError(
                        Colors.FAIL + "[ERROR] " + Colors.ENDC + f"Syntax error, missing parenthesis in expression")
                    # exit()

            else:
                while not operator_stack.is_empty():
                    top = operator_stack.top()

                    top_precedence = self.get_precedence(top)
                    char_precedence = self.get_precedence(char)

                    if (top_precedence >= char_precedence):
                        self.postfix += operator_stack.pop()
                    else:
                        break

                operator_stack.push(char)

        while not operator_stack.is_empty():
            self.postfix += operator_stack.pop()

        print(Colors.OKBLUE + "[INFO] " + Colors.ENDC +
              "Regex in postfix notation obtained: " + self.postfix)

    def build_tree(self):
        tree_stack = Stack()

        print(Colors.OKBLUE + "[INFO] " + Colors.ENDC + "Building tree")
        for char in self.postfix:
            if char in self.symbols:
                tree_stack.push(Node(char))
            else:
                if char == '*':
                    if tree_stack.get_size() > 0:
                        right = tree_stack.pop()
                        new = Node(char, right=right)
                        right.parent = new
                        tree_stack.push(new)
                    else:
                        raise AssertionError(
                            Colors.FAIL + "[ERROR] " + Colors.ENDC + "Incomplete " + char + " operation, insufficient parameters")
                        # exit()
                else:
                    if tree_stack.get_size() > 1:
                        right = tree_stack.pop()
                        left = tree_stack.pop()
                        new = Node(char, right=right, left=left)
                        right.parent = new
                        left.parent = new
                        tree_stack.push(new)
                    else:
                        raise AssertionError(
                            Colors.FAIL + "[ERROR] " + Colors.ENDC + "CONCAT or OR operation incomplete, a symbol is missing")
                        # exit()

        self.root = tree_stack.pop()

    def traverse_postorder(self, node, reachable=None, nodes=None):
        if not node:
            return

        if reachable is None:
            reachable = []

        if nodes is None:
            nodes = []

        self.traverse_postorder(node.left, reachable, nodes)
        self.traverse_postorder(node.right, reachable, nodes)

        reachable.append(node.data)
        nodes.append(node)

        if node.data in self.symbols:
            # define pos
            node.pos = self.pos
            self.pos += 1

            # define nullable
            if node.data == 'E':
                node.nullable = True
            else:
                node.nullable = False

            # define first and last pos
            node.firstpos = [node.pos]
            node.lastpos = [node.pos]

            # in case if Epsilon is needed
            # if node.data == 'E':
            #     node.firstpos = []
            #     node.lastpos = []
            #     self.pos -= 1
            # else:
            #     node.firstpos = [node.pos]
            #     node.lastpos = [node.pos]
        else:
            if node.data == '|':
                node.nullable = node.right.nullable or node.left.nullable

                node.firstpos = list(
                    set(node.right.firstpos + node.left.firstpos))
                node.lastpos = list(
                    set(node.right.lastpos + node.left.lastpos))

            elif node.data == '.':
                node.nullable = node.right.nullable and node.left.nullable

                node.firstpos = list(set(node.right.firstpos + node.left.firstpos)
                                     ) if node.left.nullable else node.left.firstpos
                node.lastpos = list(set(node.right.lastpos + node.left.lastpos)
                                    ) if node.right.nullable else node.right.lastpos

            elif node.data == '*':
                node.nullable = True
                node.firstpos = node.right.firstpos
                node.lastpos = node.right.lastpos

            else:
                pass

        return nodes

    def __str__(self):
        if self.root is not None:
            self.print_tree(self.root)

        return ("")

    def print_tree(self, node):
        if node is not None:
            self.print_tree(node.left)
            print(node.data)
            self.print_tree(node.right)


class Node(object):
    def __init__(self, data, parent=None, left=None, right=None):
        self.data = data
        self.left = left
        self.right = right
        self.parent = parent

        self.lastpos = []
        self.firstpos = []
        self.followpos = []
        self.nullable = False
        self.pos = None


class Stack(object):
    def __init__(self):
        self.stack = LifoQueue()

    def push(self, item):
        self.stack.put(item)

    def pop(self):
        if not self.is_empty():
            return self.stack.get()
        else:
            raise Exception('Stack is empty')

    def top(self):
        top = self.pop()
        self.stack.put(top)

        return top

    def get_size(self):
        return self.stack.qsize()

    def is_empty(self):
        return self.stack.empty()


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
