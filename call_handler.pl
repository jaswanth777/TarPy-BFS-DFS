:- dynamic mobile_handler/3, static_handler/3.

% below predicate is for the mobile agents. for all the mobile  agents this handler 
% is called. The functionality of this agent is fix, the value which will be returned
% from the python call is checked if it is greater than 0 then the agent keeps on moving
% else the agent will stop.

custom_move_agent(Agent_name, Receiver_ip, Receiver_port):-
    retractall(next_add(Agent_name, _, _)),
    assert(next_add(Agent_name, Receiver_ip, Receiver_port)),
    move_agent(Agent_name, (Receiver_ip, Receiver_port)).

mobile_handler(guid,(_,_),main):-
    % Retrieving payload values from predicates into Variables
    atom_string(guid, Guid),
    code_string(guid, Tmp_Str_Code),
    get_platform_details(Curr_IP, Curr_Port),

    % Check if IP is of datatype compound. If yes, convert it to atom
    (compound(Curr_IP), term_to_atom(Curr_IP, Atom_Curr_IP) ; Atom_Curr_IP = Curr_IP),

    % Append Current IP, Port and Agent Name to handler file while writing to current socket
    atom_concat('_IP = \"', Atom_Curr_IP, Partial_Curr_IP),
    atom_concat(Partial_Curr_IP, '\"\n', Complete_Curr_IP),

    atom_concat('_Port = ', Curr_Port, Partial_Curr_Port),
    atom_concat(Partial_Curr_Port, '\n', Complete_Curr_Port),

    atom_concat('_Agent = \"', Guid, Partial_Agent_Name),
    atom_concat(Partial_Agent_Name, '\"\n\n', Complete_Agent_Name),

    atom_concat(Complete_Curr_IP, Complete_Curr_Port, Complete_Socket),
    atom_concat(Complete_Socket, Complete_Agent_Name, Details),
    atom_concat(Details, Tmp_Str_Code, Atom_Code),
    atom_string(Atom_Code, Str_Code),

    % ------------------------------------------------------------------------------------------
    % Formation of filename strings
    
    atom_concat(Guid, '_handler_Rec', Handler_File_NoExt),
    atom_concat(Handler_File_NoExt, '.py', Handler_File),
    atom_concat('', Handler_File, Handler_File_Location),

    %------------------------------------------------------------------------------------------
    % Writing the payloads to agent_specific files
    
    % writing handler code in file "Guid_handler_Rec.py"
    open(Handler_File, write, Handler_File_Stream),
    write(Handler_File_Stream, Str_Code),
    close(Handler_File_Stream),

    %------------------------------------------------------------------------------------------
    % Call the python handler to visit the current node and get the next port to be visited
            
    process_create(path('python'), [Handler_File_Location], [stdout(pipe(In1)), process(PID1)]),
    read_string(In1, _, Op1),
    close(In1),
    process_release(PID1),
    writeln(Op1),

    %----------------------------------------------------------------------------------------
    % Delete the files created by this handler

    delete_file(Handler_File), 
    
    %----------------------------------------------------------------------------------------
    % checking if the handler needs to be changed 

    change_handler(guid, Mn),
    (
        Mn =:= 1
        ->  writeln('Yes, handler needs to be changed'),
            extract_handler(guid, Extract_Handler),
            atom_concat(Guid, '_extract_handler.py', Extract_Handler_File),
            atom_concat('', Extract_Handler_File, _),
            open(Extract_Handler_File, write, Extract_Handler_Stream),
            write(Extract_Handler_Stream, Extract_Handler),
            close(Extract_Handler_Stream),

            process_create(path('python'), [Extract_Handler_File], [stdout(pipe(In2)), process(PID2)]),
            read_string(In2, _, Extracted_Handler),
            close(In2),
            process_release(PID2),
            
            retractall(code_string(guid, _)),
            assert(code_string(guid, Extracted_Handler)),
            delete_file(Extract_Handler_File),

            % change_handler back to its normal state else, it will 
            % again change the handler since the value is 1
            retractall(change_handler(guid,_)),
            assert(change_handler(guid, 0))

        ; nothing
    ),
    
    %----------------------------------------------------------------------------------------
    % Check if NextPort is greater than 0, else stop
    next_add(guid, IP, Port),
    
    % Check if IP is of datatype compound. If yes, convert it to atom
    (compound(IP), term_to_atom(IP, IP_Send) ; IP_Send = IP),

    % Write next IP and Port on terminal
    write(Guid),
    write(': After changes, Next IP is ' : IP_Send),
    writeln(' and Port is ': Port),
    (
        % Move only if there is change either in IP or Port
        (Port = Curr_Port, IP = Curr_IP), writeln('Agent stopped'); move_agent(guid, (IP_Send, Port))
    ).
    
% This predicate is for the static agents. whenever the static agent is executed 
% the below predicate is executed. like in the above predicate(mobile_handler) the returned value 
% is checked if it greater than 0, but here there is no such checking since the agent doesn't 
% move thereby it only prints the returned output.

static_handler(guid,(_,_),main):-

    % Retrieving payload values from predicates into Variables
    code_string(guid, Str_Code),
    
    %------------------------------------------------------------------------------------------------
    % Formation of filename strings
    
    atom_string(guid, Guid),

    atom_concat(Guid, '_handler_Rec', Handler_File_NoExt),
    atom_concat(Handler_File_NoExt, '.py', Handler_File),
    atom_concat('', Handler_File, Handler_File_Location),

    %------------------------------------------------------------------------------------------------
    % Writing the payloads to agent_specific files
    
    %writing handler code in file Guid_handler_Rec.py
    open(Handler_File, write, Handler_File_Stream),
    write(Handler_File_Stream, Str_Code),
    close(Handler_File_Stream),
    
    %-------------------------------------------------------------------------------------------------
    % Call the python handler to visit the current node and get the next port to be visited

    process_create(path('python'), [Handler_File_Location], [stdout(pipe(In1)), process(PID1)]),
    read_string(In1, _, Op1),
    close(In1),
    process_release(PID1),
    writeln(Op1),
    %----------------------------------------------------------------------------------------
    % Delete the files created by this handler

    delete_file(Handler_File),
    change_handler(guid, Mn),
    (
        Mn =:= 1
        ->  writeln('Yes, handler needs to be changed'),
            extract_handler(guid, Extract_Handler),
            atom_concat(Guid, '_extract_handler.py', Extract_Handler_File),
            atom_concat('', Extract_Handler_File, _),
            open(Extract_Handler_File, write, Extract_Handler_Stream),
            write(Extract_Handler_Stream, Extract_Handler),
            close(Extract_Handler_Stream),

            process_create(path('python'), [Extract_Handler_File], [stdout(pipe(In2)), process(PID2)]),
            read_string(In2, _, Extracted_Handler),
            close(In2),
            process_release(PID2),
            
            retractall(code_string(guid, _)),
            assert(code_string(guid, Extracted_Handler)),
            delete_file(Extract_Handler_File),

            % change_handler back to its normal state else, it will 
            % again change the handler since the value is 1
            retractall(change_handler(guid, _)),
            assert(change_handler(guid, 0))

        ; nothing
    ).