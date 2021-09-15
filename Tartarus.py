import pyswip, ctypes
import ast, socket
from _thread import start_new_thread, allocate_lock

Lock = allocate_lock()
Client_Lock = allocate_lock()

# The below class is a non-intrusive fix for pyswip to support multithreading, can be ignored by developers.
# This fix was taken from https://github.com/yuce/pyswip/issues/3#issuecomment-355458825 
class PrologMT(pyswip.Prolog):
    """Multi-threaded (one-to-one) pyswip.Prolog ad-hoc reimpl"""
    _swipl = pyswip.core._lib

    PL_thread_self = _swipl.PL_thread_self
    PL_thread_self.restype = ctypes.c_int

    PL_thread_attach_engine = _swipl.PL_thread_attach_engine
    PL_thread_attach_engine.argtypes = [ctypes.c_void_p]
    PL_thread_attach_engine.restype = ctypes.c_int

    @classmethod
    def _init_prolog_thread(cls):
        pengine_id = cls.PL_thread_self()
        if (pengine_id == -1):
            pengine_id = cls.PL_thread_attach_engine(None)
            #print("{INFO} attach pengine to thread: %d" % pengine_id)
        if (pengine_id == -1):
            raise pyswip.prolog.PrologError("Unable to attach new Prolog engine to the thread")
        elif (pengine_id == -2):
            print("{WARN} Single-threaded swipl build, beware!")

    class _QueryWrapper(pyswip.Prolog._QueryWrapper):
        def __call__(self, *args, **kwargs):
            PrologMT._init_prolog_thread()
            return super().__call__(*args, **kwargs)




