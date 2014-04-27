<div style="width: 100%; overflow: hidden;">
  % if have_icon:
    <div style="width: 60px; float: left; margin-top:14px">
      <img src=/build_icons/{{u.safename}} />
    </div>
    <div style="margin-left: 72px;">
  % else:
    <div>
  % end
      <h1>
        % if u.name == u.role:
          {{u.name}}
        % else:
          {{u.role}}: <em>{{u.name}}</em>
        % end
      </h1>
      <em>{{u.description}}</em>
    </div>
</div>
