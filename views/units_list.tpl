% suffix = '?version='+version if version != 'current' else ''
<h2><a class="hlink" href="/table/{{link}}{{suffix}}">{{heading}}</a></h2>
<ul>
% for u in units:
<li>
% include unit_link unit=u, version=version
</li>
% end
</ul>
