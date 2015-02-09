% import webunits

<ul class="dropdown-menu hide-excess show-before show-after">
  % versions = list(webunits.AVAILABLE_VERSIONS.items())
  % versions.reverse()
  % for i,(v,desc) in enumerate(versions):
  %   if v == db.version:
  %     iActive = i
  %     break
  %   end
  % end
  % iStart = max(0, min(iActive-5, len(versions)-10))
  % iStop = min(max(iActive+5, 10), len(versions))
  % for i,(v,desc) in enumerate(versions):
    % if i and i < iStart:
    %   itemClass = 'hide-before'
    % elif i > iStop and i != len(versions)-1:
    %   itemClass = 'hide-after'
    % else:
    %   itemClass = 'show-item'
    % end
    % if i == iActive:
    %   itemClass += ' current-version'
    % end
    % if (i == iStart and iStart != 0):
      <li class="ldots-before"><a>...</a></li>
    % end
    <li class="{{itemClass}}">
      <a href="{{webunits.update_version(field=field, version=v)}}">{{desc}}</a>
    </li>
    % if (i == iStop and iStop != len(versions)):
      <li class="ldots-after"><a>...</a></li>
    % end
  % end
</ul>
