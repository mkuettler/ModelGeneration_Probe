
-- load this here, so we can access the application list
local L4 = require "L4"

-- execute the config script
print = function () end
dofile(arg[1])

for id, err in pairs(L4.error_cap_targets) do
   L4.report_data("Error-Cap-Target", id, err)
end

for i, app in pairs(L4.applications) do
   L4.report_data("Command", app.cmd)
   for n, e in pairs(app.caps or {}) do
      report_data("  Cap", n, e.id, e.role, e.args)
   end
   if app.runtime then
      report_data("  Runtime", app.runtime)
   end
   if app.prob_send then
      report_data("  prob_send", app.prob_send)
   end
   for n, p in pairs(app.prob_message_target or {}) do
      report_data("  prob_target", n, p)
   end
end
