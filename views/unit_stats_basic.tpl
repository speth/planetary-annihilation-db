<li><a href='/json/{{u.safename}}'>Blueprint</a></li>
<li>HP: {{u.health}}</li>
<li>Build cost: {{u.build_cost}} metal</li>
% if len(u.weapons) > 1:
  <li>Maximum range: {{max(w.max_range for w in u.weapons)}}</li>
  <li>Total DPS: {{u.dps}}</li>
% end
