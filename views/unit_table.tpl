<table>
  % if caption:
  <caption>{{caption}}</caption>
  % end
  <tr>
  % for name in columns:
    <th>{{name}}</th>
  % end
  </tr>
  % for row in data:
  <tr>
    <td>
      % include unit_link unit=row[0]
    </td>

    % for item in row[1:]:
    <td class="num">{{item}}</td>
    % end
  </tr>
  % end
</table>
