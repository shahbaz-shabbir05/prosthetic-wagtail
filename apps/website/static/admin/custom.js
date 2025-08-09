document.addEventListener('DOMContentLoaded', function () {
  const headerOptionsField = document.querySelector(
    'select[name="header_options"]'
  );
  const headerQuoteField = document.querySelector('input[name="header_quote"]');
  const headerQuoteAttributionField = document.querySelector(
    'input[name="header_quote_attribution"]'
  );

  function toggleQuoteFields() {
    const selectedOption = headerOptionsField.value;
    if (selectedOption == '1') {
      headerQuoteField.removeAttribute('disabled');
      headerQuoteAttributionField.removeAttribute('disabled');
    } else {
      headerQuoteField.setAttribute('disabled', 'true');
      headerQuoteAttributionField.setAttribute('disabled', 'true');
    }
  }

  // Initialize the fields on page load
  toggleQuoteFields();

  // Add event listener to toggle fields on change
  headerOptionsField.addEventListener('change', toggleQuoteFields);
});
