<span class="tier">T{{unit.tier}}</span>
  % if db.version == 'current':
	<a href="/unit/{{unit.safename}}">
  % else:
    <a href="/unit/{{unit.safename}}?version={{db.version}}">
  % end
  % if unit.name == unit.role:
    {{unit.name}}
  % else:
    {{unit.role}}: <em>{{unit.name}}</em>
  % end
</a>
