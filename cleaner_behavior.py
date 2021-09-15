'Testing out the agent behavior'
from Tartarus import Tarpy # Import Tarpy class from Tartarus file

t = Tarpy() # Create an object of the class Tarpy

exelock = t.get_val(_Agent, "exelock",_Port) # Fetch the execution lock flag
if exelock[0] == 1:
    # If the execution lock flag is 1 then execute the process
    completiondata = t.get_val(_Agent, "completiondata", _Port) # Fetching completion data from the agent
    if len(completiondata) > 1:
        # If there is a output string (the first element is the starting node's port) then other nodes cleanig is done
        outputstr = completiondata[1] # Creating an output string
        print(outputstr) # Printing the output string
        
        #cleaner agent clean
        t.remove_val(_Agent, "completiondata", [outputstr], _Port) # Removing the output string from completion data of cleaner
        t.add_val(_Agent, "nodequeue", [_Port], _Port) # As the cleaner performend a bft the node queue is empty so we need to add the current node
        visited = t.get_val(_Agent, "visited", _Port) # Fetching visited nodes of cleaner
        t.remove_val(_Agent, "visited", visited, _Port) # Emptying the visited list of cleaner

    else:
        # If there is no output string (the first element is the starting node's port) then clean the other nodes
        t.add_val(_Agent, "visited", [_Port], _Port) # Add current node to visited of cleaner
        prev = t.get_val("", "previous", _Port) # Fetching the previous node values stored in the node
        t.remove_val("", "previous", prev, _Port) # Emptying the previous node values of the node
        print("##################### node cleaned #########################")
        visited = t.get_val(_Agent, "visited", _Port) # Fetching all the nodes visited by cleaner
        t.remove_val(_Agent, "nodequeue", [_Port], _Port) # Remove the current nodefrom the node queue
        neighbours = t.get_val("", "neighbours", _Port) # Fetching the neighbours of the current node
        addnode = [] # Creating a list to add the unvisited neighbours
        for n in neighbours:
            if n not in visited:
                addnode.append(n) # If the neighbour is not visited append it to the list
        t.add_val(_Agent, "nodequeue", addnode, _Port) # Adding the unvisited nodes list to the node queue of the cleaner
        nodequeue = t.get_val(_Agent, "nodequeue", _Port) # Fetching the updated node queue of the cleaner
        if len(nodequeue) == 0:
            # If the node queue of the cleaner is empty the cleaning is done
            topnode = int(completiondata[0]) # Fetching the starting node from completion data of the cleaner
            outputstr = "############ nodes cleaning completed ##################" # Creating the output string
            t.add_val(_Agent, "completiondata", [outputstr], _Port) # Adding the output string to the completion data of the cleaner
            t.move_agent(_Agent, _IP, topnode, _Port) # Moving the cleaner agent back to the starting node
        else:
            # If the node queue of the cleaner is not empty then move the agent to next node in the node queue of the cleaner
            t.move_agent(_Agent, _IP, nodequeue[0], _Port)
else:
    # If the execution lock flag is not 1 then don't execute the process
    print("cleaner agent is locked. unlock to execute")