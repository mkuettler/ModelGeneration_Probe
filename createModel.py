#!/usr/local/bin/python

import sys
import math
import os
import copy
import itertools

### TODO List

## reward structure utility
## implement counter to control encode_sending
## implement different errors per ipc gate


from mako.template import Template
from mako.lookup import TemplateLookup

# template call procedures
mylookup = TemplateLookup(directories=[os.path.dirname(os.path.realpath(sys.argv[0]))
])


def serve_template(templatename, **kwargs):
    mytemplate = mylookup.get_template(templatename)
    return mytemplate.render(**kwargs)


def parse_process_inputs(processes, caps):
        
    # After a server received a message, 3 things can happen: 
    # 1. The server can answer the message immediately, and wait for a new message
    # 2. The server can call another server and wait for the answer before answering itself
    # 3. The server can answer the message immediately but still perform a call to another server afterwards (ack)
    # Each process should either always or never send an ack, which is determined by the dictionary <ack>.
    # The choice whether to perform a call after an ack / before answering is either non-deterministic 
    # or probabilistic. Thus, call type is one of (probabilistic,nondeterministic).
    # In case of probabilistic, prob_call gives the probability of performing a(nother) call
    # A processes working time can either be probabilistically (geometrically) distributed or a fixed
    # number of time steps. Furthermore, handling and consumed time can differ for answering a message,
    # sending an new message or sending an ack. 
    # (answer, message, ack)
    for process in processes:
      process.answer_runtime_handling = "fixed"  # one of fixed, probabilistic
      process.call_runtime_handling = "fixed"  # one of fixed, probabilistic
      process.ack_runtime_handling = "fixed"  # one of fixed, probabilistic
      process.answer_time = process.runtime
      process.call_time = process.runtime
      process.ack_time = process.runtime
    
    # sending an ack or sending an answer?
    for process in processes:
      process.ack = False
    # is sending a new message probabilistic or non-deterministic? If probabilistic, what is the probability
    # of sending a new message?
    for process in processes:
      if "server" in [each.access for each in process.caps.values()]:
        process.call_type = "probabilistic" # one of probabilistic, nondeterministic
        process.prob_call = ("often",process.prob_send) # can also be once, then a process is allowed to only send one message, 
                                                         # after this it first must receive a new one

    # if a process sends a new message, is the target channel determined non-determinstic or probabilistic? 
    # if probabilistic, what is the distribution
    for process in processes:
      process.communicate = "probabilistic"
      process.probability_communicate = {}
      for cap in process.caps:
        if cap in process.prob_target.keys():
          process.probability_communicate[process.caps[cap].id] = process.prob_target[cap]

def parse_ipc_inputs(processes,caps):
    furtherinputs = {}
    ## which kinds of errors can occur in which communication channels?
    ## Changing the list is not tested!
    error_cap_list = [(cap_id,error_type) for cap_id in caps.keys() for error_type in ["correctable_error","crash"]]
    furtherinputs["error_cap_list"] = error_cap_list

    # how many errors may occur simultaneously?
    furtherinputs["multiple_errors"] = 1
    if (furtherinputs["multiple_errors"]=="all") or (furtherinputs["multiple_errors"]>len(error_cap_list)):
      furtherinputs["multiple_errors"]=len(error_cap_list)

    # time inputs
    # handling is one of 'fixed', 'expected'
    # caution if set to 0, no errors will happen during IPC transfer (although error effects take place)
    # if set to < 1, no time will elapse during IPC and error probabilities may become to small to 
    # be taken into account.
    furtherinputs["ipc_time_handling"] = "fixed" 
    furtherinputs["ipc_time"] = 0
    
    furtherinputs["repair_time_handling"] = "fixed"
    furtherinputs["repair_time"] = 100
    
    # how long does it take until a crash after some crash-producing error occurs AND a restart is performed after the crash?
    furtherinputs["crash_time_handling"] = "fixed"
    furtherinputs["crash_time"] = 10000  #1s
    
    return furtherinputs

#def parse_error_inputs(processes,caps):

