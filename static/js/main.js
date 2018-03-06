/*

Jukebox App -- Crowd-source your playlist.


Load required dependencies and start app using RequireJS.

    http://requirejs.org/


6 March 2018, Benjamin Shanahan
*/

require(
[

    // Defined in 'require.setup.js'.
    "jquery",
    "popper",
    "mdb", 

    // App-specific code.
    "lib/jukebox",
    "lib/api"
    
], 
function($) {
    $(function() {

        // This happens on start-up, *after* all dependencies are loaded.
        var current_page = window.location.pathname.split("/").pop();
        if (current_page == "jukebox") {
            initialize_jukebox();
            console.log("Started Jukebox app.");
        }
    });
});