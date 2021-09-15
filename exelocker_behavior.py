'Testing out the agent behavior'
from Tartarus import Tarpy # Import Tarpy class from Tartarus file

t = Tarpy() # Create an object of the class Tarpy

toggler = t.get_val(_Agent, "toggler",_Port) # Fetching the toggler

if toggler[0] == 1:
    # If the toggler is 1 then unlock the agents and intialize their payloads
    dftlock = t.get_val("dft", "exelock", _Port) # Fetching the execution lock of dft
    dfslock = t.get_val("dfs", "exelock", _Port) # Fetching the execution lock of dfs
    bftlock = t.get_val("bft", "exelock", _Port) # Fetching the execution lock of bft
    bfslock = t.get_val("bfs", "exelock", _Port) # Fetching the execution lock of bfs
    cleanerlock = t.get_val("cleaner", "exelock", _Port) # Fetching the execution lock of cleaner
    t.remove_val("dft", "exelock", dftlock, _Port) # Emptying the execution lock values of dft
    t.remove_val("dfs", "exelock", dfslock, _Port) # Emptying the execution lock values of dfs
    t.remove_val("bft", "exelock", bftlock, _Port) # Emptying the execution lock values of bft
    t.remove_val("bfs", "exelock", bfslock, _Port) # Emptying the execution lock values of bfs
    t.remove_val("cleaner", "exelock", cleanerlock, _Port) # Emptying the execution lock values of cleaner
    t.add_val("dft", "exelock", [1], _Port) # Adding 1 to the execution lock of dft
    t.add_val("dfs", "exelock", [1], _Port) # Adding 1 to the execution lock of dfs
    t.add_val("bft", "exelock", [1], _Port) # Adding 1 to the execution lock of bft
    t.add_val("bfs", "exelock", [1], _Port) # Adding 1 to the execution lock of bfs
    t.add_val("cleaner", "exelock", [1], _Port) # Adding 1 to the execution lock of cleaner

    # Initializing nodequeue of bftagent
    bftnq = t.get_val("bft", "nodequeue", _Port) # Fetching the nodequeue of bftagent
    t.remove_val("bft", "nodequeue", bftnq, _Port) # Emptying the nodequeue of bftagent
    t.add_val("bft", "nodequeue", [_Port], _Port) # Adding port to the nodequeue of bftagent
    # Initializing completiondata of bftagent
    bftcd = t.get_val("bft", "completiondata", _Port) # Fetching the completiondata of bftagent
    t.remove_val("bft", "completiondata", bftcd, _Port) # Emptying the completiondata of bftagent
    t.add_val("bft", "completiondata", [str(_Port)], _Port) # Adding port to the completiondata of bftagent
    # Initializing completiondata of dfsagent
    dfscd = t.get_val("dfs", "completiondata", _Port) # Fetching the completiondata of dfsagent
    t.remove_val("dfs", "completiondata", dfscd, _Port) # Emptying the completiondata of dfsagent
    t.add_val("dfs", "completiondata", [str(_Port)], _Port) # Adding port to the completiondata of dfsagent
    # Initializing nodequeue of bfsagent
    bfsnq = t.get_val("bfs", "nodequeue", _Port) # Fetching the nodequeue of bfsagent
    t.remove_val("bfs", "nodequeue", bfsnq, _Port) # Emptying the nodequeue of bfsagent
    t.add_val("bfs", "nodequeue", [_Port], _Port) # Adding port to the nodequeue of bfsagent
    # Initializing completiondata of bfsagent
    bfscd = t.get_val("bfs", "completiondata", _Port) # Fetching the completiondata of bfsagent
    t.remove_val("bfs", "completiondata", dfscd, _Port) # Emptying the completiondata of bfsagent
    t.add_val("bfs", "completiondata", [str(_Port)], _Port) # Adding port to the completiondata of bfsagent
    # Initializing nodequeue of cleaneragent
    cleanernq = t.get_val("cleaner", "nodequeue", _Port) # Fetching the nodequeue of cleaneragent
    t.remove_val("cleaner", "nodequeue", cleanernq, _Port) # Emptying the nodequeue of cleaneragent
    t.add_val("cleaner", "nodequeue", [_Port], _Port) # Adding port to the nodequeue of cleaneragent
    # Initializing completiondata of cleaneragent
    cleanercd = t.get_val("cleaner", "completiondata", _Port) # Fetching the completiondata of cleaneragent
    t.remove_val("cleaner", "completiondata", dfscd, _Port) # Emptying the completiondata of cleaneragent
    t.add_val("cleaner", "completiondata", [str(_Port)], _Port) # Adding port to the completiondata of cleaneragent
    t.remove_val(_Agent, "toggler", toggler, _Port) # Emptying the value of toggler
    t.add_val(_Agent, "toggler", [0], _Port) # Adding 0 to the toggler
    
elif toggler[0]==0:
    # If the toggler is 0 then lock the agents
    dftlock = t.get_val("dft", "exelock", _Port) # Fetching the execution lock of dft
    dfslock = t.get_val("dfs", "exelock", _Port) # Fetching the execution lock of dfs
    bftlock = t.get_val("bft", "exelock", _Port) # Fetching the execution lock of bft
    bfslock = t.get_val("bfs", "exelock", _Port) # Fetching the execution lock of bfs
    cleanerlock = t.get_val("cleaner", "exelock", _Port) # Fetching the execution lock of cleaner
    t.remove_val("dft", "exelock", dftlock, _Port) # Emptying the execution lock values of dft
    t.remove_val("dfs", "exelock", dfslock, _Port) # Emptying the execution lock values of dfs
    t.remove_val("bft", "exelock", bftlock, _Port) # Emptying the execution lock values of bft
    t.remove_val("bfs", "exelock", bfslock, _Port) # Emptying the execution lock values of bfs
    t.remove_val("cleaner", "exelock", cleanerlock, _Port) # Emptying the execution lock values of cleaner
    t.add_val("dft", "exelock", [0], _Port) # Adding 0 to the execution lock of dft
    t.add_val("dfs", "exelock", [0], _Port) # Adding 0 to the execution lock of dfs
    t.add_val("bft", "exelock", [0], _Port) # Adding 0 to the execution lock of bft
    t.add_val("bfs", "exelock", [0], _Port) # Adding 0 to the execution lock of bfs
    t.add_val("cleaner", "exelock", [0], _Port) # Adding 0 to the execution lock of cleaner
    t.remove_val(_Agent, "toggler", toggler, _Port) # Emptying the value of toggler
    t.add_val(_Agent, "toggler", [1], _Port) # Adding 1 to the toggler