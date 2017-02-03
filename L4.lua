
local string = require "string"
local table = require "table"

report_data = print

function report_warning(...)
   report_data("Warning", ...)
end

function report_info(...)
   report_data("Info", ...)
end

----
-- Channel
----

local Channel = {}
Channel.next_id = 1
Channel.__index = Channel -- What does this do? Copied from the Wiki example

function Channel:new(error_targets)
   local id = Channel.next_id
   Channel.next_id = Channel.next_id + 1
   local ch = setmetatable({ id = id, role = "client" }, Channel)
   if error_targets == nil then
      error_targets = {}
   end
   ch.error_targets = error_targets
   return ch
end

function Channel:create(...)
   local new_channel = Channel:new()
   local id = new_channel.id
   if not self.server then
      report_warning("create called on Channel which doesn't have a server")
   else
      self.server.caps["svr".. id] = new_channel:svr()
   end

   new_channel.args = ...
   return new_channel
end

function Channel:svr(...)
   -- deep copy, so that later changes in one cap don't accect the other
   spec = nil
   if self.error_targets then
      targets = {}
      for _, gateid in pairs(self.error_targets) do
         targets[#targets+1] = v
      end
   end
   return {id = self.id, role = "server", channel = self, args = ..., error_targets = targets}
end


----
-- App
----
local App = {}
App.__index = App

function App:new()
   return setmetatable({}, App)
end

function App:wait()
   return 0
end

   applications = {}

   ----
   -- Loader
   ----

   Loader = {}
   Loader.__index = Loader

   function Loader:new()
      return setmetatable({}, Loader)
   end

   function Loader:new_channel()
      return Channel:new()
   end

   function Loader:start(env, cmd, posix_env)
      return self:startv(env, cmd:match("[^%s]+")) -- dropping arguments here; they are not used anyway
   end

   function Loader:startv(env, cmd, ...)
   --   print(unique_str, "Command", cmd)
      local app = App:new()
      app.cmd = cmd
      app.caps = env.caps
      app.prob_send = env.prob_send
      app.runtime = env.runtime
      app.prob_message_target = env.prob_message_target
      table.insert(applications, app)
      for n, e in pairs(env.caps or {}) do
         if e.role == "server" then
            --report_info("server channel registered")
            assert (not e.server)
            e.channel.server = app
         end
         --      report_data("  Cap", n, e.id, e.role, e.args)
      end
      return app
   end

return {

   error_cap_targets = {},

   applications = applications,

   report_data = report_data,

   default_loader = Loader:new(),


   -- cast
   cast = function(type, obj)
      -- remember type here? We don't really need to.
      return obj
   end,


   -- Env: content extracted from lua_env.cc
   Env = {
      parent = Channel.new(),
      mem_alloc = Channel.new(),
      user_factory = mem_alloc, -- from ned.lua
      rm = Channel.new(),
      log = Channel.new(),
      factory = Channel.new(),
      scheduler = Channel.new(),
      -- some caps that are not explicitly listed in lua_env.cc,
      -- but are used in scripts, and probably belong to the initial_caps()
      sigma0 = Channel:new(),
      icu = Channel:new(),
   },


   ----
   -- Constants, copied from ned.lua
   -- We don't care about them, might as well use the correct values
   ----

   -- L4 protocol constants
   Proto = {
      Dataspace = 0x4000,
      Namespace = 0x4001,
      Goos      = 0x4003,
      Mem_alloc = 0x4004,
      Rm        = 0x4005,
      Event     = 0x4006,
      Inhibitor = 0x4007,
      Irq       = -1,
      Sigma0    = -6,
      Log       = -13,
      Scheduler = -14,
      Factory   = -15,
      Ipc_gate  = 0,
   },

   -- L4 rights flags
   Rights = {
      s   = 2,
      w   = 1,
      r   = 4,
      ro  = 4,
      rw  = 5,
      rws = 7,
   },

   -- Ldr flags
   Ldr_flags = {
      eager_map    = 0x1, -- L4RE_AUX_LDR_FLAG_EAGER_MAP
      all_segs_cow = 0x2, -- L4RE_AUX_LDR_FLAG_ALL_SEGS_COW
      pinned_segs  = 0x4, -- L4RE_AUX_LDR_FLAG_PINNED_SEGS
   },

   -- Flags for dataspace allocation via user_factory
   -- NOTE: keep constants in sync with l4re/include/mem_alloc
   Mem_alloc_flags = {
      Continuous  = 1,
      Pinned      = 2,
      Super_pages = 4,
   },

   -- L4Re debug constants
   Dbg = {
      Info       = 1,
      Warn       = 2,
      Boot       = 4,
      Server     = 0x10,
      Exceptions = 0x20,
      Cmd_line   = 0x40,
      Loader     = 0x80,
      Name_space = 0x400,
      All        = 0xffffffff,
   },

}
