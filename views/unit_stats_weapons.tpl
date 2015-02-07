% import webunits
% suffix = '?version='+db.queryversion if db.queryversion else ''
% for i, w in enumerate(u.weapons):
  % if w.self_destruct:
    <li><div class='heading'>Self Destruct:</div></li>
  % elif w.death_explosion:
    <li><div class='heading'>Death Explosion:</div></li>
  % else:
    % N = " #{}".format(i+1) if len(u.weapons) > 1 else ""
    % Q = " (x{})".format(w.count) if w.count > 1 else ""
    <li><div class='heading'>Weapon{{N}}{{Q}}:</div></li>
  % end
  <ul>
    % if w.max_range:
      <li>Range: {{w.max_range}}</li>
    % end
    % if not w.self_destruct and not w.death_explosion:
      <li>Damage: {{w.dps}} DPS: {{w.damage}} damage every {{'{:.2f}'.format(1/w.rof)}} seconds ({{w.rof}} shots per second)</li>
    % else:
      <li>Damage: {{w.damage}}</li>
    % end
    % if w.full_damage_radius:
      <li>Full damage radius: {{w.full_damage_radius}}</li>
    % end
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
    <li><a href="/json/{{w.safename}}{{suffix}}">Blueprint</a></li>
  </ul>
% end
