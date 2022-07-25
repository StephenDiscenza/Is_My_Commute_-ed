let leg_index = 1;

function update_drop_downs(line, leg_num) {
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
                    for(var i = 0; i < data.length; i++){
                        let origin_element_id = "origin_name" + leg_index.toString();
                        document.getElementById(origin_element_id).options[i] = new Option(data[i].name, data[i].id + "|" + data[i].name);
                        let termination_element_id = "termination_name" + leg_index.toString();
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


function add_commute_leg() {
    leg_index += 1;
    var commute_form = document.getElementById('leg_data');
    
    // Create the line selection
    var line = document.createElement("select");
    line.setAttribute("name", "line" + leg_index.toString());
    line.setAttribute("id", "line" + leg_index.toString());
    line.setAttribute("onChange", "update_drop_downs(this.options[this.selectedIndex].value, " + leg_index.toString() + ")");
    // Copy all the subway lines from the original commute leg to this new one
    var orig_line = document.getElementById('line1');
    line.innerHTML = line.innerHTML + orig_line.innerHTML;

    // Create the origin and destination selects
    var origin = document.createElement("select");
    origin.setAttribute("name", "origin_name" + leg_index.toString());
    origin.setAttribute("id", "origin_name" + leg_index.toString());
    var termination = document.createElement("select");
    termination.setAttribute("name", "termination_name" + leg_index.toString());
    termination.setAttribute("id", "termination_name" + leg_index.toString());

    commute_form.append(line);
    commute_form.append(origin);
    commute_form.append(termination);
    return true;

}