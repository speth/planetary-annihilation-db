<a href="/unit/{{unit.safename}}">
  % if unit.name == unit.role:
    {{unit.name}}
  % else:
    {{unit.role}}: <em>{{unit.name}}</em>
  % end
</a>
