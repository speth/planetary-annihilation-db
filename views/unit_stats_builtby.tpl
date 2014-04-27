% import webunits
<li>
  <div class='heading'>Built by:</div>
  <ul>
    % for other in u.built_by:
    <li>
      % include unit_link unit=other, version=version
      % if other.build_rate:
        ({{webunits.timestr(u.build_cost / other.build_rate)}})
      % end
    </li>
    % end
  </ul>
</li>
