'Testing out the agent behavior'
from Tartarus import Tarpy # Import Tarpy class from Tartarus file

t = Tarpy() # Create an object of the class Tarpy

exelock = t.get_val(_Agent, "exelock",_Port) # Fetch the execution lock flag
if exelock[0] == 1:
    # If the execution lock flag is 1 then execute the process
    completiondata = t.get_val(_Agent, "completiondata",_Port) # Fetching completion data from the agent
    if len(completiondata) > 1:
        # If there is a output string (the first element is the starting node's port) then search is done
        print(completiondata[1]) # printing the output string
        t.remove_val(_Agent, "completiondata", [completiondata[1]], _Port) # Removing the output string from completion data
        visited = t.get_val(_Agent, "visited", _Port) # Fetching visited nodes
        t.remove_val(_Agent, "visited", visited, _Port) # Emptying the visited list
        addprev = t.get_val(_Agent, "addprev", _Port) # Fetching addprev data stored in the agent
        t.remove_val(_Agent, "addprev", addprev, _Port) # Emptying the addprev list
        print("#################### dfs completed ############################")
    else:
        # If there is no output string (the first element is the starting node's port) then search must  go on.
        add_prev = t.get_val(_Agent, "addprev",_Port) # Getting previous node data if available
        if len(add_prev) == 1:
            # If there is a previous node to store in the platform
            t.assign_val("", "previous", add_prev,_Port) # Adding previous node to the platform
            t.add_val(_Agent, "visited", [_Port],_Port) # Adding the current node to visited list
            print("############# node visited after port "+str(add_prev[0])+" ################")
        
        tofind = t.get_val(_Agent, "tofind",_Port) # Fetching the ladel to be searched for
        label = t.get_val("", "label",_Port) # Fetching the label of the current node
        
        if label == tofind:
            # If the labels match search is over
            print("found")
            topnode = int(completiondata[0]) # We fetch the starting node 
            outputstr = "the label "+ tofind[0] + " is found at IP: " + str(_IP) + " and port: " + str(_Port) # Creating the output string with the location of the found label
            t.add_val(_Agent, "completiondata", [outputstr],_Port) # Adding the output string to completion data
            t.move_agent(_Agent, _IP, topnode,_Port) # moving the agent to starting node
        else:

            # If the labels doesn't match continue with the search
            neighbours = t.get_val("", "neighbours",_Port) # Extracting neighbours of the current platform
            prev = t.get_val("", "previous",_Port) # Extracting the previous node of the platform
            visited = t.get_val(_Agent, "visited",_Port) # Extracting all the visited nodes

            if len(prev) == 0:
                # If starting node is not visited then it is the start of the dfs
                if _Port not in visited:
                    print("starting dfs")
                    t.add_val(_Agent, "visited", [_Port],_Port) # Add starting node to visited list
                    print("###################### node visited ###############################")
                    t.add_val(_Agent, "addprev", [_Port],_Port) # Add starting node to addprev for next node
                    if len(neighbours) == 0: # If starting node have no neighbours dfs is done as node is isolated
                        print("###################### node is isolated ######################")
                    else:
                        # If the staring node have neighbours we move to the first neighbour as the only node visited is the starting node
                        t.move_agent(_Agent, _IP, neighbours[0],_Port)
                else:
                    # If starting node is visited then check whether there is any unvisited neighbouring node
                    complete_flag = 1 # Create a flag for cheking the traversal completion(set to 0 is any unvisited neighbour is found)
                    for n in neighbours:
                        if n not in visited:
                            complete_flag = 0 # If an unvisited neighbouring node exixts dfs is not finished
                            t.remove_val(_Agent, "addprev", add_prev,_Port) # Removing the previous data in addprev
                            t.add_val(_Agent, "addprev", [_Port],_Port) # Add current node to addprev for next node
                            #visitng un visited node
                            t.move_agent(_Agent, _IP, n,_Port) # moving to the unvisited neighbouring node
                            break
                    if complete_flag == 1:
                        # If the value of the flag is unaltered then dfs is completed and the label is not found
                        print("#################### dfs completed ############################")
                        print("#################### node not found ###########################")
            else:
                # If there is a previous node then it is not a starting node
                complete_flag = 1 # Create a flag for cheking whether we need to backtrack or not(set to 0 is any unvisited neighbour is found)
                for n in neighbours:
                    if n not in visited:
                        complete_flag = 0 # If an unvisited neighbouring node exixts then backtracking is not needed
                        t.remove_val(_Agent, "addprev", add_prev,_Port) # Removing the previous data in addprev
                        t.add_val(_Agent, "addprev", [_Port],_Port) # Add current node to addprev for next node
                        #visiting unvisited node
                        t.move_agent(_Agent, _IP,n,_Port) # moving to the unvisited neighbouring node
                        break
                if complete_flag == 1:
                    t.remove_val(_Agent, "addprev", add_prev,_Port) # Removing the addprev values as we should not change the previous node
                    #backtracking
                    print("######################## backtracking ###########################")
                    t.move_agent(_Agent, _IP,prev[0],_Port) # Backtracking to the previous node
else:
    # If the execution lock flag is not 1 then don't execute the process
    print("dfs agent is locked. unlock to execute")