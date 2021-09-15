'Testing out the agent behavior'
from Tartarus import Tarpy # Import Tarpy class from Tartarus file

t = Tarpy() # Create an object of the class Tarpy

exelock = t.get_val(_Agent, "exelock",_Port) # Fetch the execution lock flag
if exelock[0] == 1:
    # If the execution lock flag is 1 then execute the process
    completiondata = t.get_val(_Agent, "completiondata",_Port) # Getting completion data
    if len(completiondata) > 1:
        # If the output string is present then bft is over(this happens only at starting node)
        print(completiondata[1]) # Print the output string
        t.remove_val(_Agent, "completiondata", [completiondata[1]], _Port)
        visited = t.get_val(_Agent, "visited", _Port) # Fetching visited nodes
        t.remove_val(_Agent, "visited", visited, _Port) # Emptying the visited list
        t.add_val(_Agent, "nodequeue", [_Port], _Port) # Initializing the node queue with Starting node
    else:
        #If the output string is not present then continue the travesal

        # Adding node to visited list
        t.add_val(_Agent, "visited", [_Port],_Port)
        print("##################### node visited #########################")

        visited = t.get_val(_Agent, "visited",_Port) # Visited nodes till now
        t.remove_val(_Agent, "nodequeue", [_Port],_Port) # Removing current node from node queue
        neighbours = t.get_val("", "neighbours",_Port) # Collecting neighbouring nodes of the current node
        addnode = [] # Creating a list for nodes to be added to node queue
        for n in neighbours:
            if n not in visited:
                addnode.append(n) # Out of all the neighbours adding the non visited nodes to the list
        t.add_val(_Agent, "nodequeue", addnode,_Port) # Adding the list to node queue
        nodequeue = t.get_val(_Agent, "nodequeue",_Port) # Getting the updated list
        if len(nodequeue) == 0:
            # If the node queue is empty bft is done
            outputstr = "#################### bft completed ############################"
            t.add_val(_Agent, "completiondata", [outputstr], _Port)
            t.move_agent(_Agent, _IP, int(completiondata[0]), _Port)
        else:
            # If the node queue is not empty move to first node in the queue
            t.move_agent(_Agent, _IP, nodequeue[0],_Port)
else:
    # If the execution lock flag is not 1 then don't execute the process
    print("bft agent is locked. unlock to execute")