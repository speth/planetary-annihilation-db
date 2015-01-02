% import webunits

% include unit_header u=u, have_icon=have_icon
<ul>
  % include unit_stats_basic u=u
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
    % include unit_stats_weapons u=u
  % end
  % if u.builds:
    <br />
    % include unit_stats_builds u=u, version=version
  % end
  % if u.built_by:
    <br />
    % include unit_stats_builtby u=u, version=version
  % end
</ul>
% rebase page version=version, unit=u
