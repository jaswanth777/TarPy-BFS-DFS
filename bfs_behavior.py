'Testing out the agent behavior'
from Tartarus import Tarpy # Import Tarpy class from Tartarus file

t = Tarpy() # Create an object of the class Tarpy

exelock = t.get_val(_Agent, "exelock",_Port) # Fetch the execution lock flag
if exelock[0] == 1:
    # If the execution lock flag is 1 then execute the process
    completiondata = t.get_val(_Agent, "completiondata",_Port) # Getting completion data
    if len(completiondata) > 1:
        # If the output string is present then bfs is over(this happens only at starting node)
        print(completiondata[1]) # Print the output string
        t.remove_val(_Agent, "completiondata", [completiondata[1]], _Port) # Removing the output string from completion data
        nodequeue = t.get_val(_Agent, "nodequeue", _Port) # Fetching node queue
        t.remove_val(_Agent, "nodequeue", nodequeue, _Port) # Emptying the node queue
        t.add_val(_Agent, "nodequeue", [_Port], _Port) # Initializing the node queue with Starting node
        visited = t.get_val(_Agent, "visited", _Port) # Fetching visited nodes
        t.remove_val(_Agent, "visited", visited, _Port) # Emptying the visited list

        print("#################### bfs completed ############################")
    else:
        #If the output string is not present then continue the search

        # Adding node to visited list
        t.add_val(_Agent, "visited", [_Port],_Port)
        print("##################### node visited #########################")

        visited = t.get_val(_Agent, "visited",_Port) # Visited nodes till now
        t.remove_val(_Agent, "nodequeue", [_Port],_Port) # Removing current node from node queue

        tofind = t.get_val(_Agent, "tofind",_Port) # Collecting the key to search
        label = t.get_val("", "label",_Port) # Collecting the label of the platform
        if label == tofind:
            # If the labels match the search is over
            print("found")
            outputstr = "the label "+ tofind[0] + " is found at IP: " + str(_IP) + " and port: " + str(_Port) # Adding the label's location as output string
            topnode = int(completiondata[0]) # Extracting the starting node's port from completion data
            t.add_val(_Agent, "completiondata", [outputstr],_Port) # Adding output strig to completion data
            t.move_agent(_Agent, _IP, topnode,_Port) # moving the agent to starting node
        else:

            # If the labels doesn't match continue with the search
            neighbours = t.get_val("", "neighbours",_Port) # Collecting neighbouring nodes of the current node
            addnode = [] # Creating a list for nodes to be added to node queue
            for n in neighbours:
                if n not in visited:
                    addnode.append(n) # Out of all the neighbours adding the non visited nodes to the list
            t.add_val(_Agent, "nodequeue", addnode,_Port) # Adding the list to node queue
            nodequeue = t.get_val(_Agent, "nodequeue",_Port) # Getting the updated list
            if len(nodequeue) == 0:
                # If the node queue is empty bfs is done but the label is not found
                print("################### bfs completed #######################")
                outputstr = "the label "+ tofind[0] + " is  not found " # creating output string 
                topnode = int(completiondata[0]) # Extracting the starting node's port from completion data
                t.add_val(_Agent, "completiondata", [outputstr],_Port) # Adding output string to completion data
                t.move_agent(_Agent, _IP, topnode,_Port) # moving the agent to starting node
            else:
                # If the node queue is not empty move to first node in the queue
                t.move_agent(_Agent, _IP, nodequeue[0],_Port)
else:
    # If the execution lock flag is not 1 then don't execute the process
    print("bfs agent is locked. unlock to execute")