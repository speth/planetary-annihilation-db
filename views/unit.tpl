% import webunits

% include unit_header u=u, have_icon=have_icon, db=db
<ul>
  % include unit_stats_basic u=u, db=db
  % if 'Mobile' in u.unit_types:
    <br />
    %include unit_stats_physics u=u
  % else:
    %include unit_stats_building u=u
  % end
  <br />
  % include unit_stats_recon u=u
  % if u.affects_economy:
    <br />
    % include unit_stats_economy u=u
  % end
  % if u.weapons:
    <br />
    % include unit_stats_weapons u=u, db=db
  % end
  % if u.builds:
    <br />
    % include unit_stats_builds u=u, db=db
  % end
  % if u.built_by:
    <br />
    % include unit_stats_builtby u=u, db=db
  % end
</ul>
% rebase page db=db, unit=u, title=u.name
