% suffix = '?version='+db.queryversion if db.queryversion else ''
<h2><a class="hlink" href="{{WEB_BASE}}/table/{{link}}{{suffix}}">{{heading}}</a></h2>
<ul>
% for u in units:
<li>
% include unit_link unit=u, db=db, WEB_BASE=WEB_BASE
</li>
% end
</ul>
