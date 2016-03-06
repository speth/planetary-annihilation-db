% import webunits

% include unit_header u=u, have_icon=have_icon, db=db, WEB_BASE=WEB_BASE
<ul>
  % include unit_stats_basic u=u, db=db, WEB_BASE=WEB_BASE
  % if 'Mobile' in u.unit_types:
    <br />
    %include unit_stats_physics u=u, WEB_BASE=WEB_BASE
  % else:
    %include unit_stats_building u=u, WEB_BASE=WEB_BASE
  % end
  <br />
  % include unit_stats_recon u=u, WEB_BASE=WEB_BASE
  % if u.affects_economy:
    <br />
    % include unit_stats_economy u=u, WEB_BASE=WEB_BASE
  % end
  % if u.weapons:
    <br />
    % include unit_stats_weapons u=u, db=db, WEB_BASE=WEB_BASE
  % end
  % if u.builds:
    <br />
    % include unit_stats_builds u=u, db=db, WEB_BASE=WEB_BASE
  % end
  % if u.built_by:
    <br />
    % include unit_stats_builtby u=u, db=db, WEB_BASE=WEB_BASE
  % end
</ul>
% rebase page db=db, unit=u, title=u.name, WEB_BASE=WEB_BASE