# All the rules of the Tartarus, written in its module are defined below. which can be called by the object 
# handler is defined in call_handler.pl file, User doesnt know anything about handler.
# Class Tarpy encapsulates all functions of Tarpy
class Tarpy:
    p = PrologMT()
    M_Handler = "mobile_handler"
    S_Handler = "static_handler"
    Static_agents = []
    Mobile_agents = []

    # Include function consults a prolog file to the memory
    def include(self, filename):
        self.p.consult(filename)

    # 'start_tartarus' is responsible for instantiating a Tartarus platform with a specific IP, Port and Token
    # Every platform also instantiates a server socket with IP = "127.0.0.1" and Port + 1.
    # Since sockets have an inherent queue, it can be specified manually by changing the default parameter named 'agents'
    def start_tartarus(self, IP, Port, Token, agents = 5):
        self.include("call_handler.pl")
        list(self.p.query("start_tartarus(" + repr(IP) + "," + str(Port) + "," + str(Token) + ")" ))    
        start_new_thread(self.server_thread,('127.0.0.1', Port + 1, agents))    # Run a server socket at IP = "127.0.0.1" and Port = Port + 1

    # 'close_tartarus' is responsible for closing the Tartarus platform.
    # It is recommended to close the Tartarus platform to release used resources.
    def close_tartarus(self):
        list( self.p.query("close_tartarus"))

    # 'reset_tartarus' closes and restarts the Tartarus platform with the same IP, Port, and Token already associated with it before closing.
    def reset_tartarus(self):
        list( self.p.query("reset_tartarus"))
    
    # 'print_tartarus_status' prints status of Tartarus such as agents present on the platform, IP, Port and Token of platform etc.
    # It prints all the values asserted in Tartarus platform, all the agent codes and threads currently associated with the platform, 
    # payloads carried by agents, token of the platform and other information related to platform. 
    def print_tartarus_status(self, port = None):
        if port is None:
            Lock.acquire()
            list( self.p.query("print_tartarus_status"))
            Lock.release()
        else:
            return self.to_tarpy(port, "query : print_tartarus_status")

    # 'assert_file_to_tartarus' is used for asserting the handler codes of the concerned agents by specifying 
    # the name of the file viz.File_name ( variable) which contains the agent code. 
    # NB: Here all file codes are in SWI-Prolog.
    """ FOR PROLOG USERS """
    def assert_file_to_tartarus(self, filename, port = None):
        Str = "assert_file_to_tartarus(\'" + filename + "\')"
        if port is None:
            Lock.acquire()
            list(self.p.query(Str))                             # "query : assert_file_to_tartarus('random_file.pl')"
            Lock.release()
        else:
            Str = "query : " + Str
            return self.to_tarpy(port, Str)

    # 'get_tartarus_details' gives the IP, Port number of platform set using start_tartarus function. 
    # The function comes handy when an agent or program requires to know the details of the platform where it is executing
    # Details of current IP and Port can be accessed in agent handler via '_IP' and '_Port' variables, thus the functionality to call this from handler is not added.
    def get_tartarus_details(self):
        Lock.acquire()
        """ Added during developers demo 7th July 2021, needs to be tested????"""
        for socket in list(self.p.query("get_tartarus_details(IP, Port)")):
            Lock.release()
            return socket['IP'], socket['Port']


    # 'set_token' function is required if the user wants to change the token at some later point after starting the platform
    def set_token(self, Token):
        Lock.acquire()
        list(self.p.query("set_token(" + str(Token) + ")"))
        Lock.release()

    # 'save_tartarus_state' stores all associated asserted code along with facts and running agents in this file location.
    """ FOR PROLOG USERS """
    def save_tartarus_state(self, location):
        list(self.p.query("save_tartarus_state(\'"+location+"\')"))
    
    # It asserts all the associated predicates within the file at location and asserts all the agents and related handler code.
    """ FOR PROLOG USERS """
    def load_tartarus_state(self, location):
        list(self.p.query("load_tartarus_state(\'"+location+"\')"))  

    
    #______________________________FUNCTIONS PERTAINING TO AGENTS_____________________________________

    # Creates mobile agent and adds the mobile handler as a string payload
    def create_mobile_agent(self, Agent_name, Behav_filename, IP, Port, Token_list):
        # Create the appopriate query string
        string = "create_mobile_agent(" + Agent_name + ',' + '( ' + repr(IP) + \
            ',' + str(Port) + '), ' + self.M_Handler + ',' + str(Token_list) + ')'

        # Query using above string
        Lock.acquire()     
        list(self.p.query(string))
        Lock.release()

        # Append to list of Mobile agents
        self.Mobile_agents.append(Agent_name)

        # Add payloads to mobile agent. Payloads are change_handler flag initially set to 0 
        # and next_add set to IP and Port of agent creation. 
        Str = "change_handler(" + Agent_name + " , 0)"   # change_handler flag payload initially set to 0 
        self.p.assertz(Str) 
        Str = "next_add(" + Agent_name + " , " + repr(IP) + " , " + str(Port) + ")"
        self.p.assertz(Str)
        self.add_payload(Agent_name, [("next_add", 3)])
        self.add_payload(Agent_name, [("change_handler", 2)])

        # Make a call to add_behav, to add the handler file as a string payload
        self.add_behav(Agent_name, Behav_filename)

    # Creates static agent and adds the static handler as a string payload
    def create_static_agent(self, Agent_name, Behav_filename, IP, Port, Token_list):
        
        string = "create_static_agent(" + Agent_name + ',' + '( ' + repr(IP) + \
            ',' + str(Port) + '), ' + self.S_Handler + ',' + str(Token_list) + ')'

        # Query using above string
        Lock.acquire()
        list(self.p.query(string))
        Lock.release()

        # Append to list of Static agents
        self.Static_agents.append(Agent_name)

        # Add payloads to static agent. Payloads are change_handler flag initially set to 0 
        Str = "change_handler(" + Agent_name + " , 0)"
        self.p.assertz(Str) 
        self.add_payload(Agent_name,[("change_handler", 2)])

        # Make a call to add_behav, to add the handler file as a string payload
        self.add_behav(Agent_name, Behav_filename)

    # This function is used for starting the executing of an agent which has already been created 
    # (and is not executing) on the specified platform.
    def agent_execute(self, Agent_name, IP, Port, Start_function = "main"):
        # Check the list of agents
        if Agent_name in self.Static_agents:
            Handler = self.S_Handler
        else:
            Handler = self.M_Handler
        
        # Form the agent_execute query
        string = "agent_execute(" + Agent_name + ',' + \
            '(' + repr(IP) + ',' + str(Port) + '),' + \
            Handler + ',' + Start_function + ')'
        
        # Query the above string
        Lock.acquire()
        list(self.p.query(string))
        Lock.release()

    # Adds token to an agent's tokenlist 
    def add_token(self, Agent_name, Token_List):
        string = "add_token(" + Agent_name + ',' + str(Token_List) + ')'
        list(self.p.query(string))

    # 'purge_agent' kills an agent and releases all resources used by the agent
    def purge_agent(self, Agent_name, port = None):
        string = "purge_agent(" + Agent_name + ')'
        if port is None:
            Lock.acquire()
            list(self.p.query(string))
            Lock.release()
        else:
            string = "query : " + string
            self.to_tarpy(port, string)

    # 'add_payload' adds a payload to the agent
    def add_payload(self, Agent_name, Variable_name, port = None):
        
        if type(Variable_name) == str: 
            Variable_List = [(Variable_name, 2)]
        else:
            Variable_List = Variable_name
        string = "add_payload(" + Agent_name + ',' + str(Variable_List) + ')'
        
        if port is None:
            Lock.acquire()
            list(self.p.query(string))
            Lock.release()
        else:
            string = "query : " + string
            return self.to_tarpy(port, string)
        
    # 'remove_payload" removes a payload from the agent
    def remove_payload(self, Agent_name, Variable_name, port = None):

        if type(Variable_name) == str: 
            Variable_List = [(Variable_name, 2)]
        else:
            Variable_List = Variable_name
        string = "remove_payload(" + Agent_name + ',' + str(Variable_List) + ')'
        
        if port is None:
            list(self.p.query(string))
        else:
            string = "query : " + string
            return self.to_tarpy(port,string)

    # Clone agent is a functionality that replicates the entire behaviour of agent on a destination platform and executes there
    def clone_agent(self, Agent_name, Dest_IP, Dest_Port, Curr_Port = None):
        
        if Curr_Port is None:
            Lock.acquire()
            self.p.retractall("next_add( "+ Agent_name + ", _ , _ )")
            Str = "next_add( " + Agent_name + " , " + repr(Dest_IP) + " , " + str(Dest_Port) + " )"        
            self.p.assertz(Str)
            string = "clone_agent(" + Agent_name + ',( ' + repr(Dest_IP) + ',' + str(Dest_Port) + '),Clone_name)'
            for Clone in self.p.query(string):            
                name =  Clone['Clone_name']
                break
            self.p.retractall("next_add( "+ Agent_name + ", _ , _ )")
            Lock.release()
            return name
            
        else:
            # first storing the agents next_IP and next_add
            Str = "query : next_add("+ Agent_name + " , X , Y )"
            add = self.to_tarpy(Curr_Port, Str)

            # now updating the next_add with the address where the 
            # agent needs to be cloned  
            Str = "retractall : next_add( " + Agent_name + " , _ , _ )"
            self.to_tarpy(Curr_Port, Str)
            Str = "assert : next_add( " + Agent_name + " , " + repr(Dest_IP) + " , " + str(Dest_Port) + " )"        
            self.to_tarpy(Curr_Port, Str)

            # now calling the clone_agent function of the tartarus.
            string = "query : clone_agent(" + Agent_name + ",( " + repr(Dest_IP) + "," + str(Dest_Port) + "),Clone_name)"
            name =  self.to_tarpy(Curr_Port,string)
            
            # after cloning the agent, the next add which we updated for the 
            # agent, need to be changed back to its original address.
            Str = "retractall : next_add( " + Agent_name + " , _ , _ )"
            self.to_tarpy(Curr_Port, Str)
            Str = "assert : next_add( " + Agent_name + " , " + add[0] + " , " + str(add[1]) + " )"        
            self.to_tarpy(Curr_Port, Str)
            return name
            
    # This predicate is used to save all the predicates, payload and facts associated with the agent named Agent_name specified by user.
    def save_agent(self, Agent_name, Filename):
        string = "agent_save(" + Agent_name + ',\''+Filename+'\')'
        list(self.p.query(string))

    # 'list_agent' function lists all agents existing in the current platform along with details of the 
    # agent viz. - its name, handler and port number on which agent resides.
    def list_agent(self, port = None):
        if port is None:
            Lock.acquire()
            list(self.p.query("list_agent"))
            Lock.release()
        else:
            self.to_tarpy(port, "query : list_agent")

    # 'isexist_agent' function checks if any agent exists with the name provided within the predicate.
    def isexist_agent(self,Agent_name, IP = "IP", Port = "Port", Handler = "Handler"):
        string = "isexist_agent(" + Agent_name + ',(' + \
            repr(IP) + ',' + str(Port) + '),' + Handler + ')' 
        if list(self.p.query(string)) == []:
            return False
        return True

    # 'move_agent' function is used for mobility of agents the agent named Agent_name is moved to Receiver_ip 
    # and Receiver_port specified by user. 
    def move_agent(self, Agent_name, Receiver_ip, Receiver_port, Port = None):
        # First adding the next_add as payload in the knowledge base      
        if Port is None:
            # Now, moving the agent
            Lock.acquire()
            self.p.retractall("next_add( "+ Agent_name + ", _ , _ )")
            Str = "next_add( " + Agent_name + " , " + repr(Receiver_ip) + " , " + str(Receiver_port) + " )"        
            self.p.assertz(Str)
            string = "move_agent(" + Agent_name + ',(' + repr(Receiver_ip) + \
                ',' + str(Receiver_port) + '))'
            list(self.p.query(string))
            Lock.release()
        
        else:
            # dont call "assign_val" function with variable name next_add here because then Ip and Port will be in a list.
            Str = "retractall : next_add( " + Agent_name + " , _ , _ )"
            self.to_tarpy(Port, Str)
            Str = "assert : next_add( " + Agent_name + " , " + repr(Receiver_ip) + " , " + str(Receiver_port) + " )"        
            self.to_tarpy(Port, Str)

    # Post_agent requires assertion and execution of a Prolog Rule, which is tricky for a Python user
    # Thus, this function is left for future use..
    #____________________________________FUTURE USE_________________________________________________________
    def post_agent(self,Receiver_ip, Receiver_port, Predlist):
        #post_agent(platform, (IP, 50000), [add, _, (IP, 50000), [IP, 50002]]).
        Plist = "["
        count = 0
        for x in Predlist:
            if count != 0 :
                Plist += "," 
            Plist += str(x)
            count += 1
        Plist += "]"
        string = "post_agent( platform, (" + repr(Receiver_ip) + ',' + str(Receiver_port) + ")," + Plist + ')'
        #print(string)
        list(self.p.query(string))


    #______________________________FUNCTIONS PERTAINING TO LOG SERVER_____________________________________

    # 'set_log_server' function is used for setting the IP address and Port number of a log server.
    # Log servers are usually set up in platforms and not agent handlers
    def set_log_server(self, IP, Port):
        list(self.p.query("set_log_server(" + repr(IP) + ',' + str(Port) + ')'))
    
    # 'send_log' function is used by agents to send log messages to log server. 
    # The log server displays these messages on its terminal.
    def send_log(self, Agent_name, Message, Port = None):
        if Port is not None:
            String = "query : send_log(" + Agent_name + ',' + repr(Message) + ')'
            self.to_tarpy(Port, String)
        else:
            list(self.p.query("send_log(" + Agent_name + ',' + repr(Message) + ')'))


    #_________________________________Miscellaneous functions_______________________________________
    def get_new_name(self, Agent_name):
        for x in self.p.query("get_new_name(" + Agent_name +',New_agent_name )'):
            return x['New_agent_name']

    def get_new_name_alpha(self):
        for x in self.p.query("get_new_name_alpha(New_Agent_name)"):
            return x['New_Agent_name']

    def tts(self, Message):
        list(self.p.query("tts(" + Message + ')'))

    def tts_off(self):
        list(self.p.query("tts_off"))


    def tts_on(self):
        list(self.p.query("tts_on"))


    def subt_off(self):
        list(self.p.query("subt_off"))


    def subt_on(self):
        list(self.p.query("subt_on"))


    def ledOn(self, Pin):
        for x in self.p.query("ledOn(" + str(Pin) + ', Status)'):
            return x['Status']

    def ledOff(self, Pin):
        for x in self.p.query("ledOff(" + str(Pin) + ', Status)'):
            return x['Status']


    def mpu6050(self, Reading = None):
        string = "mpu6050( "
        if Reading:
            string += Reading + ','
        string += 'Result)'
        for Res in self.p.query(string):
            return Res['Result']


    def servo(self, Pin, Fr, Start):
        string = "servo( " + str(Pin) + ',' + str(Fr) + ',' + str(Start) + ',Result)'
        for res in self.p.query(string):
            return res['Result']

    # 'hop_times' function has some issues as said by Shubham
    def hop_times(self, Agent = None):
        string = "hop_times("
        if Agent:
            string += Agent + ','
        string += 'Hoptime )'
        Res = list(self.p.query(string))
        return Res
        

    def verbose(self, variable):
        list(self.p.query("verbose(" + str(variable) + ')'))


    #-----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------

    #-----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------
    #-----------------------------------------------------------------------------


    # Additional functions 
    
    #   1.  add_behav/3
    #   2.  assert/2
    #   3.  retract/2 [ no need to use ]
    #   4.  retractall/2
    #   5.  get_val/2
    #   6.  change_behav/5
    #   7.  add_val/4
    #   8.  remove_val/4
    #   9.  assign_val/4


    #   Some more functions are written below but they are not numbered because those are 
    #   not used by the user.

    '''
    1. add_behav/3 :- 

        It is required before executing the agent, because the functionality of the agents is binded
        with this function call.

        There are 2 strings added as a payload each having its own importance
        1. handler code written in file(Code_filename) is added as a string in a predicate code_string
        2. We may need to read the changed handler file again to have the modified handler. 
        For that we have a string in predicated extract_data
    '''

    def add_behav(self, Agent_name, Code_filename):
        
        # 1st part(code_string) - For Python handler 
        # Read the file having the Python handler
        file1 = open(Code_filename,"r")
        handlr_code = file1.read()
        file1.close()

        # Replace all single quotes as they might cause issue
        handlr_code = handlr_code.replace("\'", "\\'")

        # Add the file as a string to a predicate 'code_string'
        string = "code_string(" + Agent_name + ",'" + handlr_code + "' )"
        self.p.assertz(string)
        self.add_payload(Agent_name, [("code_string", 2)])
        
        # 2nd part(extract_handler) - For changing handler
        extract_handler_code = "file2 = open(\"new_behav.py\",\"r\")\ns = file2.read()\nfile2.close()\nprint(s)\n"
        string = "extract_handler(" + Agent_name + ",'" + extract_handler_code + "' )"
        self.p.assertz(string)
        self.add_payload(Agent_name, [("extract_handler", 2)])
    

    '''
    2.  assertz/3 :-

        1.  Below function takes a string as an input which is just a predicate that 
            needs to be asserted to the platform.

    '''   

    def assertz(self, Agent_name, set_name, list_of_val, port = None):
        if port is None:
            Query = self.eval_query(Agent_name,set_name, list_of_val)
            self.p.assertz(Query)

        else:
            Query = self.eval_query(Agent_name,set_name, list_of_val)
            Str = "assert : " + Query
            #print(Str)
            return self.to_tarpy(port, Str)


    '''
    3.  retract/3 :-

        1.  Below function takes a string as an input which is just a predicate that 
            needs to be retracted from the platform.
            
    '''    
    
    def retract(self, Agent_name, set_name, port = None):
        if port is None:
            Query = self.eval_query(Agent_name, set_name,"_")
            #print(Query)
            self.p.retract(Query)
        else:
            Query = self.eval_query(Agent_name, set_name,"_")
            Str = "retract : " + Query
            return self.to_tarpy(port, Str)
    
    '''
    4.  retractall/3 :-

        1.  Below function takes a string as an input which is just a predicate that 
            needs to be retracted from the platform.
            
    '''

    def retractall(self, Agent_name, set_name, port = None):
        if port is None:
            Query = self.eval_query(Agent_name, set_name, "_")
            self.p.retractall(Query)
        else:
            Query = self.eval_query(Agent_name, set_name, "_")
            Str = "retractall : " + Query
            return self.to_tarpy(port, Str)
    '''
    5.  get_val/2 :-

        1.  Below function takes a string as an input which is just a predicate, 
            the variable's value is extracted and then returned as a list.
            
    '''
        
    def get_val(self, Agent_name, set_name, port = None, asserted_from_tarpy = True):
        if port is None :
            # Structure the query using eval_query
            Query = self.eval_query(Agent_name, set_name, "X")

            # Add mutex to prevent agent process conflicts
            Query = "mutex_acquire, " + Query + ", mutex_release"

            # Query
            Lock.acquire()
            List = list(self.p.query(Query))
            Lock.release()
            if List != [{}] and List != []:
                return self.extract_output(List, asserted_from_tarpy)

        else:
            Str = "query : mutex_acquire"
            Query = self.eval_query(Agent_name, set_name, "X")
            #print(Query)
            Str = Str + ", " + Query + ", mutex_release"
            temp = self.to_tarpy(port, Str, asserted_from_tarpy)
            return temp
    

    '''
    
    6.  change_behav/3 :-

        1.  This function sets the value of the change_handler, the value is passed
            as a argument named 'flag'.
        2.  The default value of the flag is 0. which means handler need not to be changed.
        
    '''
    def change_behav(self, Agent_name, Port = None):

        # Port is not None : shows that this function is called from handler
        if Port is not None:
            Str = "retractall : change_handler( " + Agent_name + " , _)"
            self.to_tarpy(Port, Str)
            Str = "assert : change_handler( " + Agent_name + " , 1)"
            self.to_tarpy(Port, Str)

        # else this function is called from local node
        else:
            Str = "change_handler( " + Agent_name + " , _)"
            self.p.retractall(Str)
            Str = "change_handler( " + Agent_name + " , 1)"
            self.p.assertz(Str)

    '''

    # eval_query /3 :- 


    '''
    def eval_query(self, Agent_name, set_name, list_of_val = []):
        # First the set_name alongwith opening bracket
        Query = set_name + "("

        # Check if agent name is mentioned. If not, it's meant for platform and not agent
        if Agent_name != "":
            Query = Query + Agent_name + ", "
        
        # Check if X is present in list_of_values. If yes, that means, it's a value retrieval query
        if list_of_val == "X":
            Query += "X)"
        
        # Check if _ is present in list of values and add 
        elif list_of_val == "_":
            Query += "_)"
        
        # None of the above? Convert the list_of_val to string
        else:
            Query += repr(str(list_of_val)) + ")"
        return Query

    '''
    7.  add_val/4 

        1.  This function adds the value to the variable already present

    '''

    def add_val(self, Agent_name, set_name, list_of_val, port = None, allow_duplicates = False):
        # Get the previous value of the set_name
        val = self.get_val(Agent_name,set_name, port)

        # If duplicates are allowed, simply append
        if allow_duplicates == True:
            val = val + list_of_val
        else:
            # Add elements to list of set_name if not already present
            val = val + [x for x in list_of_val if x not in val]

        # Retract the old values and assert the new values
        self.retractall(Agent_name, set_name,port)
        self.assertz(Agent_name, set_name, val, port)
    
    '''
    8.  remove_val/4 

        1.  This function removes the value from the variable 

    '''
    def remove_val(self, Agent_name, set_name, list_of_val, port = None):
        # Get the list of values from set_name
        val = self.get_val(Agent_name,set_name, port)

        # Keep only those values not present in list_of_val
        val = [x for x in val if x not in list_of_val]

        # Retaract the old list and append the new list to set_name
        self.retractall(Agent_name, set_name,port)
        self.assertz(Agent_name, set_name, val, port)
        
    '''
    9.  assign_val/4 

        1.  This function does not adds or removes, it changes
            the value to the variable. 

    '''
    def assign_val(self, Agent_name, set_name, list_of_val, port = None):
        if port is None:
            # First retract old value and then assert the new set of value
            Query1 = self.eval_query(Agent_name, set_name, "_")
            Query2 = self.eval_query(Agent_name, set_name, list_of_val)

            # Add mutex lock and release. Retract all previous values and assert new value
            Query = "mutex_acquire, retract_assert_tarpy(" + Query1 + ", " + Query2 + "), mutex_release"

            # Query the above operation
            Lock.acquire()
            list(self.p.query(Query))
            Lock.release()
        else:
            # Same process, but send the query via to_tarpy, as it's from agent_handler process
            Query1 = self.eval_query(Agent_name, set_name, "_")
            Query2 = self.eval_query(Agent_name, set_name, list_of_val)
            Query = "mutex_acquire, retract_assert_tarpy(" + Query1 + ", " + Query2 + "), mutex_release"
            Str = "query : " + Query
            return self.to_tarpy(port, Str)

    '''
   
    # to_tarpy/2 :-

        1.  This function is called by the multiple user functions which
            wants to send the message to the local node. 
        2.  To connect with the server, we require host and port.
            Since host is a localhost always, only port is passed as a argument in the function.
        3.  The last argument is the message, which the handler passes to the server.
    '''

    def to_tarpy(self, port, message, asserted_from_tarpy = True, raw_operation = False):
        global Lock
        host = '127.0.0.1'  # Platform server runs on IP = "127.0.0.1"
        ClientSocket = socket.socket()  # Create a client socket
        message = message + " : " + str(raw_operation)  # Attach the flag of raw_operation with message
        Client_Lock.acquire()
        try:
            ClientSocket.connect((host, port + 1))  # Try to establish a connection with platform
            _ = ClientSocket.recv(2048)             # Recieve a dummy message from server
            ClientSocket.send(str.encode(message))  # Send the message to server in encoded form
            enc_Response = ClientSocket.recv(2048)  # Recieve the response in encoded form
            dec_Response = enc_Response.decode('utf-8') # Decode the response
            ClientSocket.close()    # Close the connection
        except socket.error as e:
            print(str(e))
        except Exception:
            print('Failed')

        finally:
            Client_Lock.release()
            if dec_Response != "Assertion Successfull" and  dec_Response != "Retraction Successfull" and dec_Response != "Wrong Format":
                # Here? That means that this was a query
                if asserted_from_tarpy == True: # If asserted from Tarpy, then eval the response
                    Op = ast.literal_eval(dec_Response)
                else:
                    Op = dec_Response   # Else, take the raw response
                if Op != [{}]:  # If response is not empty, return the output after extracting
                    return self.extract_output(Op, asserted_from_tarpy)

    '''
    # extract_output/1 :- Used to extract the output from List of dictionaries and returns a list of values.

    '''

    def extract_output(self, List, asserted_from_tarpy = True):
            
            # This condition will check if the output
            # is it is from the query next_add or clone_Agent
            # then if condition part will get execute else the second one.
            if type(List[0]) == str:
                data = List[0]
            else:
                data = List[0]["X"]

            # below code handles the exception of the variable 'data'
            # since 'data' can be byte instead of string and in that
            # case we then need to decode it.  

            try:
                data = data.decode()
            except (UnicodeDecodeError, AttributeError):
                pass
            if asserted_from_tarpy == True:
                List =  ast.literal_eval(data)
            else:
                List = data
            return List      

    '''
    10.  keep_alive/0 

        1.  This function makes platform running till user give input 
            "halt"
        2.  The user or developer who knows prolog can use prolog features
            can query the knowldege base.    

    '''

    def keep_alive(self):

        while True:
            ip = input("enter 'halt' to exit: \n")
            if ip == 'halt':
                break
            Lock.acquire()
            list(self.p.query(ip))
            Lock.release()

    #-------------------------------------------------------
    #--------------------Multi Threading Part---------------
    #-------------------------------------------------------


    '''
    #   agent_thread/1 :- 

        1.  The below function gets active when some agent 
            visits the platform(tartarus) and wants to communicate
            with the tartarus.

        2.  This function is responsible for the output which agent 
            recieves.
    '''

    def agent_thread(self,connection):
        global Lock
        connection.send(str.encode('Welcome to the Server')) #this line is mandatory, some sort of string as a ack is required.    
        enc_data = connection.recv(2048)
        data = enc_data.decode('utf-8')
        reply = self.evaluate(data)
        connection.sendall(str.encode(reply))
        connection.close()


    '''
        1.  Below message/1 function parse the message, send by the agent.
        
        2.  There can be 3 types of messages :
            1.  Assert  ( eg -> "assert : num(2)"   )
            2.  Retract ( eg -> "retract : num(2)"  )
            3.  Query   ( eg -> "query : num(X)"    )

    '''
    # A function to parse the message recieved from agent
    def evaluate(self, msg):
        # Split the message first into types
        lst = msg.split(" : ")

        # lst[1] contains the actual operation

        # Get the boolean value of whether raw or not
        raw = eval(lst[2])
        Lock.acquire()

        # If query type is assert, Assert the message and return successful
        if lst[0] == 'assert':        
            self.p.assertz(lst[1])
            Lock.release()
            return "Assertion Successfull"

        # Elif query type is retract, Retract the contents of lst[1] and return successful
        elif lst[0] == 'retract':
            self.p.retract(lst[1])
            Lock.release()
            return "Retraction Successfull"
        
        # Elif query type is retractall, Retract all the contents of lst[1] and return successful
        elif lst[0] == 'retractall':
            self.p.retractall(lst[1])
            Lock.release()
            return "Retraction Successfull"
        
        # Elif query operation, then parse the query and perform operations
        elif lst[0] == 'query':
            if raw == False:
                parsed_query = lst[1].split("(",1)
                set_name = parsed_query[0]
            else:
                set_name = lst[1]
            if set_name == "clone_agent":
                for Clone in self.p.query(lst[1]):            
                    name = Clone['Clone_name']
                    op = [str([name])]
                    Lock.release()
                    return str(op)
            if set_name == "next_add":                
                for op in self.p.query(lst[1]):
                    lst = [op['X'], op['Y']]
                    op = [str(lst)]
                    Lock.release()
                    return str(op)                    
            else:
                op = str(list(self.p.query(lst[1])))
                Lock.release()
                return op
        else:
            Lock.release()
            return "Wrong Format"
        

    '''

            server_thread implements the functionality of the server.
            it keeps running in a loop, waiting for a agent. when agent 
            comes it starts new thread and in that thread they communicate
            with each other making this socket available for other agents
            to work parallely.
    '''
    
    def server_thread(self, host, port, agents):    
        
        global ServerSocket
        ServerSocket = socket.socket()                      # Socket creation
        try:
            ServerSocket.bind((host, port))                 # Bind socket
        except socket.error as e:
            print(str(e))
        ServerSocket.listen(agents)                         # Listen for active connections

        # Run in an infinite loop
        while True:
            Agent, _ = ServerSocket.accept()                # Accept connections. Blocking call
            start_new_thread(self.agent_thread, (Agent, ))  # Create a new thread that servers the client request

    #-------------------------------------------------------
    #--------------------Multi Threading Part Ended---------
    #-------------------------------------------------------
