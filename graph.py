from Tartarus import Tarpy # Import Tarpy class from Tartarus file

t = Tarpy() # Create an object of the class Tarpy

t.include("platform_ubuntu.pl") # including the Tartarus platform file which is a string

IP = "localhost" # IP address
Port = (int(input("Enter node: "))+4000)*2 # Port of current platform. did the caliculation to give every node atleast 2 Ports gap
label = input("Enter label of platform(used in search): ") # Key value for searching
Token = 7 #token
dftagent = "dft" # Agent for depth first traversal
bftagent = "bft" # Agent for breadth first traversal
dfsagent = "dfs" # Agent for depth first search
bfsagent = "bfs" # Agent for breadth first search
cleaneragent = "cleaner" # Agent for cleaning up all the changes made by the agents. Preparing the nodes for another execution
exelockeragent = "exelocker" # Agent for locking the remaining agents behavior for migration
neighbours = [2*(int(x)+4000) for x in input("Enter neighbours:\n").split()] # Neighbouring nodes input
exe_flag = int(input("Enter\n1 to run dft\n2 to run bft\n3 to run dfs\n4 to run bfs\n0 to execute nothing\n: ")) # Execution flag input. 0 for nothing 1 for dft 2 for bft 3 for dfs 4 for bfs
if exe_flag != 0:
    tofind = input("enter the label to search(also collected for dft and bft, this is used for bfs and dfs infuture exe)\n: ") # Search Key (for dft and bft also for future execution purpose)
t.start_tartarus(IP, Port, Token) # Starting platform with IP and Port 

t.assign_val("", "neighbours", neighbours) # Assigning neighbours to platform
t.assign_val("", "label", [label]) # Assigning label to platform
t.assign_val("", "previous", []) # Creating a empty variable to store previous node data

if exe_flag != 0:
    #dft agent creation
    t.create_mobile_agent(dftagent, "dft_behavior.py", IP, Port, [Token])
    t.assign_val(dftagent, "visited", []) # Visited nodes
    t.assign_val(dftagent, "addprev", []) # To carry previous nodes data
    t.assign_val(dftagent, "exelock", [1]) # To not let the agent execute right after it is migrated
    t.add_payload(dftagent, "visited") # Adding visited payload
    t.add_payload(dftagent, "addprev") # Adding addprev payload
    t.add_payload(dftagent, "exelock") # Adding exelock payload

    #bft agent creation
    t.create_mobile_agent(bftagent, "bft_behavior.py", IP, Port, [Token])
    t.assign_val(bftagent, "nodequeue", [Port]) # Next "to visit" node queue
    t.assign_val(bftagent, "visited", []) # Visited nodes
    t.assign_val(bftagent, "completiondata", [str(Port)]) # To update status of traversal completion and return to start node. used string form of port to further add output string
    t.assign_val(bftagent, "exelock", [1]) # To not let the agent execute right after it is migrated
    t.add_payload(bftagent, "nodequeue") # Adding nodequeue payload
    t.add_payload(bftagent, "visited") # Adding visited payload
    t.add_payload(bftagent, "completiondata") # Adding completiondata payload
    t.add_payload(bftagent, "exelock") # Adding exelock payload

    #dfs agent creation
    t.create_mobile_agent(dfsagent, "dfs_behavior.py", IP, Port, [Token])
    t.assign_val(dfsagent, "visited", []) # Visited nodes
    t.assign_val(dfsagent, "addprev", []) # To carry previous nodes data
    t.assign_val(dfsagent, "tofind", [tofind]) # key of node to be searched
    t.assign_val(dfsagent, "completiondata", [str(Port)]) # To update status of search completion and return to start node. used string form of port to further add output string
    t.assign_val(dfsagent, "exelock", [1]) # To not let the agent execute right after it is migrated
    t.add_payload(dfsagent, "visited") # Adding visited payload
    t.add_payload(dfsagent, "addprev") # Adding addprev payload
    t.add_payload(dfsagent, "tofind") # Adding tofind payload
    t.add_payload(dfsagent, "completiondata") # Adding completiondata payload
    t.add_payload(dfsagent, "exelock") # Adding exelock payload

    #bfs agent creation
    t.create_mobile_agent(bfsagent, "bfs_behavior.py", IP, Port, [Token])
    t.assign_val(bfsagent, "nodequeue", [Port]) # Next "to visit" node queue
    t.assign_val(bfsagent, "visited", []) # Visited nodes
    t.assign_val(bfsagent, "tofind", [tofind]) # key of node to be searched
    t.assign_val(bfsagent, "completiondata", [str(Port)]) # To update status of search completion and return to start node. used string form of port to further add output string
    t.assign_val(bfsagent, "exelock", [1]) # To not let the agent execute right after it is migrated
    t.add_payload(bfsagent, "nodequeue") # Adding nodequeue payload
    t.add_payload(bfsagent, "visited") # Adding visited payload
    t.add_payload(bfsagent, "tofind") # Adding tofind payload
    t.add_payload(bfsagent, "completiondata") # Adding completiondata payload
    t.add_payload(bfsagent, "exelock") # Adding exelock payload

    #cleaner agent creation
    t.create_mobile_agent(cleaneragent, "cleaner_behavior.py", IP, Port, [Token])
    t.assign_val(cleaneragent, "nodequeue", [Port]) # Next "to visit" node queue
    t.assign_val(cleaneragent, "visited", []) # Visited nodes
    t.assign_val(cleaneragent, "completiondata", [str(Port)]) # To update status of cleaning completion and return to start node. used string form of port to further add output string
    t.assign_val(cleaneragent, "exelock", [1]) # To not let the agent execute right after it is migrated
    t.add_payload(cleaneragent, "nodequeue") # Adding nodequeue payload
    t.add_payload(cleaneragent, "visited") # Adding visited payload
    t.add_payload(cleaneragent, "completiondata") # Adding completiondata payload
    t.add_payload(cleaneragent, "exelock") # Adding exelock payload
    
    #mover agent creation
    t.create_mobile_agent(exelockeragent, "exelocker_behavior.py", IP, Port, [Token])
    t.assign_val(exelockeragent, "toggler", [0]) # Used to toggle the execution lock of the above agents
    t.add_payload(exelockeragent, "toggler") # Adding toggler payload
if exe_flag == 1:
    #dft execution
    t.agent_execute(dftagent, IP, Port)
elif exe_flag == 2:
    #bft execution
    t.agent_execute(bftagent, IP, Port)
elif exe_flag == 3:
    #dfs execution
    t.agent_execute(dfsagent, IP, Port)
elif exe_flag == 4:
    #bfs execution
    t.agent_execute(bfsagent, IP, Port)

t.keep_alive() # Keep the platform available for further instructions