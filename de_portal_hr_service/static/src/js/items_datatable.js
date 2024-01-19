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
  var record_line_ids = document.getElementsByName("record_line_id");
  // Loop over the record_line_ids
  var record_line_selected_id = ''
  for (var i = 0; i < record_line_ids.length; i++) {
    var record_line_id = record_line_ids[i].id;
    
    var attached_document_obj = document.getElementById("attached_document_" + record_line_id);
    if (attached_document_obj.value !== null &&  attached_document_obj.value !== '') {
      let text1 = "#";
      let attached_document_id = text1.concat("", attached_document_obj.id);
      var file_data = $(attached_document_id).prop("files")[0];

      // for import record input field
      const str = attached_document_obj.id; // replace with your input string
      const parts = str.split('_'); // split the string into an array using "_" as the delimiter
      record_line_selected_id = parts[2];  

    }
  }
  // var attachment = document.getElementById("attached_document");
  // let import_record_id_first_part = "import_record_";
  // let import_record_id = text1.concat("", attached_document_obj.id); 
  var service = ''
  var model = ''
  var record = ''
  var service_item_record_line_id = ''

  var import_record_inputs = document.getElementsByName("import_record");
  for (var i = 0; i < import_record_inputs.length; i++) {
    let import_record_array = import_record_inputs[i].id.split("-");
    // let service = parseInt(array[0]);
    // let model = parseInt(array[1]);
    // let record = parseInt(array[2]);
    let rec_line = parseInt(import_record_array[3]);
    rec_line_id = rec_line.toString()
    
    // Check if the attached_document_1 has a non-null value
    if (record_line_selected_id == rec_line_id) {
       service = parseInt(import_record_array[0]);
       model = parseInt(import_record_array[1]);
       record = parseInt(import_record_array[2]);
       service_item_record_line_id = rec_line_id

    }}
  // var import_type = document.getElementById('import_type');

  var radioGroup = document.getElementsByName("file_format");
  for (var i = 0; i < radioGroup.length; i++) {
    if (radioGroup[i].checked) {
      var import_type = radioGroup[i].value;
      break;
    }
  }



  // var file_data = $("#attached_document").prop("files")[0];

  var formData = new FormData();
  formData.append("file", file_data);
  formData.append("import_type", import_type);
  formData.append("service", service);
  formData.append("model", model);
  formData.append("record", record);
  formData.append("service_item_record_line_id", service_item_record_line_id);

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
