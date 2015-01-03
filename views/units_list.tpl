% suffix = '?version='+db.version if db.version != 'current' else ''
<h2><a class="hlink" href="/table/{{link}}{{suffix}}">{{heading}}</a></h2>
<ul>
% for u in units:
<li>
% include unit_link unit=u, db=db
</li>
% end
</ul>
