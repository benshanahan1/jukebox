// Functions to interact with API
var api = "http://127.0.0.1:5000/api/v1/";

// GET request from API. Endpoint specifies the API endpoint for the request. 
// Simple wrapper around jQuery $.get() function.
function api_get(endpoint="", callback=undefined) {
    var full_endpoint = api + endpoint;
    $.get(full_endpoint, function(data) {
        if (callback != undefined) {
            callback(data);
        }
    }).fail(function() {
        console.log("GET request to API failed: " + full_endpoint);
    });
}

// POST request to API. Endpoint specifies the API endpoint for the request.
function api_post(endpoint="", payload=undefined, callback=undefined) {
    var full_endpoint = api + endpoint;
    done_callback = function(data) {
        if (callback != undefined) {
            callback(data);
        }
    };
    fail_callback = function(data) {
        // console.log(data)
        console.log("POST request to API failed: " + full_endpoint);
    };
    if (payload == undefined) {
        $.post(full_endpoint, done_callback).fail(fail_callback);
    } else {
        // console.log(payload)
        // $.post(full_endpoint, payload).done(done_callback).fail(fail_callback);
        $.ajax({ type: 'POST',
                url: full_endpoint,
                data: payload,
                dataType: 'json',
                headers: {
                    'Content-Type' : 'application/json'
                },
                contentType: 'application/json',
                success: done_callback
        });
    }
}

// DELETE request to API
function api_delete(endpoint="", callback=undefined) {
    var full_endpoint = api + endpoint;
    $.ajax({
        url: full_endpoint,
        type: "DELETE",
        success: function(data) {
            if (callback != undefined) {
                callback(data)
            }
        },
        fail: function() {
            console.log("DELETE request to API failed: " + full_endpoint);    
        }
    });
}