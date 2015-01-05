% import webunits
% import urllib
<br/>
<div class="container">
  <div class="row">
  % for i,(u,db,cat) in enumerate(((u1,db1,cat1), (u2,db2,cat2))):
    <div class="col-sm-6">
      <div class="btn-group">
        <button type="button" class="btn btn-sm btn-info dropdown-toggle" data-toggle="dropdown">
          {{db.unit_groups[cat][0]}} <span class="caret"></span>
        </button>
        <ul class="dropdown-menu" role="info">
          % for group in db.unit_groups:
            % q = dict(request.query)
            % q['cat{}'.format(i+1)] = group
            <li><a href="compare?{{urllib.parse.urlencode(q)}}">
              {{db.unit_groups[group][0]}}
            </a></li>
          % end
        </ul>
      </div>

      <div class="btn-group">
        <button type="button" class="btn btn-sm btn-info dropdown-toggle" data-toggle="dropdown">
          {{u.name}} <span class="caret"></span>
        </button>
        <ul class="dropdown-menu" role="info">
          % for ux in db.get_units(db.unit_groups[cat][3]):
            % q = dict(request.query)
            % q['u{}'.format(i+1)] = ux.safename
            <li><a href="compare?{{urllib.parse.urlencode(q)}}">
              {{ux.name}}
            </a></li>
          % end
        </ul>
      </div>

      <div class="btn-group">
        <button type="button" class="btn btn-sm btn-success dropdown-toggle" data-toggle="dropdown">
          Build: {{db.version}} <span class="caret"></span>
        </button>
        <ul class="dropdown-menu" role="info">
          % for ver in webunits.AVAILABLE_VERSIONS:
            % q = dict(request.query)
            % q['v{}'.format(i+1)] = ver
            <li><a href="compare?{{urllib.parse.urlencode(q)}}">
              Build: {{ver}}
            </a></li>
          % end
        </ul>
      </div>
    </div>
  % end
  </div>
  <div class="row">
    <div class="col-sm-6">
      % include unit_header u=u1, have_icon=have_icon1
      <ul>
        % include unit_stats_basic u=u1
      </ul>
    </div>
    <div class="col-sm-6">
      % include unit_header u=u2, have_icon=have_icon2
      <ul>
        % include unit_stats_basic u=u2
      </ul>
    </div>
  </div>

  <div class="row">
    <div class="col-sm-6">
      <ul>
        % include unit_stats_physics u=u1
      </ul>
    </div>
    <div class="col-sm-6">
      <ul>
        % include unit_stats_physics u=u2
      </ul>
    </div>
  </div>

  <div class="row">
    <div class="col-sm-6">
      <ul>
        % include unit_stats_recon u=u1
      </ul>
    </div>
    <div class="col-sm-6">
      <ul>
        % include unit_stats_recon u=u2
      </ul>
    </div>
  </div>

  % if u1.affects_economy or u2.affects_economy:
    <div class="row">
      <div class="col-sm-6">
        <ul>
          % include unit_stats_economy u=u1
        </ul>
      </div>
      <div class="col-sm-6">
        <ul>
          % include unit_stats_economy u=u2
        </ul>
      </div>
    </div>
  % end

  % if u1.weapons or u2.weapons:
    <div class="row">
      <div class="col-sm-6">
        <ul>
          % include unit_stats_weapons u=u1
        </ul>
      </div>
      <div class="col-sm-6">
        <ul>
          % include unit_stats_weapons u=u2
        </ul>
      </div>
    </div>
  % end

  % if u1.builds or u2.builds:
  <div class="row">
    <div class="col-sm-6">
      <ul>
        % include unit_stats_builds u=u1, db=db1
      </ul>
    </div>
    <div class="col-sm-6">
      <ul>
        % include unit_stats_builds u=u2, db=db2
      </ul>
    </div>
  </div>
  % end

  % if u1.built_by or u2.built_by:
    <div class="row">
      <div class="col-sm-6">
        <ul>
          % include unit_stats_builtby u=u1, db=db1
        </ul>
      </div>
      <div class="col-sm-6">
        <ul>
          % include unit_stats_builtby u=u2, db=db2
        </ul>
      </div>
    </div>
  % end

</div>

% rebase page db=db1
