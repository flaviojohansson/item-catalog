// GOOGLE SIGN IN

var googleUser = {};

$(function() {
    startApp();
    $("#googleSigninButton").click(function() {
        auth2.grantOfflineAccess(
            {"redirect_uri": "postmessage", scope: "openid email", prompt: "consent"}
        ).then(signInCallback);
    });

    $("#facebookSigninButton").click(function() {
        fb_login();
    });
});

var startApp = function() {
    gapi.load("auth2", function(){
        // Retrieve the singleton for the GoogleAuth library and set up the client.
        auth2 = gapi.auth2.init({
            client_id:google_client_id,
            //redirecturi:"postmessage",
            //accesstype:"offline",
            cookie_policy:"single_host_origin",
            // Request scopes in addition to 'profile' and 'email'
            // scope: 'openid email'
        });
    });
};

function signInCallback(authResult) {
    if (authResult["code"]) {

        console.log("Welcome!  Fetching your information.... ");

        // Hide the sign-in button now that the user is authorized
        // $("#googleSigninButton").attr("style", "display: none");

        // Send the one-time-use code to the server, if the server responds, write a 'login successful' message to the web page and then redirect back to the main page
        $.ajax({
            type: "POST",
            url: "/auth/gconnect?state=" + state + "&_csrf_token=" + csrf_token,
            processData: false,
            data: authResult["code"],
            contentType: "application/octet-stream; charset=utf-8",
            success: function(result) {
                // Handle or verify the server response if necessary.
                if (result) {
                    console.log("Successful login for: " + result);
                    $("#result").html("Login Successful, " + result + ". Redirecting...");
                    setTimeout(function() {
                        window.location.href = "/signedin";
                    }, 100);
                } else {
                    if (authResult["error"])
                        console.log("There was an error: " + authResult["error"]);

                    $("#result").html("Failed to make a server-side call. Check your configuration and console.");
                }
            }
        });
    }
}

// END GOOGLE SIGN IN


// FACEBOOK SIGN IN

window.fbAsyncInit = function() {
    FB.init({
        appId : facebook_client_id,
        cookie : true,  // enable cookies to allow the server to access 
        // the session
        xfbml : true,  // parse social plugins on this page
        version : "v2.8" // use version 2.8
    });
};

// Load the SDK asynchronously
(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, "script", "facebook-jssdk"));

// Here we run a very simple test of the Graph API after login is
// successful.  See statusChangeCallback() for when this call is made.
function fb_login(){
    FB.login(function(response) {
        if (response.authResponse) {
            var access_token = response.authResponse.accessToken;
            console.log("Welcome!  Fetching your information.... ");

            // Hide the sign-in button now that the user is authorized
            // $("#facebookSigninButton").attr("style", "display: none");
            FB.api("/me", function(response) {
                console.log("Successful login for: " + response.name);
                $.ajax({
                    type: "POST",
                    url: "/auth/fbconnect?state=" + state + "&_csrf_token=" + csrf_token,
                    processData: false,
                    data: access_token,
                    contentType: "application/octet-stream; charset=utf-8",
                    success: function(result) {
                        // Handle or verify the server response if necessary.
                        if (result) {
                            $("#result").html("Login Successful, " + result + ". Redirecting...")
                            setTimeout(function() {
                                window.location.href = "/signedin";
                            }, 100);
                        } else {
                            $("#result").html("Failed to make a server-side call. Check your configuration and console.");
                        }
                    }
                });
            });
        } else {
            $("#result").html("Not athorized.");
        }
    }, {
        scope: "public_profile,email"
    });
}

// END FACEBOOK SIGN IN
