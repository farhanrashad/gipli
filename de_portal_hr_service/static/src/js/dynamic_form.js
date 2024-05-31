function check_list(obj) {
    debugger;
    var changed_field = document.getElementById(obj.id);
    var join_fields = document.getElementById('join_fields');

    let string = changed_field.id;
    let array = string.split("-");
    let service_id = parseInt(array[1]);

    let join_fields_string = join_fields.name;
    let join_fields_array = join_fields_string.split("-");
    let model_field = join_fields_array[0];
    let response_field = join_fields_array[1];
    let field_model = array[2];

    var options = changed_field.options;
    let selected_option = "";
    for (var i = 0; i < options.length; i++) {
        var option = options[i];
        if (option.selected) {
            selected_option = option.value;
            console.log(option.value);
        break;
        }
    }

    var formData = new FormData();
    formData.append("field_name", changed_field.name);
    formData.append("selected_option_id", selected_option);
    formData.append("service_id", service_id);
    formData.append("model_field", model_field);
    formData.append("response_field", response_field);
    formData.append("field_model", field_model);

    $.ajax({
        url: "/get/target/items",
        type: "POST",
        dataType: "json",
        data: formData,
        contentType: false,
        processData: false,
        success: function (data) {
            if (data !== undefined && data !== null) {
            let responce_field = document.getElementById(data[0].responce_field);
            try {
                responce_field.innerHTML = "";
            } 
            catch(err) {
                responce_field.className = "form-control";
            }
            data.forEach(function (option) {
                var optionEl = document.createElement("option");
                optionEl.value = option.value;
                optionEl.text = option.text;
                responce_field.add(optionEl);
            });
        }
    }
    error: function () {
      console.log("Something went wrong!");
    }
  });
}
