$(document).ready(function () {
  if (document.getElementById("status").value == "3") {
    $("#cancellation").show();
  } else {
    $("#cancellation").hide();
  }
  let status = $("#status");
  status.change(() => {
    let cancellation_reason_field = $("#cancellation-reason");
    if (document.getElementById("status").value == "3") {
      $("#cancellation").show();
    } else {
      $("#cancellation").hide();
    }
  });
});
