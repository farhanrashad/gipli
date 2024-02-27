$(document).ready(function () {
  $(".itemsTable").DataTable({
    dom: 'Bfrtip',
        buttons: [
            'copy',
            'csv',
            'excel',
            'pdf',
            {
                extend: 'print',
                text: 'Print all (not just selected)',
                exportOptions: {
                    modifier: {
                        selected: null
                    }
                }
            }
        ],
        select: true
  });
});

function submit_document() {
  var attachment = document.getElementById("attached_document");
  var import_record = document.getElementById("import_record");
  // var import_type = document.getElementById('import_type');

  var radioGroup = document.getElementsByName("file_format");
  for (var i = 0; i < radioGroup.length; i++) {
    if (radioGroup[i].checked) {
      var import_type = radioGroup[i].value;
      break;
    }
  }

  let array = import_record.name.split("-");
  let service = parseInt(array[0]);
  let model = parseInt(array[1]);
  let record = parseInt(array[2]);

  var file_data = $("#attached_document").prop("files")[0];

  var formData = new FormData();
  formData.append("file", file_data);
  formData.append("import_type", import_type);
  formData.append("service", service);
  formData.append("model", model);
  formData.append("record", record);

  $.ajax({
    url: "/items/document",
    type: "POST",
    enctype: "multipart/formData",
    dataType: "json",
    data: formData,
    contentType: false,
    processData: false,
    success: function (data) {
      debugger;
      if (data.status_is != "Error") {
        console.log("sucessfully imported");
        swal({
          title: "Success",
          text: "Successfully imported",
          buttons: false,
          timer: 1500,
        });
        setTimeout(function () {
          location.reload();
        }, 2000);
      } else {
        swal({
          title: "Error",
          text: data.message,
          buttons: false,
          timer: 2500,
        });
        // showNotify(data.error_message,'danger','top-right');
      }
      setInterval(function () {
        $("#body-overlay-documents").hide();
      }, 100);
    },
    error: function () {
      console.log("Something wrong!");
    },
  });
}

function action(type, service_id, model_id, record_id) {
  var formData = new FormData();
  if (type === "previous") {
    formData.append("btn", 'previous');

  } else if (type === "next") {
    formData.append("btn", 'next');  
  }
  formData.append("service_id", service_id);
  formData.append("model_id", model_id);
  formData.append("record_id", record_id);
  $.ajax({
    url: "/my/model/record/next/prev",
    type: "POST",
    enctype: "multipart/formData",
    dataType: "json",
    data: formData,
    contentType: false,
    processData: false,
    success: function (data) {
      if (data.status_is != "Error") {
        console.log("sucessfully");
        if (data.next_record){
          let currentUrl = window.location.pathname;
          let newUrl = currentUrl.substring(0, currentUrl.lastIndexOf('/')) + '/' +data.next_record.toString();
          console.log(newUrl)
          window.location.pathname = newUrl;
        }
        
      } else {
        console.log('Error')
      }
    },
    error: function () {
      console.log("Something wrong!");
    },
  });
}
