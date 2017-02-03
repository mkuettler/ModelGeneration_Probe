#!/usr/bin/env python2

from __future__ import print_function

import sys
import os
import subprocess
import argparse
import createModel

def usage():
    print(sys.argv[0] + " <lua script>", file=sys.stderr)

class Cap:
    def __init__(self, id, access):
        self.id = id
        self.access = access

class Process:
    def __init__(self, name, caps=None):
        self.name = name
        self.caps = caps or dict()
        self.runtime = 0
        self.prob_send = 0
        self.prob_target = {}


def parse_lines(lines):
    processes = []
    process = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        words = [w.strip() for w in line.split('\t')]

        if words[0] == "Command":
            if process:
                processes.append(process)
            process = Process(words[1])
        elif words[0] == "Cap":
            process.caps[words[1]] = Cap(int(words[2]), words[3])
        elif words[0] == "Runtime":
            process.runtime = int(words[1])
        elif words[0] == "prob_send":
            process.prob_send = float(words[1])
        elif words[0] == "prob_target":
            process.prob_target[words[1]] = float(words[2])

    if process:
        processes.append(process)

    return processes

def parse_file(filename):
    with file(filename, "r") as f:
        return parse_lines(f.readlines())

def parse_script(filename):
    lines = subprocess.check_output(["lua5.3", "extract.lua", filename]).split("\n")
    return parse_lines(lines)

def create_model(processes,args):
    model = createModel.main(processes,args)
    return model
   


def dump_process_list(processes):
    for p in processes:
        print ("Process", p.name)
        for n, e in p.caps.items():
            print ("  cap", n, e.id, e.access)
        print ("  runtime", p.runtime)
        print ("  prob_send", p.prob_send)
        for n, prob in p.prob_target.items():
            print ("  prob_target", n, prob)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Tool to extract Information about processes and capabilities and runtime/sending annotations from ned (lua) script.")
    parser.add_argument("file", metavar="FILE", help="The lua script, or a file containing extracted information from the script (depends on -e/-f option)", type=str)
    parser.add_argument("--extract", "-e", action="store_true", dest="script", help="Extract information from lua script", default=True)
    parser.add_argument("--data-file", "-f", action="store_false", dest="script", help="Use already extracted information")
    parser.add_argument("--error-prob", "-p", action="store", dest="error_prob", help="Probability for an error in the IPC data structures in one time unit",
                          default=1e-7, type=float)
    parser.add_argument("--detectable-prob", "-d", action="store", dest="detectable_prob", help="Probability for an error to be a detectable",
                          default=0.99, type=float)
    #parser.add_argument("--undetectable-prob", "-u", action="store", dest="undetectable_prob", help="Probability for an error to be a undetectable",
    #                      default=0.01, type=float)
    parser.add_argument("--model-output", metavar="FILE", dest="mf", help="Output file for the PRISM model",
                          default="PRISM_model.prism", type=str)

    args = parser.parse_args()
    args.undetectable_prob = 1 - args.detectable_prob

    if args.script:
        processes = parse_script(args.file)
    else:
        processes = parse_file(args.file)
    
    model = create_model(processes,args)
    model_file = open(args.mf, 'w')
    model_file.write(model)
    
    
    print("Error probability:", args.error_prob)
    print("Detectable probability:", args.detectable_prob)
    print("Undetectable probability:", args.undetectable_prob)
    dump_process_list(processes)

