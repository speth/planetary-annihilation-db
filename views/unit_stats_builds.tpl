% import webunits

<li>
  <div class='heading'>Builds:</div>
  <ul>
    % for other in u.builds:
    %   if other.variant and not webunits.show_variants():
    %     continue
    %   end
      <li>
        % include unit_link unit=other, version=version
        % if u.build_rate and other.build_cost:
          ({{webunits.timestr(other.build_cost / u.build_rate)}})
        % end
      </li>
    % end
  </ul>
</li>
