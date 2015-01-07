% suffix = '?version='+db.queryversion if db.queryversion else ''
<li><a href='/json/{{u.safename}}{{suffix}}'>Blueprint</a></li>
<li>HP: {{u.health}}</li>
<li>Build cost: {{u.build_cost}} metal</li>
% if u.weapons:
  <li>Maximum range: {{max(w.max_range for w in u.weapons)}}</li>
  <li>Total DPS: {{u.dps}}</li>
% end
