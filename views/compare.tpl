% import webunits
% import units
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
            <li><a href="{{webunits.update_query('cat{}'.format(i+1), group)}}">
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
            <li><a href="{{webunits.update_query('u{}'.format(i+1), ux.safename)}}">
              {{ux.name}}
            </a></li>
          % end
        </ul>
      </div>

      <div class="btn-group">
        <button type="button" class="btn btn-sm btn-success dropdown-toggle" data-toggle="dropdown">
          Build: {{db.description}} <span class="caret"></span>
        </button>
        % include version_dropdown db=db, field='v{}'.format(i+1)
      </div>

      % if units.AVAILABLE_MODS:
      <div class="btn-group">
        <button type="button" class="btn btn-sm btn-success dropdown-toggle" data-toggle="dropdown">
          Mods ({{len(db.active_mods)}} active)
          <span class="caret"></span>
        </button>
        <ul class="dropdown-menu" role="info">
          % for mod in units.AVAILABLE_MODS.values():
            <li>
              % if mod['identifier'] in db.active_mods:
                <a href="{{webunits.update_version(remove_mod=mod['identifier'], field='v{}'.format(i+1))}}">
                <b class="glyphicon glyphicon-check"></b>&nbsp;
                {{mod['display_name']}} {{mod['version']}}
                </a>
              % else:
                <a href="{{webunits.update_version(add_mod=mod['identifier'], field='v{}'.format(i+1))}}">
                <b class="glyphicon glyphicon-unchecked"></b>&nbsp;
                {{mod['display_name']}} {{mod['version']}}
                </a>
              % end
            </li>
          % end
        </ul>
      </div>
      % end

    </div>
  % end
  </div>
  <div class="row">
    <div class="col-sm-6">
      % include unit_header u=u1, have_icon=have_icon1, db=db1
      <ul>
        % include unit_stats_basic u=u1, db=db1
      </ul>
    </div>
    <div class="col-sm-6">
      % include unit_header u=u2, have_icon=have_icon2, db=db2
      <ul>
        % include unit_stats_basic u=u2, db=db2
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
          % include unit_stats_weapons u=u1, db=db1
        </ul>
      </div>
      <div class="col-sm-6">
        <ul>
          % include unit_stats_weapons u=u2, db=db2
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

% rebase page db=db1, hide_nav_version=True, title='Compare'
