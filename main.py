from automata import DFA
from structures import SyntaxTree
from utils import printBTree, readFile

from structures import Colors

# operators and precedence
OPERATORS = {
    '|': 1,
    '.': 2,
    '*': 3
}

# Example regex expression
# REGEX = '(a|b)*((a|(bb)))'
# REGEX = '(a|b)b'
# REGEX = '(a|b)*abb'
# REGEX = '(a|b)*a(a|b)(a|b)'
# REGEX = '(b|b)*abb(a|b)*'
# REGEX = '(ab)*(p|q)(p|q)*'
# REGEX = '(a|ab)*bb(a|b)*'
# REGEX = '(a(a|bb))'


def main():
    try:
        choice = int(
            input(Colors.HEADER + "[QUESTION] " + Colors.ENDC + "Would you like to read from file or from console?(0-file, 1-console): "))

        # read file
        if choice == 0:
            filename = "input.txt"
            input(Colors.OKBLUE + "[INFO] " + Colors.ENDC +
                  f"Place your input into {filename} and press enter to continue...\n")
            user_input = readFile(filename)
            print(Colors.OKBLUE + "[INFO] " + Colors.ENDC +
                  f"Read input string: {user_input}")
        # read from console
        if choice == 1:
            user_input = input(
                Colors.HEADER + "[QUESTION] " + Colors.ENDC + "Please enter your input: ")

        # Regex to DFA using direct method
        hash_tree = SyntaxTree(OPERATORS, "(" + user_input + ")" + "#")

        # get nodes for computing nullable, firstpos, lastpos and followpos
        nodes = hash_tree.traverse_postorder(hash_tree.root)

        # instantiate dfa object
        direct_dfa = DFA(syntax_tree=hash_tree, nodes=nodes)

        # print syntax tree
        printBTree(hash_tree.root, lambda n: (n.data, n.left, n.right))
        # call get_tree_data method
        direct_dfa.get_tree_data()

        # graph resulting DFA
        direct_dfa.graph_automata(mapping=direct_dfa.state_mapping)

        # check if string can be Accepted by dfa
        while True:
            try:
                string_to_check = input(
                    Colors.HEADER + "[QUESTION] " + Colors.ENDC + "Enter a string to check: ")
                result = direct_dfa.isGenerated(string_to_check)
                print(Colors.OKBLUE + "[INFO] " + Colors.ENDC +
                      f"ACCEPTANCE RESULT FOR DFA \n-> {result}\n")
                choice = int(input(
                    Colors.HEADER + "[QUESTION] " + Colors.ENDC + "Would you like to try another string?(1-yes,0-no): "))
                if not choice:
                    main() if int(input(Colors.HEADER +
                                        "[QUESTION] " + Colors.ENDC + "Would you like to give it another try and enter another RE?(1-yes, 0-no): ")) else exit()

            except Exception as e:
                print(e)
                choice = int(input(
                    Colors.HEADER + "[QUESTION] " + Colors.ENDC + "Would you like to try another string?(1-yes,0-no): "))
                if not choice:
                    main() if int(input(Colors.HEADER +
                                        "[QUESTION] " + Colors.ENDC + "Would you like to give it another try and enter another RE?(1-yes, 0-no): ")) else exit()

    except AssertionError as e:
        print(e)
        main() if int(input(Colors.HEADER +
                            "[QUESTION] " + Colors.ENDC + "Would you like to give it another try and enter another RE?(1-yes, 0-no): ")) else exit()
    except ValueError:
        main() if int(input(Colors.HEADER +
                            "[QUESTION] " + Colors.ENDC + "Would you like to give it another try and enter another RE?(1-yes, 0-no): ")) else exit()


if __name__ == '__main__':
    main()
