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
    % if u.assist_buildable_only:
      <li>Can only assist building items it can build</li>
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
