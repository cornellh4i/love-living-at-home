// Convert a date string with format `yyyy-mm-dd` to a Date object that assumes the local timezone.
function date_object_of_string(date_str) {
  // TODO: need to test timezone (maybe set to ET manually)... what about daylight savings time?
  let date_parts = date_str.split('-');
  let year = date_parts[0];
  let month_zero_indexed = date_parts[1] - 1;
  let day = date_parts[2];
  return new Date(year, month_zero_indexed, day);
}


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

  $('#clear-filter-button').click(function (e) {
    // Instead of resetting all individual form fields, we're reloading the page. 
    location.reload();
  })

  $('#apply-filter-button').click(function (e) {
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

    // Dated or Undated
    let date_status_options = []
    $('input[name="date_status"]:checked').each(function () {
      date_status_options.push($(this).parent().text().trim());
    });

    // Obtain date filters by (1) getting the type of date, and (2) getting the start/end dates
    let date_type_options = [];
    let date_type_filter_text;
    $(':radio').each(function () {
      date_type_options.push($(this).parent().text().trim());
    });
    date_type_filter_id = $("input[name='date_type']:checked").val();
    if (date_type_filter_id) {
      date_type_filter_text = date_type_options[date_type_filter_id];
    }

    let start_date_str = $('#start-date').val();
    let end_date_str = $('#end-date').val();
    let start_date = date_object_of_string(start_date_str);
    let end_date = date_object_of_string(end_date_str);

    request_number_filter = document.getElementById("request_number").value;

    // Filter through request cards 
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

      // TODO: Date status filter ("Dated" vs "Undated")

      // Apply filter for Date Type and Range
      let date_str;
      if (date_type_filter_text == "Service Date") {
        date_str = $this.find('.requested-date-value').attr('data-value');
      }
      else if (date_type_filter_text == "Created Date") {
        date_str = $this.find('.created-date-value').html().trim();
      }
      // Assuming format 'mm/dd/yyyy'
      let date_str_tokens = date_str.split('/');
      let date_month = date_str_tokens[0];
      let date_day = date_str_tokens[1];
      let date_year = date_str_tokens[2];
      let date_obj = new Date(date_year, date_month - 1, date_day);

      // Filter by start date.
      if (start_date && date_obj < start_date) {
        $this.hide();
      }
      // Filter by end date.
      if (end_date && date_obj > end_date) {
        $this.hide();
      }

      let request_number = $this.find('.request-number-value').html();
      if (request_number_filter && request_number_filter !== request_number) {
        $this.hide();
      }

      // TODO: Update the display for the number of search results returned. 

    });
  });

  // L and R arrows to control date selection
  $("#leftbutton").click(function () {
    var option = document.getElementById("time-period").value;
    var start_date = document.getElementById("start-date").value;
    var end_date = document.getElementById("end-date").value;
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

    var dateControl = document.querySelector('#start-date');
    dateControl.value = new_date;

    var dateControl2 = document.querySelector('#end-date');
    dateControl2.value = end_date;
  });
  $("#rightbutton").click(function () {
    var option = document.getElementById("time-period").value;
    var start_date = document.getElementById("start-date").value;
    var end_date = document.getElementById("end-date").value;
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
    var dateControl = document.querySelector('#start-date');
    dateControl.value = new_date;

    var dateControl2 = document.querySelector('#end-date');
    dateControl2.value = end_date;
  });

  $("select[name = time-period]").on("change", function () {
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
        break;
      default:
    }

    var dateControl = document.querySelector('#start-date');
    dateControl.value = start_date;

    var dateControl2 = document.querySelector('#end-date');
    dateControl2.value = end_date;
  });


  return false;
})



