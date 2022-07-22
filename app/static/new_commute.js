

function update_drop_downs(line) {
    // Call the getstations endpoint to get a list of stations based on the supplied line. 
    // This is actually a list of dicts with the form [{"name": "name1", "id", "id1"}}
    // Update the options for origin and destination with said list
    let request_url = 'getstations?line=' + line;
    const options = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    };
    fetch(request_url, options)
        .then(
            function(response) {
                if (response.status !== 200) {
                    console.log('Looks like there was a problem. Status Code: ' +
                    response.status);
                    return;
                }
                response.json().then(function(data) {
                    console.log(data);
                    // The origin and terminations will have to be looped through as well. Hard coding to 1 to get things working
                    let j = 1;
                    for(var i = 0; i < data.length; i++){
                        let origin_element_id = "origin_name" + j.toString();
                        document.getElementById(origin_element_id).options[i] = new Option(data[i].name, data[i].id + "|" + data[i].name);
                        let termination_element_id = "termination_name" + j.toString();
                        document.getElementById(termination_element_id).options[i] = new Option(data[i].name, data[i].id + "|" + data[i].name);
                    };
                });
            }
        )
        .catch(function(err) {
            console.log('Fetch Error :-S', err);
        });
    return true;
}