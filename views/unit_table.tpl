% if caption:
<h1>{{caption}}</h1>
% end
<table class="table table-striped table-nonfluid vert-center">
  <thead>
    <tr>
    <th></th>
    % for name in columns:
      <th>{{name}}</th>
    % end
    </tr>
  </thead>
  <tbody>
    % for row in data:
    <tr>
      <td>
        <img class="unit-icon" src="/build_icons/{{row[0].safename}}" />
      </td>
      <td>
        % include unit_link unit=row[0], version=version
      </td>

      % for item in row[1:]:
      <td class="num">{{item}}</td>
      % end
    </tr>
    % end
  </tbody>
</table>
