<li><div class='heading'>Physics:</div>
  <ul>
    <li>Max speed: {{u.move_speed}}</li>
    <li>Acceleration: {{u.turn_speed}}</li>
    <li>Braking rate: {{u.brake}}</li>
    <li>Turn rate: {{u.turn_speed}}</li>
    % if u.amphibious:
      <li>Amphibious</li>
    % end
    % if u.hover:
      <li>Hovering</li>
    % end
  </ul>
</li>
