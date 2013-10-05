% import webunits

<div style="width: 100%; overflow: hidden;">
  % if have_icon:
    <div style="width: 60px; float: left; margin-top:14px">
      <img src=/build_icons/{{u.safename}} />
    </div>
    <div style="margin-left: 72px;">
  % else:
    <div>
  % end
      <h1>
        % if u.name == u.role:
          {{u.name}}
        % else:
          {{u.role}}: <em>{{u.name}}</em>
        % end
      </h1>
      <em>{{u.description}}</em>
    </div>
</div>
<ul>
  <li>HP: {{u.health}}</li>
  <li>Build cost: {{u.build_cost}} metal</li>
  % if len(u.weapons) > 1:
    <li>Maximum range: {{max(w.max_range for w in u.weapons)}}</li>
    <li>Total DPS: {{u.dps}}</li>
  % end
  % if 'Mobile' in u.unit_types:
    <br />
    <li><div class='heading'>Physics:</div>
      <ul>
        <li>Max speed: {{u.move_speed}}</li>
        <li>Acceleration: {{u.turn_speed}}</li>
        <li>Braking rate: {{u.brake}}</li>
        <li>Turn rate: {{u.turn_speed}}</li>
      </ul>
    </li>
  % end
  <br />
  <li><div class='heading'>Recon:</div>
    <ul>
      % if u.vision_radius:
        <li>Vision radius: {{u.vision_radius}}</li>
      % end
      % if u.underwater_vision_radius:
        <li>Underwater vision radius: {{u.underwater_vision_radius}}</li>
      % end
      % if u.radar_radius:
        <li>Radar radius: {{u.radar_radius}}</li>
      % end
      % if u.sonar_radius:
        <li>Sonar radius: {{u.sonar_radius}}</li>
      % end
    </ul>
  </li>
  % if u.affects_economy:
    <br />
    <li><div class='heading'>Economy:</div>
      <ul>
        % if u.production.metal:
          <li>Metal production: {{u.production.metal}} / s</li>
        % end
        % if u.production.energy:
          <li>Energy production: {{u.production.energy}} / s</li>
        % end
        % if u.consumption.metal:
          <li>Base metal consumption: {{u.consumption.metal}} / s</li>
        % end
        % if u.consumption.energy:
          <li>Base energy consumption: {{u.consumption.energy}} / s</li>
        % end
        % if u.storage.metal:
          <li>Metal storage: {{u.storage.metal}}</li>
        % end
        % if u.storage.energy:
          <li>Energy storage: {{u.storage.energy}}</li>
        % end
        % if u.weapon_consumption.metal:
          <li>Weapon metal consumption: {{u.weapon_consumption.metal}} / s</li>
        % end
        % if u.weapon_consumption.energy:
          <li>Weapon energy consumption: {{u.weapon_consumption.energy}} / s</li>
        % end
        % if u.build_rate:
          <li>Build rate: {{u.build_rate}}</li>
        % end
        % if u.tool_consumption.metal:
          <li>Fabrication metal consumption: {{u.tool_consumption.metal}} / s</li>
        % end
        % if u.tool_consumption.energy:
          <li>Fabrication energy consumption: {{u.tool_consumption.energy}} / s</li>
        % end
        % if u.tool_consumption.metal:
          <li>Energy consumption per metal: {{'{:.1f}'.format(u.build_inefficiency)}}</li>
        % end
      </ul>
    </li>
  % end
  % if u.weapons:
    <br />
  % end
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
    </ul>
  % end
  % if u.builds:
  <br />
  <li>
    <div class='heading'>Builds:</div>
    <ul>
      % for other in u.builds:
        <li>
          % include unit_link unit=other
          % if u.build_rate and other.build_cost:
            ({{webunits.timestr(other.build_cost / u.build_rate)}})
          % end
        </li>
      % end
    </ul>
  </li>
  % end
  % if u.built_by:
    <br />
    <li>
      <div class='heading'>Built by:</div>
      <ul>
        % for other in u.built_by:
        <li>
          % include unit_link unit=other
          % if other.build_rate:
            ({{webunits.timestr(u.build_cost / other.build_rate)}})
          % end
        </li>
        % end
      </ul>
    </li>
  % end
</ul>
% rebase page
