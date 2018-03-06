// Global user-specific variables.
var user_id             = undefined;
var user_display_name   = undefined;
var user_profile_image  = undefined;

function initialize_jukebox() {
    setup_interactions();
    update_user_information();
}

function setup_interactions() {
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
    api_post("party/" + name, JSON.stringify(payload), function(data) {
        console.log(data);
    });
}

function revoke_permissions() {
    window.open("https://www.spotify.com/us/account/apps/");
    window.location.replace("/logout");
}