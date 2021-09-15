'Testing out the agent behavior'
from Tartarus import Tarpy # Import Tarpy class from Tartarus file

t = Tarpy() # Create an object of the class Tarpy

exelock = t.get_val(_Agent, "exelock",_Port) # Fetch the execution lock flag
if exelock[0] == 1:
    # If the execution lock flag is 1 then execute the process
    add_prev = t.get_val(_Agent, "addprev",_Port) # Getting previous node data if available
    if len(add_prev) == 1:
        # If there is a previous node to store in the platform
        t.assign_val("", "previous", add_prev,_Port) # Adding previous node to the platform
        t.add_val(_Agent, "visited", [_Port],_Port) # Adding the current node to visited list
        print("############# node visited after port "+str(add_prev[0])+" ################")

    neighbours = t.get_val("", "neighbours",_Port) # Extracting neighbours of the current platform
    prev = t.get_val("", "previous",_Port) # Extracting the previous node of the platform
    visited = t.get_val(_Agent, "visited",_Port) # Extracting all the visited nodes

    if len(prev) == 0:
        # If no previous node then it is starting node
        if _Port not in visited:
            # If starting node is not visited then it is the start of the dft
            print("starting dft")
            t.add_val(_Agent, "visited", [_Port],_Port) # Add starting node to visited list
            print("###################### node visited ###############################")
            t.add_val(_Agent, "addprev", [_Port],_Port) # Add starting node to addprev for next node
            if len(neighbours) == 0: # If starting node have no neighbours dft is done as node is isolated
                print("###################### node is isolated ######################")
            else:
                # If the staring node have neighbours we move to the first neighbour as the only node visited is the starting node
                t.move_agent(_Agent, _IP, neighbours[0],_Port) 
        else:
            # If starting node is visited then check whether there is any unvisited neighbouring node
            complete_flag = 1 # Create a flag for cheking the dft's completion(set to 0 is any unvisited neighbour is found)
            for n in neighbours:
                if n not in visited:
                    complete_flag = 0 # If an unvisited neighbouring node exixts dft is not finished
                    t.remove_val(_Agent, "addprev", add_prev,_Port) # Removing the previous data in addprev
                    t.add_val(_Agent, "addprev", [_Port],_Port) # Add current node to addprev for next node
                    #visitng un visited node
                    t.move_agent(_Agent, _IP, n,_Port) # moving to the unvisited neighbouring node
                    break
            if complete_flag == 1:
                # If the value of the flag is unaltered then dft is completed
                visited = t.get_val(_Agent, "visited", _Port) # Fetching visited nodes
                t.remove_val(_Agent, "visited", visited, _Port) # Emptying the visited list
                addprev = t.get_val(_Agent, "addprev", _Port) # Fetching addprev data stored in the agent
                t.remove_val(_Agent, "addprev", addprev, _Port) # Emptying the addprev list
                print("#################### dft completed ############################")
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
            # If the value of the flag is unaltered then we need to backtrack
            t.remove_val(_Agent, "addprev", add_prev,_Port) # Removing the addprev values as we should not change the previous node
            t.remove_val("", "previous", prev,_Port) # As the current node is visited and never visited again previous node data is cleaned for next execution
            #backtracking
            print("######################## backtracking ###########################")
            t.move_agent(_Agent, _IP,prev[0],_Port) # Backtracking to the previous node
else:
    # If the execution lock flag is not 1 then don't execute the process
    print("dft agent is locked. unlock to execute")