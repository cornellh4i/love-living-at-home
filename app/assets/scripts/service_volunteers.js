function serviceChoices() {
    let service_category = document.getElementById('service_category').value;
    let service_select = document.getElementById('services');
    const protocol = window.location.protocol;
    const host = window.location.host;
    fetch(`${protocol}//${host}/admin/create-request/${service_category}`, {
    }).then(function (response) {
        response.json().then(function (data) {
            let optionHTML = '';
            for (let service of data.services) {
                optionHTML += '<option value="' + service.id + '">' + service.name + '</option>'
            }
            service_select.innerHTML = optionHTML;
            providerChoices()
        })
    })
}

function providerChoices() {
    let service = document.getElementById('services').value;
    let service_provider_select = document.getElementById('service-provider');
    const protocol = window.location.protocol;
    const host = window.location.host;
    fetch(`${protocol}//${host}/admin/create-request/service/${service}`, {
    }).then(function (response) {
        response.json().then(function (data) {
            let optionHTML = '';
            for (let volunteer of data.service_providers) {
                optionHTML += '<option value="' + volunteer.id + '">' + volunteer.firstName + " " + volunteer.lastName + '</option>'
            }
            service_provider_select.innerHTML = optionHTML;
            if (service_provider_select.innerHTML == '') {
                alert("No service providers for this service");
            }
            var selected_members = [];
            for (var option of document.getElementById('member').options) {
                if (option.selected) {
                    selected_members.push(option.value);
                }
            }
            num_selected_members = selected_members.length;
            var selected_locations = [];
            for (var option of document.getElementById('home_location').options) {
                if (option.selected) {
                    selected_locations.push(option.value);
                }
            }
            num_selected_locations = selected_locations.length;
            let selected_people = document.getElementsByClassName("ui label transition visible");
            for (var i = selected_people.length - 1; i >= num_selected_members + num_selected_locations; i--) {
                selected_people[i].remove();
            }
            let volunteer_table = document.getElementById("volunteerDataTable");
            volunteer_table.remove();
        })
    })
}