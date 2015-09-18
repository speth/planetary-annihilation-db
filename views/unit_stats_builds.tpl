% import webunits

<li>
  <div class='heading'>Builds:</div>
  <ul>
    % for other in sorted(u.builds, key=lambda b: b.name):
    %   if other.variant and not webunits.show_variants():
    %     continue
    %   elif not other.accessible and not webunits.show_inaccessible():
    %     continue
    %   end
      <li>
        % include unit_link unit=other, db=db
        % if u.build_rate and other.build_cost:
          ({{webunits.timestr(other.build_cost / u.build_rate)}})
        % end
      </li>
    % end
  </ul>
</li>