def main(processes,args):
    # we extract a list of capabilities for iteration
    caps = {}
    for process in processes:
      for cap in process.caps:
        if not process.caps[cap].id in caps:
          caps[process.caps[cap].id] = [process.caps[cap].access]
        else:
          caps[process.caps[cap].id].append(process.caps[cap].access) 

    ####################################################################################################
    ####################################################################################################
    ####################################################################################################
    ## MODEL INPUTS
    ####################################################################################################
    ####################################################################################################
    ####################################################################################################
    
    #modelinputs = parse_inputs(processes,caps)
        
    parse_process_inputs(processes,caps)
    furtherinputs = parse_ipc_inputs(processes,caps)
    #error_inputs = parse_error_inputs(processes,caps)
    



    # We model errors per IPC communication channel. Thus, an error may happen somewhere in 
    # the data structures, capability table, or IPC code. We don't care. 
    probability_error_per_timestep = args.error_prob #(10**-7) ##1.5*(10**-11)
    probability_correctable_error_per_timestep = 0
    probability_crash_per_timestep = args.detectable_prob #0.99
    probability_silent_data_corruption_per_timestep = args.undetectable_prob #0.01
        
    
    # During crashes and recovery, error probabilities may be different.
    # Not yet supported, all values need to be 0.
    # TODO add implementation for this -
    probability_correctable_error_per_crash_timestep = 0;
    probability_crash_per_crash_timestep = 0;
    probability_silent_data_corruption_per_crash_timestep = 0;
     
    ## How many utility / time should be countable?
    MAX_utility=1
    MAX_time=1000
    
    
    ####################################################################################################
    ####################################################################################################
    ####################################################################################################
    ## Preprocessing and template calls
    ####################################################################################################
    ####################################################################################################
    ####################################################################################################
    
    # PRISM cannot handle special characters, so we replace them.
    for process in processes:
      process.name = process.name.replace('/','_')
      process.name = process.name.replace('-','__')
    
    # We sort out IPC gates if no process can send to this gate
    caps = {key : value for key, value in caps.iteritems() if value.count("client")>0}
    
    max_IPC_id = max(caps.keys())
    
    
    ## why is this still needed?
    process_is_client = {}
    for process in processes:
      process_is_client[process] = not "server" in [each.access for each in process.caps.values()]
    
    
    # template calls.
    model = ""
    model+= serve_template('Templates/preample.tmpl',processes=processes
                                                  ,max_IPC_id=max_IPC_id
                                                  ,caps=caps
                                                  ,ipc_time_handling=furtherinputs["ipc_time_handling"]
                                                  ,ipc_time=furtherinputs["ipc_time"]
                                                  ,repair_time_handling=furtherinputs["repair_time_handling"]
                                                  ,repair_time=furtherinputs["repair_time"]
                                                  ,crash_time_handling=furtherinputs["crash_time_handling"]
                                                  ,crash_time=furtherinputs["crash_time"]
                                                  ,probability_error_per_timestep=probability_error_per_timestep
                                                  ,probability_correctable_error_per_timestep=probability_correctable_error_per_timestep
                                                  ,probability_crash_per_timestep=probability_crash_per_timestep
                                                  ,probability_silent_data_corruption_per_timestep=probability_silent_data_corruption_per_timestep
                                                  ,probability_correctable_error_per_crash_timestep=probability_correctable_error_per_crash_timestep
                                                  ,probability_crash_per_crash_timestep=probability_crash_per_crash_timestep
                                                  ,probability_silent_data_corruption_per_crash_timestep=probability_silent_data_corruption_per_crash_timestep
    )
    
    model+= serve_template('Templates/ipc.tmpl',processes=processes
                                             ,caps=caps
    )
    model+= serve_template('Templates/processes.tmpl',processes=processes
                                                   ,process_is_client=process_is_client
                                                   ,caps=caps
    )
    
    model+= serve_template('Templates/error.tmpl',processes=processes
                                               ,process_is_client=process_is_client
                                               ,caps=caps
                                               ,error_cap_list=furtherinputs["error_cap_list"]
                                               ,multiple_errors=furtherinputs["multiple_errors"]
    )
    model+=  serve_template('Templates/rewards.tmpl',processes=processes
                                                 ,process_is_client=process_is_client
                                                 ,caps=caps
                                                 ,ipc_time_handling=furtherinputs["ipc_time_handling"]
                                                 ,ipc_time=furtherinputs["ipc_time"]
    )
    model+= serve_template('Templates/utility.tmpl',processes=processes
                                                 ,process_is_client=process_is_client
                                                 ,caps=caps
                                                 ,ipc_time_handling=furtherinputs["ipc_time_handling"]
                                                 ,ipc_time=furtherinputs["ipc_time"]
                                                 ,MAX_utility=MAX_utility
    )
    model+= serve_template('Templates/stop.tmpl')
    
    return model


