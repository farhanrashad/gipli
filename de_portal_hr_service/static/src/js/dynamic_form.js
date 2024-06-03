function check_list(obj) {
  debugger;
  var changed_field = document.getElementById(obj.id);
  var join_fields = document.getElementById('join_fields');

  let string = changed_field.id;
  let array = string.split('-');
  let service_id = parseInt(array[1]);

  let join_fields_string = join_fields.name;
  let join_fields_array = join_fields_string.split('-');
  let model_field = join_fields_array[0];
  let response_field = join_fields_array[1];
  let field_model = array[2];

  var options = changed_field.options;
  let selected_option = '';
  for (var i = 0; i < options.length; i++) {
    var option = options[i];
    if (option.selected) {
      selected_option = option.value;
      console.log(option.value);
      break;
    }
  }

  var formData = new FormData();
  formData.append('field_name', changed_field.name);
  formData.append('selected_option_id', selected_option);
  formData.append('service_id', service_id);
  formData.append('model_field', model_field);
  formData.append('response_field', response_field);
  formData.append('field_model', field_model);

  $.ajax({
    url: '/get/target/items',
    type: 'POST',
    dataType: 'json',
    data: formData,
    contentType: false,
    processData: false,
    success: function (data) {
      if (data !== undefined && data !== null) {
        let responce_field = document.getElementById(data[0].responce_field);
        try {
          responce_field.innerHTML = '';
        } catch (err) {
          responce_field.className = 'form-control';
        }
        data.forEach(function (option) {
          var optionEl = document.createElement('option');
          optionEl.value = option.value;
          optionEl.text = option.text;
          responce_field.add(optionEl);
        });
      }
    },
    error: function () {
      console.log('Something went wrong!');
    },
  });
}

// onchange function
function filter_changeable_fields(form_id, source_field, target_field) {
  console.log("Function filter_field_vals started");
  console.log("Form ID:", form_id);
  console.log("Form Element:", document.getElementById(form_id));
  console.log("Element Source Name:", source_field);
  console.log("Element Target Name:", target_field);

  var formValues = {};
  var formElements = document.getElementById(form_id);

  // Check if formElements is not null
  if (!formElements) {
    console.error("No form found with the given ID:", form_id);
    return;
  }
  var formData = new FormData();

  $.ajax({
    url: "/get/recompute_values",
    type: "POST",
    dataType: "json",
    data: formData,
    contentType: false,
    processData: false,
    success: function (data) {
      if (data !== undefined && data !== null) {
        console.log(data);
      }
    },
    error: function () {
      console.log("Something went wrong!");
    }
  });

  // Loop through each form element
  for (var i = 0; i < formElements.length; i++) {
    var element = formElements[i];

    // Check if element has a name and avoid non-input elements
    if (element.name) {
      var elementData = {
        id: element.id,
        name: element.name,
        value: element.value
      };
      // Add the element data to formValues with name as key
      formValues[element.name] = elementData;
    }
  }

  // Convert formValues to JSON string (optional)
  var jsonValues = JSON.stringify(formValues);
  console.log("Form Values (JSON):", jsonValues);
}
