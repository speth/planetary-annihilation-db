  <li><div class='heading'>Recon:</div>
    <ul>
      % if u.vision_radius:
        <li>Vision radius: {{u.vision_radius}}</li>
      % end
      % if u.underwater_vision_radius:
        <li>Underwater vision radius: {{u.underwater_vision_radius}}</li>
      % end
      % if u.orbital_vision_radius:
        <li>Orbital vision radius: {{u.orbital_vision_radius}}</li>
      % end
      % if u.mine_vision_radius:
        <li>Mine vision radius: {{u.mine_vision_radius}}</li>
      % end
      % if u.radar_radius:
        <li>Radar radius: {{u.radar_radius}}</li>
      % end
      % if u.sonar_radius:
        <li>Sonar radius: {{u.sonar_radius}}</li>
      % end
      % if u.orbital_radar_radius:
        <li>Orbital radar radius: {{u.orbital_radar_radius}}</li>
      % end
    </ul>
  </li>
