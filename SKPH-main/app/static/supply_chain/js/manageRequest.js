

let formId = 'send-resource';
let resourceForm = document.getElementById(formId);

let checkForm = function () {
    let data = new FormData(resourceForm);
    let donationAmount = data.get('donation_amount');
    let itemAmount = data.get('item_amount');

    if (donationAmount < itemAmount) {
        if (document.getElementById('error-item') != null) {
            return false;
        }
        let element = document.body.appendChild(document.createElement('button'));
        element.id = 'error-item';
        element.classList.add('btn')
        element.classList.add('btn-primary')
        element.classList.add('btn-ln')
        element.style['background-color'] = 'red'

        element.textContent = 'Cannot send items to current request';
        return false;
    }
    return true;
}

let mainForm = document.forms[0];

mainForm.onsubmit = function(event) {
    let donationAmount = parseInt(mainForm.elements['donationAmount'].value);
    let itemStockAmount = parseInt(mainForm.elements['item_amount'].value);
    let amountErrorMessage = document.getElementById['amount-error-div']
    if (donationAmount > itemStockAmount) {
        amountErrorMessage.style['display'] = 'block';
        event.preventDefault();
    } else {
        amountErrorMessage.style['display'] = 'none';
        document.getElementById['submit-button'].disabled = true;
    }
}