

function check_commute(commute_id) {
    let request_body = {"commute_id": commute_id};
    let request_url = 'checkcommute';
    const options = {
        method: 'POST',
        body: JSON.stringify(request_body),
        headers: {
            'Content-Type': 'application/json'
        }
    }
    fetch(request_url, options)
        .then(
            function(response) {
                if (response.status !== 200) {
                    console.log('Looks like there was a problem. Status Code: ' +
                    response.status);
                    return;
                }
                // Dynamically generate element ids in the html for each commute so we can use them here
                response.json().then(function(data) {
                    console.log(data);
                    if (data.result === true) {
                        result_text = "Yep"
                    }
                    else {
                        result_text = "Nope"
                    }
                    result_html = "<strong>" + result_text + "</strong>"
                    for (var i = 0; i < data.alerts.length; i++) {
                        result_html += "<p>" + data.alerts[i] + "</p>"
                    }
                    document.getElementById(commute_id).innerHTML = result_html;
                });
            }
        )
        .catch(function(err) {
            console.log('Fetch Error :-S', err);
        });
}