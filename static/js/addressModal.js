$('#addressModal').on('submit', '#addressForm', function(e) {
    e.preventDefault();
    var $form = $(this);
    var formData = $form.serialize();
    $.ajax({
        url: "{% url 'address_add_ajax' %}",
        method: "POST",
        data: formData,
        success: function(data) {
            $('#address-list-section').html(data.address_list_html);
            $('#address-form-section').hide();
            $form[0].reset();
            $('#address-form-errors').html('');
            $('#address-list-section').show();
        },
        error: function(xhr) {
            if (xhr.responseJSON && xhr.responseJSON.errors) {
                $('#address-form-errors').html(xhr.responseJSON.errors);
            } else {
                $('#address-form-errors').html('An error occurred.');
            }
        }
    });
});
$('#addressModal').on('click', '#show-address-form', function() {
    $('#address-list-section').hide();
    $('#address-form-section').show();
});
$('#addressModal').on('click', '#cancel-add-address', function() {
    $('#address-form-section').hide();
    $('#address-list-section').show();
});