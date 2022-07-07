

function check_commute(commute_id) {
    let request_body = {"id": commute_id};
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
                    quoteObject = data;
                    document.getElementById(commute_id).innerHTML = data.Summary;
                });
            }
        )
        .catch(function(err) {
            console.log('Fetch Error :-S', err);
        });
}