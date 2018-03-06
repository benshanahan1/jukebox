/* RequireJS Setup */

var require = {
    /*  Shim defines dependencies for a given module. For example, to use 
        Material Design Bootstrap, we need to first load jQuery and Waves,
        so we include those as dependencies in the "mdb" shim entry. */
    shim: {
        "mdb": {
            "deps": ["jquery", "waves"],
            "exports": "MDB"
        }
    },

    /*  Named paths to our dependencies. */
    paths: {
        "popper":       "https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.13.0/umd/popper.min",
        "jquery":       "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min",
        "mdb":          "https://cdnjs.cloudflare.com/ajax/libs/mdbootstrap/4.5.0/js/mdb.min",
        "waves":        "https://cdnjs.cloudflare.com/ajax/libs/node-waves/0.7.6/waves.min"
    }
};