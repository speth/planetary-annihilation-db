% import webunits
% import urllib
% import units
% suffix = '?version='+db.queryversion if db.queryversion else ''
<div class="navbar navbar-default navbar-fixed-top">
  <div class="container-fluid">
  <div class="navbar-collapse collapse navbar-responsive-collapse">
    <ul class="nav navbar-nav">
      <li><a href="/{{suffix}}">Home</a></li>
      <li class="dropdown">
        <a href="#" class="dropdown-toggle" data-toggle="dropdown">Mobile<b class="caret"></b></a>
        <ul class="dropdown-menu">
          <li><a href="/table/builders{{suffix}}">Builders</a></li>
          <li><a href="/table/vehicles{{suffix}}">Vehicles</a></li>
          <li><a href="/table/bots{{suffix}}">Bots</a></li>
          <li><a href="/table/air{{suffix}}">Air</a></li>
          <li><a href="/table/naval{{suffix}}">Naval</a></li>
          <li><a href="/table/orbital{{suffix}}">Orbital</a></li>
        </ul>
      </li>
      <li class="dropdown">
        <a href="#" class="dropdown-toggle" data-toggle="dropdown">Buildings<b class="caret"></b></a>
        <ul class="dropdown-menu">
          <li><a href="/table/factories{{suffix}}">Factories</a></li>
          <li><a href="/table/economy{{suffix}}">Economy</a></li>
          <li><a href="/table/defense{{suffix}}">Defense</a></li>
          <li><a href="/table/other{{suffix}}">Other</a></li>
        </ul>
      </li>
      % q = {}
      % if unit:
      %   q['u1'] = unit.safename
      %   q['u2'] = unit.safename
      % end
      % if db.queryversion:
      %   q['v1'] = db.queryversion
      %   q['v2'] = db.queryversion
      % end
      <li><a href="/compare?{{urllib.parse.urlencode(q)}}">Compare</a></li>
      <li><a href="/about">About</a></li>

    </ul>
    <ul class="nav navbar-nav navbar-right">
      <li class="dropdown">
        <a href="#" class="dropdown-toggle" data-toggle="dropdown">Options<b class="caret"></b></a>
        <ul class="dropdown-menu">
          <li><a href="javascript:toggle_bool('show_commander_variants')">
            % if webunits.show_variants():
              Hide Commander Variants
            % else:
              Show Commander Variants
            % end
            </a></li>
          <li><a href="javascript:toggle_bool('show_inaccessible_units')">
            % if webunits.show_inaccessible():
              Hide Inaccessible Units
            % else:
              Show Inaccessible Units
            % end
            </a></li>
        </ul>
      </li>
      % if units.AVAILABLE_MODS and not hide_version:
      <li class="dropdown">
        <a href="#" class="dropdown-toggle" data-toggle="dropdown">
          Mods
          % if db.active_mods:
          ({{len(db.active_mods)}} active)
          % end
        <b class="caret"></b></a>
        <ul class="dropdown-menu">
          % for mod in units.AVAILABLE_MODS.values():
            <li>
              % if mod['identifier'] in db.active_mods:
                <a href="{{webunits.update_version(remove_mod=mod['identifier'])}}">
                <b class="glyphicon glyphicon-check"></b>&nbsp;
                {{mod['display_name']}} {{mod['version']}}
                </a>
              % else:
                <a href="{{webunits.update_version(add_mod=mod['identifier'])}}">
                <b class="glyphicon glyphicon-unchecked"></b>&nbsp;
                {{mod['display_name']}} {{mod['version']}}
                </a>
              % end
            </li>
          % end
        </ul>
      </li>
      % end

      % if not hide_version:
      <li class="dropdown">
        <a href="#" class="dropdown-toggle" data-toggle="dropdown">Build: {{db.description}}<b class="caret"></b></a>
        <ul class="dropdown-menu">
          % for v,desc in reversed(list(webunits.AVAILABLE_VERSIONS.items())):
            <li><a href="{{webunits.update_version(version=v)}}">{{desc}}</a></li>
          % end
        </ul>
      </li>
      % end
    </ul>
  </div>
  </div>
</div>
