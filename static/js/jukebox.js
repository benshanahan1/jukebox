// Global user-specific variables.
var user_id             = undefined;
var user_display_name   = undefined;
var user_profile_image  = undefined;

function initialize_create_party_page() {
    $("#new-party-btn").click(function() {
        // Get user inputs.
        var new_party_name          = $("#new-party-name").val();
        var new_party_description   = $("#new-party-description").val();
        var new_party_playlist      = $("#new-party-playlist").val();

        // Error check user inputs.
        var name_ok     = (new_party_name != undefined && new_party_name.length >= 1);
        var playlist_ok = true;
        // var playlist_ok = (new_party_playlist != undefined && new_party_playlist.substring(0,13) == "spotify:user:");
        if (new_party_description == undefined)
            new_party_description = "Jukebox playlist.";

        if (name_ok && playlist_ok) {
            create_party(new_party_name, new_party_description, new_party_playlist);
        }
    });
    update_user_information();
}

function initialize_view_party_page(party_id, is_party_host) {
    $("#add-song-btn").click(function() {
        // Get user input.
        var new_song_uri = $("#add-song-uri-input").val();
        if (new_song_uri == undefined) {
            console.log("An error occurred.");
            return false;
        }

        // Error check user input.
        if (new_song_uri.length <= 0) {
            $("#add-song-error-text").text("Please enter a Spotify URI.");
            return false;
        }
        if (new_song_uri.indexOf("spotify:track:") === -1) {
            $("#add-song-error-text").text("Please enter a valid Spotify URI.");
            return false;
        }
        // Made it through all error conditions. Proceed.
        add_song(party_id, new_song_uri, function() {
            // Song was added successfully. Refresh page and highlight added entry.
            location.replace(location.origin + location.pathname + "?highlight=" + new_song_uri);
        }, function() {
            // Invalid spotify URI.
            $("#add-song-error-text").text("Please enter a valid Spotify URI.");
            return false;
        });
    });
    if (is_party_host) {
        $("#spotify-export-btn").click(function() {
            export_party(party_id, function() {
                // TODO: alert user in GUI
                $("#spotify-export-modal").modal("toggle");
            });
        });
        $("#delete-party-btn").click(function() {
            delete_party(party_id, function() {
                $("#delete-party-modal").modal("toggle");
                location.replace(location.origin);  // redirect user to homepage
            });
        });
        $("#header-party-name").blur(function() {
            var new_name = $("#header-party-name").text();
            var payload = {
                "party_id":     party_id,
                "name":         new_name
            };
            api_post("party/update", JSON.stringify(payload), function(data) {
                console.log(data.message);
            });
        });
        $("#header-party-description").blur(function() {
            var new_description = $("#header-party-description").text();
            var payload = {
                "party_id":     party_id,
                "description":  new_description
            };
            api_post("party/update", JSON.stringify(payload), function(data) {
                console.log(data.message);
            });
        });
    }
}

function initialize_user_account_page() {
    $("#account-create-party-btn").click(function() {
        // Redirect to party create page.
        location.replace(location.origin + "/create");
    });
    $("#account-revoke-spotify-permissions").click(function() {
        // Direct user to page to revoke Jukebox app permissions.
        revoke_permissions();
    });
    update_user_information();
}

function update_user_information() {
    api_get("me", function(data) {
        user_id             = data.id;
        user_display_name   = data.display_name;
        user_profile_image  = data.images[0].url;
        $("#user-profile-image").attr("src", user_profile_image);
        $("#user-display-name").text(user_display_name);
    });
}

function create_party(name, description, playlist) {
    // name = name.replace(/\s/g, "");  // TODO make this text also become titled
    var payload = {
        "name":         name,
        "description":  description,
        "playlist":     playlist
    };
    api_post("party", JSON.stringify(payload), function(data) {
        console.log(data.message);
        window.location.replace("/" + data.party_id)
    });
}

function export_party(party_id, callback) {
    api_post("party/" + party_id, undefined, function() {
        console.log("Exported party: " + party_id);
        if (callback != undefined) {
            callback();
        }
    })
}

function delete_party(party_id, callback) {
    api_delete("party/" + party_id, function() {
        console.log("Deleted party: " + party_id);
        if (callback != undefined) {
            callback();
        }
    });
}

function add_song(party_id, new_song_id, success_callback, error_callback) {
    console.log("Party: " + party_id + ", Song: " + new_song_id + ". Not implemented.");
    if (success_callback != undefined) {
        success_callback();
    }
    // if (error_callback != undefined) {
    //     error_callback();
    // }
}

function vote_on_song(vote_display_id, party_id, song_id, vote_type) {
    switch (vote_type.toLowerCase()) {
        case "up":
            api_post("party/" + party_id + "/song/" + song_id + "/votes", undefined, function(data) {
                console.log(data.message);
                $("#" + vote_display_id).text(data.vote_count);
            });
            break;
        case "down":
            api_delete("party/" + party_id + "/song/" + song_id + "/votes", function(data) {
                console.log(data.message);
                $("#" + vote_display_id).text(data.vote_count);
            });
            break;
        default:
            return undefined;
    }
}

function revoke_permissions() {
    // Redirect page to /logout endpoint and open a new tab with Spotify 
    // connected apps page. The new tab (Spotify account page) will take
    // the browser's focus.
    location.replace(location.origin + "/logout");
    window.open("https://www.spotify.com/us/account/apps/");
}