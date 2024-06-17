import re, sys

arg_grammar = "bash.grammar"
arg_script = sys.argv[1]
arg_debug_char = len(sys.argv) > 2
arg_debug_grammar = len(sys.argv) > 3
arg_debug_state = True
arg_indent = "    "

indent = arg_indent
classes = {
    "{newline}": "\n",
    "{space}": " ",
    "{tab}": "\t",
    "{alpha}": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXY",
    "{number}": "0123456789",
}
multi_regex = re.compile("{'[^']*'}|{\"[^\"]*\"}")
multi_length = 1

classes_chars = {}
for cs,s in classes.items():
    for c in s:
        if c not in classes_chars:
            classes_chars[c] = []
        classes_chars[c].append(cs)

#
class Entity:
    def __init__(self, target: str) -> None:
        target = target + ":0:0"
        parts = target.split(":")
        self.name = parts[0]
        self.offset = int(parts[1])
        self.start = int(parts[2])
    def __repr__(self) -> str:
        return "Entity(name=%r, offset=%d, start=%d)" % (self.name, self.offset, self.start)

class State:
    def __init__(self, name: str, start: int, depth: int) -> None:
        self.name = name
        self.start = start
        self.end = start
        self.depth = depth
    def __repr__(self) -> str:
        return "State(name=%r, start=%d, end=%d, depth=%d)" % (self.name, self.start, self.end, self.depth)

# utilities
def debug_start(state: State) -> None:
    print("%sstart: %s" % (indent*state.depth, state))

def debug_end(state: State, script: str) -> None:
    data = script[state.start:state.end]
    if len(data) > 60:
        data = data[:40] + "..." + data[-20:]
    print("%send: %s => %r" % (indent*state.depth, state, data))

def debug_char(pos: int, c: str, cs: str, before: str, after: str) -> None:
    print("%d: %r class=%r before=%r after=%r" % (pos, c, cs, before, after))

# read bash grammar script file
grammar = {}

with open(arg_grammar) as f:
    entity = None
    current = None
    # read lines one by one
    for line in f:
        # remove all leading and trailing whitespace
        line = line.strip()
        # if line is empty or a comment, skip
        if len(line) == 0 or line[0] == '#':
            continue
        # if line starts with ':', it is an entity
        if line[0] == ':':
            entity = {}
            current = line[1:]
            grammar[current] = entity
            continue
        # line is a key-value pair
        target, chars = line.split(" ", 1)
        chars = chars.strip().split(" ", 1)[0]
        # specific char classes
        for c in [ "{any}", "{eof}", "{hidden}" ] + list(classes.keys()):
            if c in chars:
                entity[c] = Entity(target)
                chars = chars.replace(c, "")
        for c in multi_regex.findall(chars):
            if len(c) - 4 > multi_length:
                multi_length = len(c) - 4
            entity[c[2:-2]] = Entity(target)
            chars = chars.replace(c, "")
        # add key-value pair to entity
        for c in chars:
            entity[c] = Entity(target)

if arg_debug_grammar:
    for t in sorted(grammar.keys()):
        ce = grammar[t]
        print("%s:" % t)
        for c,e in ce.items():
            print("    %11r: %s" % (c, e))

# read script file
with open(arg_script, "r") as f:
    script = f.read()
# if len(script) > 0 and script[-1] != "\n":
#     script = script + "\n"

# loop on characters in script
current_state = "start"
current_entity = grammar[current_state]
state = State(current_state, 0, 0)
states = [state]
states_offset = 0
debug_start(state)
pos = 0
while pos <= len(script):
    # get current character
    if pos == len(script):
        c = "{eof}"
        cs = ""
        pos += 1
    else:
        c = script[pos]
        for i in range(multi_length, 1, -1):
            if script[pos:pos+i] in current_entity:
                c = script[pos:pos+i]
                break
        cs = classes_chars[c] if c in classes_chars else []
        pos += len(c)
    # check if character is in grammar and get next state
    target = None
    found_c = None
    if found_c is None and c in current_entity:
        found_c = c
        target = current_entity[found_c]
    if target is None:
        for cc in cs:
            if cc in current_entity:
                found_c = cc
                target = current_entity[found_c]
                break
    if target is None and "{any}" in current_entity and c != "{eof}":
        found_c = "{any}"
        target = current_entity[found_c]
    # errors
    if target is None:
        if c == "{eof}":
            break
        raise Exception("unexpected character: %r" % c)
    # change state
    if arg_debug_char:
        debug_char(pos - 1, c, found_c, current_state, target.name)
    if target.name == "=":
        continue
    pos -= target.offset
    if target.name == "^":
        state = states.pop()
        state.end = pos - target.start
        if arg_debug_state:
            if "{hidden}" not in current_entity:
                debug_end(state, script)
            else:
                states_offset -= 1
        #
        state = states[-1]
        current_state = state.name
        current_entity = grammar[current_state]
    else:
        current_state = target.name
        current_entity = grammar[current_state]
        state = State(current_state, pos - target.start, len(states) - states_offset)
        states.append(state)
        if arg_debug_state:
            if "{hidden}" not in current_entity:
                debug_start(state)
            else:
                states_offset += 1

# check if all states are closed
if len(states) > 1:
    raise Exception("unexpected end of script")

# close last state
state = states.pop()
state.end = pos - 1
debug_end(state, script)
