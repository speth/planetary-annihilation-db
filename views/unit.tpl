<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>PADB - {{u.name}}</title>
    <link rel="stylesheet" href="/static/site.css">
  </head>
  <body>
    % if u.name == u.role:
    <h1>{{u.name}}</h1>
    % else:
    <h1>{{u.role}}: <em>{{u.name}}</em></h1>
    % end
    {{u.description}}
    <ul>
      <li>HP: {{u.health}}</li>
      <li>Build cost: {{u.build_cost}} metal</li>
      <li>Built by:
        <ul>
          % for other in u.built_by:
          <li> <a href="/unit/{{other.safename}}">
          % if other.name == other.role:
          {{other.name}}
          % else:
          {{other.role}}: <em>{{other.name}}</em>
          % end
          </a></li>
          % end
        </ul>
      </li>
      % if u.affects_economy:
      <li>Economy:
        <ul>
          % if u.production.metal:
          <li>Metal production: {{u.production.metal}} / s
          % end
          % if u.production.energy:
          <li>Energy production: {{u.production.energy}} / s
          % end
          % if u.consumption.metal:
          <li>Base metal consumption: {{u.consumption.metal}} / s
          % end
          % if u.consumption.energy:
          <li>Base energy consumption: {{u.consumption.energy}} / s
          % end
          % if u.storage.metal:
          <li>Metal storage: {{u.storage.metal}}
          % end
          % if u.storage.energy:
          <li>Energy storage: {{u.storage.energy}}
          % end
          % if u.weapon_consumption.metal:
          <li>Weapon metal consumption: {{u.weapon_consumption.metal}} / s
          % end
          % if u.weapon_consumption.energy:
          <li>Weapon energy consumption: {{u.weapon_consumption.energy}} / s
          % end
          % if u.build_rate:
          <li>Build rate: {{u.build_rate}}
          % end
          % if u.tool_consumption.metal:
          <li>Fabrication metal consumption: {{u.tool_consumption.metal}} / s
          % end
          % if u.tool_consumption.energy:
          <li>Fabrication energy consumption: {{u.tool_consumption.energy}} / s
          % end
        </ul>
      </li>
      % end
      % if u.builds:
      <li>Builds:
        <ul>
          % for other in u.builds:
          <li><a href="/unit/{{other.safename}}">
          % if other.name == other.role:
          {{other.name}}
          % else:
          {{other.role}}: <em>{{other.name}}</em>
          % end
          </a></li>
          % end
        </ul>
      </li>
      % end
      % if len(u.weapons) > 1:
        <li>Maximum range: {{max(w.max_range for w in u.weapons)}}</li>
        <li>Total DPS: {{u.dps}}</li>
      % end
      % for i, w in enumerate(u.weapons):
        % if len(u.weapons) > 1:
          <li>Weapon {{i+1}}:</li>
        % else:
          <li>Weapon:</li>
        % end
        <ul>
          <li>Range: {{w.max_range}}</li>
          <li>Damage: {{w.dps}} DPS: {{w.damage}} damage every {{1/w.rof}} seconds ({{w.rof}} shots per second)</li>
          % if w.splash_damage:
            <li>Splash: {{w.splash_damage}} damage, radius {{w.splash_radius}}</li>
          % end
          % if w.metal_per_shot:
            <li>Metal consumption: {{w.metal_per_shot}} per shot ({{w.metal_per_shot * w.rof}} per second)</li>
          % end
          % if w.energy_per_shot:
            <li>Energy consumption: {{w.energy_per_shot}} per shot ({{w.energy_per_shot * w.rof}} per second)</li>
          % end
        </ul>
      % end
    </ul>
  </body>
</html>
