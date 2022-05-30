import graphviz
import tempfile
from structures import Colors


class FA(object):
    def __init__(self, symbols, states, tfunc, istate, tstate):
        self.states = states
        self.symbols = symbols
        self.transition_function = tfunc
        self.initial_state = istate
        self.terminal_states = tstate

    def print_automata(self, type, i_state, t_state, states, symbols, t_function, state_mapping=None):
        print(Colors.OKBLUE + "[INFO] " + Colors.ENDC +
              Colors.UNDERLINE + type + Colors.ENDC + " AUTOMATA CREATED WITH")
        print(Colors.OKCYAN + " INITIAL STATE" + Colors.ENDC)
        print(i_state)
        print(Colors.OKCYAN + " TERMINAL STATES" + Colors.ENDC)
        print(t_state)
        print(Colors.OKCYAN + " STATES" + Colors.ENDC)

        for state in states:
            print("     ", state)
        print(Colors.OKCYAN + " SYMBOLS" + Colors.ENDC)
        print(symbols)
        if state_mapping:
            print(Colors.OKCYAN + " STATE MAPPING" + Colors.ENDC)

            for key, value in state_mapping.items():
                print("     ", key, "->", value)
        print(Colors.OKCYAN + " TRANSITIONS" + Colors.ENDC)

        for key, value in t_function.items():
            print("     ", key, "->", value)
        print("")

    def graph_automata(self, mapping=None):
        builder = graphviz.Digraph(graph_attr={'rankdir': 'LR'})

        for x in self.states:
            x = x if not mapping else mapping[tuple(x)]
            if x not in self.terminal_states:
                builder.attr('node', shape='circle')
                builder.node(x)
            else:
                builder.attr('node', shape='doublecircle')
                builder.node(x)

        builder.attr('node', shape='none')
        builder.node('')
        builder.edge('', self.initial_state)

        for key, value in self.transition_function.items():
            if isinstance(value, str):
                builder.edge(key[0], value, label=(key[1]))
            else:
                for val in value:
                    builder.edge(key[0], val, label=(key[1]))

        builder.view(tempfile.mktemp('.gv'), cleanup=True, )

    def isGenerated(self):
        raise Exception("Not Implemented")


class DFA(FA):
    def __init__(self, syntax_tree=None, states=[], tfunc={}, istate=None, tstate=[], nodes=None):
        self.syntax_tree = syntax_tree
        self.nodes = nodes
        self.state_mapping = None

        # remove 'E' from symbols (affects construction)
        syntax_tree and 'E' in syntax_tree.symbols and syntax_tree.symbols.remove(
            'E')

        # instantiate the object
        FA.__init__(
            self,
            symbols=syntax_tree.symbols,
            states=states,
            tfunc=tfunc,
            istate=istate,
            tstate=tstate
        )

    def follow_pos(self):
        self.followpos = {}

        for node in self.nodes:
            if node.pos:
                self.followpos[node.pos] = []

        for node in self.nodes:
            if node.data == '.':
                for i in node.left.lastpos:
                    self.followpos[i] += node.right.firstpos

            if node.data == '*':
                for i in node.lastpos:
                    self.followpos[i] += node.firstpos

    def get_tree_data(self):
        self.follow_pos()
        first = []
        last = []
        # get first
        for node in self.nodes:
            first.append(node.firstpos)
        # get last
        for node in self.nodes:
            last.append(node.lastpos)

        print(Colors.OKBLUE + "[INFO] " + Colors.ENDC + Colors.UNDERLINE +
              'SYNTAX TREE' + Colors.ENDC + " HAS THE FOLLOWING FUNCTIONS:")
        print(Colors.OKCYAN + " FIRST: " + Colors.ENDC + f"{first}")
        print(Colors.OKCYAN + " LAST: " + Colors.ENDC + f"{last}")
        print(Colors.OKCYAN + " FOLLOW: " + Colors.ENDC + f"{self.followpos}")

        final_pos = 0

        for node in self.nodes:
            if node.data == '#':
                final_pos = node.pos

        t_func = {}
        subset_mapping = {}

        dstates_u = [self.syntax_tree.root.firstpos]
        dstates_m = []

        while len(dstates_u) > 0:
            T = dstates_u.pop(0)
            dstates_m.append(T)

            for symbol in self.symbols:
                U = []
                for node in self.nodes:
                    if node.data == symbol and node.pos in T:
                        U += self.followpos[node.pos]
                        U = list(set(U))

                if len(U) > 0:
                    if U not in dstates_u and U not in dstates_m:
                        dstates_u.append(U)

                    list_of_strings = [str(s) for s in T]
                    joined_string = "".join(list_of_strings)
                    subset_mapping[tuple(T)] = joined_string

                    list_of_strings = [str(s) for s in U]
                    joined_string = "".join(list_of_strings)
                    subset_mapping[tuple(U)] = joined_string

                    t_func[(subset_mapping[tuple(T)], symbol)
                           ] = subset_mapping[tuple(U)]

        for state in dstates_m:
            if final_pos in state:
                self.terminal_states.append(subset_mapping[tuple(state)])

        self.initial_state = subset_mapping[tuple(dstates_m[0])]
        self.states = dstates_m
        self.transition_function = t_func
        self.state_mapping = subset_mapping

        self.print_automata("DFA", self.initial_state, self.terminal_states, self.states,
                            self.symbols, self.transition_function, state_mapping=subset_mapping)

    def isGenerated(self, string):

        s = self.initial_state
        terminal = False

        for char in string:
            if char not in self.symbols:
                terminal = None
                raise Exception(Colors.FAIL + "[ERROR] " + Colors.ENDC +
                                " Symbol " + char + " not recognized by the automata")

            try:
                s = self.transition_function[(s, char)]
            except:
                return Colors.WARNING + "Not Accepted" + Colors.ENDC

        terminal = True if s in self.terminal_states else terminal

        if terminal is None:
            return Colors.FAIL + str(terminal) + Colors.ENDC
        if terminal:
            return Colors.OKGREEN + "Accepted" + Colors.ENDC
        else:
            return Colors.WARNING + "Not Accepted" + Colors.ENDC
