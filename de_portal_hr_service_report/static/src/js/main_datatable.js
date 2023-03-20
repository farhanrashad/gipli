$(document).ready(function () {
  $(".myTable").DataTable({
    pageLength: 50,
    dom: "Bfrtip",
    
    buttons: [
      "copy",
      "csv",
      "excel",
      "pdf",
      {
        
        extend: "print",
        text: "Print all (not just selected)",
        exportOptions: {
          modifier: {
            selected: null,
          },
        },
      },
  
    ],
    select: true,
  });
});



// function submit_input() {
//   debugger;
//   var formData = new FormData();

//   var inputElements = document.getElementsByTagName("input");
//   var selectElements = document.getElementsByTagName("select");
//   for (var i = 0; i < inputElements.length; i++) {
//     if (inputElements[i].type !== "button" && inputElements[i].type !== "submit") {
//       formData.append(inputElements[i].name, inputElements[i].value);
//     }
//   }
//   for (var i = 0; i < selectElements.length; i++) {
//       formData.append(selectElements[i].name, selectElements[i].value);
//   }
  
//   $.ajax({
//     url: "/my/report/model/record/submit/input",
//     type: "POST",
//     dataType: "json",
//     data: formData,
//     contentType: false,
//     processData: false,
//     success: function (data) {
//       debugger;
//       if (data !== undefined && data !== null) {
//         var dataTableDiv = document.querySelector("#data_table_div");

//         dataTableDiv.innerHTML = data[0].template;
//       }
   
//     },
//     error: function () {
//       console.log("Something wrong!");
//     },
//   });
// }
