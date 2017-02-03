
local L4 = require("L4");

local l = L4.default_loader;

local mc1 = l:new_channel();
local mc2 = l:new_channel();
local sc = l:new_channel();
local con = l:new_channel();

l:start( {caps = {acc = mc1:svr()}, runtime=1, prob_send=0},
	 "rom/measure1");

l:start( {caps = {acc = mc2:svr()}, runtime=1, prob_send=0},
	 "rom/measure2");

l:start( {caps = {m1 = mc1, m2 = mc2, s = sc, con=con:svr()},
	  prob_message_target={m1 = 0.4, m2 = 0.58, s = 0.02},
	  prob_send=0.98, runtime=5},
	 "rom/analysis");

l:start( {caps = {con = con}, runtime=25, prob_send=1},
	 "rom/control");

l:start( {caps = {c = sc:svr()}, runtime=50, prob_send=0},
	 "rom/send");
