<h2><a class="hlink" href="/table/{{link}}">{{heading}}</a></h2>
<ul>
% for u in units:
<li>
% include unit_link unit=u
</li>
% end
</ul>
