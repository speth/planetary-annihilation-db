% import webunits
<li>
  <div class='heading'>Built by:</div>
  <ul>
    % for other in sorted(u.built_by, key=lambda b: b.name):
    %   if other.variant and not webunits.show_variants():
    %     continue
    %   elif not other.accessible and not webunits.show_inaccessible():
    %     continue
    %   end
    <li>
      % include unit_link unit=other, db=db
      % if other.build_rate:
        ({{webunits.timestr(u.build_cost / other.build_rate)}})
      % end
    </li>
    % end
  </ul>
</li>
