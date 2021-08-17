
$(document).ready(function () {
  $('.ui.search.selection.dropdown').dropdown({ fullTextSearch: true });
  $('.ui.checkbox').checkbox();

  $('#select-role').dropdown({
    onChange: function (value, text, $selectedItem) {
      $('#service-provider-menu').find('.item').each(
        function () {
          $this = $(this);
          let role = $this.attr('data-role');
          $this.show();
          if (value && value != role) {
            $this.hide();
          }
        });
    }
  });

  $('.no.label .ui.multiple.selection.dropdown')
    .dropdown({
      useLabels: false
    });

  $('#filter-button').click(function (e) {
    request_type_filter = [];
    service_category_filter = [];
    request_status_filter = [];
    requesting_member_filter = [];
    volunteer_filter = [];
    local_resource_filter = [];
    request_number_filter = null;

    // grab filters from relevant form fields
    $('#request_type .menu .item.active').each(function () {
      selected_value = $(this).attr('data-value');
      request_type_filter.push(selected_value);
    });
    $('#service_category .menu .item.active').each(function () {
      selected_value = $(this).attr('data-value');
      service_category_filter.push(selected_value);
    });
    $('#request_status .menu .item.active').each(function () {
      selected_value = $(this).attr('data-value');
      request_status_filter.push(selected_value);
    });
    $('#requesting_member .menu .item.active').each(function () {
      selected_value = $(this).attr('data-value');
      requesting_member_filter.push(selected_value);
    });
    $('#service-provider-menu .item.active').each(function () {
      volunteer_id = $(this).attr('data-id');
      role = $(this).attr('data-role'); // either "volunteer" or "local-resource"
      id = $(this).attr('data-id');
      if (role == "volunteer") {
        volunteer_id = id;
        volunteer_filter.push(volunteer_id);
      }
      else if (role == "local-resource") {
        local_resource_id = id;
        local_resource_filter.push(local_resource_id);
      }
    });
    request_number_filter = document.getElementById("request_number").value;
    date_type_filter = $("input[name='date_type']:checked").val();
    window.alert(date_type_filter);

    let date_option_filter = $('#date-options').find('[name="date-options"]:checked').val();
    let start_date = $('#startdate').val();
    let end_date = $('#enddate').val()

    // window.alert(Date.parse(start_date));
    // window.alert(Date.parse("2021-06-29"));
    // window.alert(new Date());

    $('.request-card').each(function () {
      $this = $(this);
      $this.show();
      let request_type = $this.find('.request-type-value').html();
      if (request_type_filter.length > 0 && !request_type_filter.includes(request_type)) {
        $this.hide();
      }
      let service_category = $this.find('.service-category-value').html();
      if (service_category_filter.length > 0 && !service_category_filter.includes(service_category)) {
        $this.hide();
      }
      let request_status = $this.find('.request-status-value').find('div').html();
      if (request_status_filter.length > 0 && !request_status_filter.includes(request_status)) {
        $this.hide();
      }
      let requesting_member = $this.find('.requesting-member-value').attr('data-value');
      if (requesting_member_filter.length > 0 && !requesting_member_filter.includes(requesting_member)) {
        $this.hide();
      }

      let volunteer_id = $this.find('.service-provider-value').attr('data-value');
      if (volunteer_filter.length > 0 && !volunteer_filter.includes(volunteer_id)) {
        $this.hide();
      }

      let request_number = $this.find('.request-number-value').html();
      if (request_number_filter && request_number_filter !== request_number) {
        $this.hide();
      }
    });



  });

  // L and R arrows to control date selection
  $("#leftbutton").click(function () {
    var option = document.getElementById("timePeriod").value;
    var start_date = document.getElementById("startdate").value;
    var end_date = document.getElementById("enddate").value;
    var date_values = start_date.split("-");
    var year = parseInt(date_values[0]);
    var month = parseInt(date_values[1]) - 1;
    var date = parseInt(date_values[2]);
    var current = new Date(year, month, date);

    switch (option) {
      case '0':
        var yesterday = new Date(current);
        yesterday.setDate(yesterday.getDate() - 1)
        var new_date = yesterday.getFullYear() + '-' + ("0" + (yesterday.getMonth() + 1)).slice(-2) + '-' + ("0" + yesterday.getDate()).slice(-2);
        var end_date = new_date;
        break;
      case '1':
        var week_ = current.getDate() - 7;
        var last_week = new Date(current.setDate(week_));
        var end_week = new Date(current.setDate(current.getDate() + 7));
        var new_date = last_week.getFullYear() + '-' + ("0" + (last_week.getMonth() + 1)).slice(-2) + '-' + ("0" + last_week.getDate()).slice(-2);
        var end_date = end_week.getFullYear() + '-' + ("0" + (end_week.getMonth() + 1)).slice(-2) + '-' + ("0" + end_week.getDate()).slice(-2);
        break;
      case '2':
        var month_ = current.getMonth() - 1;
        var last_month = new Date(current.setMonth(month_));
        var end_month = new Date(current.setMonth(current.getMonth() + 1));
        var new_date = last_month.getFullYear() + '-' + ("0" + (last_month.getMonth() + 1)).slice(-2) + '-' + ("0" + last_month.getDate()).slice(-2);
        var end_date = end_month.getFullYear() + '-' + ("0" + (end_month.getMonth() + 1)).slice(-2) + '-' + ("0" + end_month.getDate()).slice(-2);
        break;
      default:
        var new_date = start_date;
    }

    var dateControl = document.querySelector('#startdate');
    dateControl.value = new_date;

    var dateControl2 = document.querySelector('#enddate');
    dateControl2.value = end_date;
  });
  $("#rightbutton").click(function () {
    var option = document.getElementById("timePeriod").value;
    var start_date = document.getElementById("startdate").value;
    var end_date = document.getElementById("enddate").value;
    var date_values = start_date.split("-");
    var year = parseInt(date_values[0]);
    var month = parseInt(date_values[1]) - 1;
    var date = parseInt(date_values[2]);
    var current = new Date(year, month, date);

    switch (option) {
      case '0':
        var tomorrow = new Date(current);
        tomorrow.setDate(tomorrow.getDate() + 1)
        var new_date = tomorrow.getFullYear() + '-' + ("0" + (tomorrow.getMonth() + 1)).slice(-2) + '-' + ("0" + tomorrow.getDate()).slice(-2);
        var end_date = new_date;
        break;
      case '1':
        var week_ = current.getDate() + 7;
        var next_week = new Date(current.setDate(week_));
        var end_week = new Date(current.setDate(current.getDate() + 7));
        var new_date = next_week.getFullYear() + '-' + ("0" + (next_week.getMonth() + 1)).slice(-2) + '-' + ("0" + next_week.getDate()).slice(-2);
        var end_date = end_week.getFullYear() + '-' + ("0" + (end_week.getMonth() + 1)).slice(-2) + '-' + ("0" + end_week.getDate()).slice(-2);
        break;
      case '2':
        var month_ = current.getMonth() + 1;
        var next_month = new Date(current.setMonth(month_));
        var end_month = new Date(current.setMonth(current.getMonth() + 1));
        var new_date = next_month.getFullYear() + '-' + ("0" + (next_month.getMonth() + 1)).slice(-2) + '-' + ("0" + next_month.getDate()).slice(-2);
        var end_date = end_month.getFullYear() + '-' + ("0" + (end_month.getMonth() + 1)).slice(-2) + '-' + ("0" + end_month.getDate()).slice(-2);
        break;
      default:
        var new_date = start_date;
    }
    var dateControl = document.querySelector('#startdate');
    dateControl.value = new_date;

    var dateControl2 = document.querySelector('#enddate');
    dateControl2.value = end_date;
  });

  $("select[name = timePeriod]").on("change", function () {
    var date = new Date();
    var start_date;
    var end_date;
    //YYYY-MM-DD                      

    switch ($(this).val()) {
      case '0':
        var start_date = date.getFullYear() + '-' + ("0" + (date.getMonth() + 1)).slice(-2) + '-' + ("0" + date.getDate()).slice(-2);
        var end_date = start_date;
        break;
      case '1':
        var first = date.getDate() - date.getDay() + 1; // First day is the day of the month - the day of the week
        var last = first + 6;
        var firstDay = new Date(date.setDate(first));
        var lastDay = new Date(date.setDate(last));
        var start_date = firstDay.getFullYear() + '-' + ("0" + (firstDay.getMonth() + 1)).slice(-2) + '-' + ("0" + firstDay.getDate()).slice(-2);
        var end_date = lastDay.getFullYear() + '-' + ("0" + (lastDay.getMonth() + 1)).slice(-2) + '-' + ("0" + lastDay.getDate()).slice(-2);
        break;
      case '2':
        var firstDay = new Date(date.getFullYear(), date.getMonth(), 1);
        var lastDay = new Date(date.getFullYear(), date.getMonth() + 1, 0);
        var start_date = firstDay.getFullYear() + '-' + ("0" + (firstDay.getMonth() + 1)).slice(-2) + '-' + ("0" + firstDay.getDate()).slice(-2);
        var end_date = lastDay.getFullYear() + '-' + ("0" + (lastDay.getMonth() + 1)).slice(-2) + '-' + ("0" + lastDay.getDate()).slice(-2);
        break;
      case '3':
        var tomorrow = new Date(date);
        tomorrow.setDate(tomorrow.getDate() + 1);
        var start_date = tomorrow.getFullYear() + '-' + ("0" + (tomorrow.getMonth() + 1)).slice(-2) + '-' + ("0" + tomorrow.getDate()).slice(-2);
        var end_date = start_date;
        break;
      default:
    }

    var dateControl = document.querySelector('#startdate');
    dateControl.value = start_date;
    //window.alert(dateControl.value);
    var dateControl2 = document.querySelector('#enddate');
    dateControl2.value = end_date;
  });


  return false;
})



