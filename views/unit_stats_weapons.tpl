% import webunits
% for i, w in enumerate(u.weapons):
  % if len(u.weapons) > 1:
    <li><div class='heading'>Weapon {{i+1}}:</div></li>
  % else:
    <li><div class='heading'>Weapon:</div></li>
  % end
  <ul>
    <li>Range: {{w.max_range}}</li>
    <li>Damage: {{w.dps}} DPS: {{w.damage}} damage every {{'{:.2f}'.format(1/w.rof)}} seconds ({{w.rof}} shots per second)</li>
    % if w.splash_damage:
      <li>Splash: {{w.splash_damage}} damage, radius {{w.splash_radius}}</li>
    % end
    % if w.muzzle_velocity:
      <li>Muzzle velocity: {{w.muzzle_velocity}}</li>
    % end
    % if w.metal_per_shot:
      <li>Metal consumption: {{w.metal_per_shot}} per shot ({{w.metal_per_shot * w.rof}} per second)</li>
    % end
    % if w.energy_per_shot:
      <li>Energy consumption: {{w.energy_per_shot}} per shot ({{w.energy_per_shot * w.rof}} per second)</li>
    % end
    % if w.ammo and w.ammo.metal_cost:
      <li>Metal cost: {{w.ammo.metal_cost}} per shot</li>
      <li>Build time: {{webunits.timestr(w.ammo.metal_cost / u.build_rate)}}</li>
    % end
    % if w.target_layers:
      <li>Targets: {{', '.join(w.target_layers)}}</li>
    % end
    <li><a href="/json/{{w.safename}}">Blueprint</a></li>
  </ul>
% end
