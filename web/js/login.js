/**
 * login.js
 *
 * We must ensure that any remembered values are populated on the login form if they are available.
 * We also hide to login form until that information is retrieved. Then populating the information and hiding our loader.
 */
$(document).ready(function() {
    // Create a dictionary of all available elements present on the login page.
    let elements = {
        errorsContainer: $(".errors-container"),
        errors: $(".errors"),
        // Loader (Spinner).
        loaderContainer: $(".loader"),
        // Form Container.
        formContainer: $(".container"),
        // Form Elements.
        formLoader: $(".form-loader"),
        formUsername: $("#inputUsername"),
        formToken: $("#inputToken"),
        formSubmit: $("#submitLogin"),
        // Card Elements.
        cardBody: $("#loginCardBody")
    };

    /**
     * Create an alert of the specified ``type`` with the provided ``message``.
     */
    function createErrors(errors) {
        // Ensure we fade out and clear the current errors container
        // in case messages are already present.
        elements.errorsContainer.fadeOut(50, function() {
            elements.errors.empty();

            // Loop through each available error that is available, and ensure
            // an alert is created for each one.
            for (let error of errors) {
                elements.errors.append(`
                    <div class="alert alert-${error["type"]} alert-dismissible">
                        <button type="button" class="close" data-dismiss="alert">&times;</button>
                        ${error["message"]}
                    </div>
                `);
            }
            // Fade the error container in once we've added all our present errors
            // to the element.
            elements.errorsContainer.fadeIn(50, function() {
                enableForm();
            });
        });
    }

    /**
     * Disable the login form, fading out all content and making it disabled, and also displaying the form loader.
     */
    function disableForm() {
        elements.cardBody.css("pointer-events", "none").fadeTo("fast", 0.15, function() {
            elements.formLoader.fadeIn(50);
        });
    }

    /**
     * Enable the login form, fading in all content and making them enabled, and also hiding the form loader.
     */
    function enableForm() {
        elements.formLoader.fadeOut(50, function() {
            elements.cardBody.css("pointer-events", "all").fadeTo("fast", 1);
        });
    }

    /**
     * Remove and fade out the errors present on the form (if there are any).
     */
    function fadeOutErrors() {
        elements.errorsContainer.fadeOut(50, function() {
            elements.errors.empty();
        });
    }

    /**
     * Attempt to retrieve the remembered information from the database.
     *
     * If the information is found, we can populate the proper form fields, and hide our loader
     * and show the form before submitting the information.
     */
    async function loadRememberedInformation() {
        let information = await eel.load_remembered_information()();
        debugger;

        // Information is available, populate the values before showing the form.
        // Anything other than "null" means we have some information available.
        if (information !== null) {
            elements.formUsername.val(information.__data__.username);
            elements.formToken.val(information.__data__.token);
        }

        // Fade out our loader and begin fading in the form itself.
        // Happens once per application start (if no user is already valid).
        elements.loaderContainer.fadeOut(50, function() {
            elements.formContainer.fadeIn(50);
        });
    }

    /**
     * Attempting to log a user in asynchronously. When a user hits submit, we follow a flow of actions to determine
     * whether or not the information they have entered is at all valid.
     */
    async function login() {
        let errors = [];

        // Make sure the entire form is disabled and faded out slightly
        // while we go ahead and perform our login validation.
        fadeOutErrors();
        disableForm();

        setTimeout(async function() {
            // Begin by ensuring that the values entered for the username and token are
            // at least truthy (they are entered with some sort of data).
            let username = elements.formUsername.val();
            let token = elements.formToken.val();

            if (!username) {
                errors.push({
                    type: "danger",
                    message: "Ensure the username field is filled out appropriately."
                });
            }
            if (!token) {
                errors.push({
                    type: "danger",
                    message: "Ensure the token field is filled out appropriately."
                });
            }

            // Any errors yet? Let's return early if so and create some error messages.
            if (errors.length > 0) {
                return createErrors(errors)
            }

            // Information is present, let's attempt to validate the information entered
            // by the user, our eel library can handle this with a function.
            let information = await eel.login(username, token)();

        }, 200);
    }

    // Whenever the submit button is pressed, attempting to login to the system
    // through an asynchronous call to the internal web server.
    elements.formSubmit.on("click", function() {
        login();
    });

    // Loading remembered information (if available).
    // This kick-starts the login flow if a user is sent here.
    loadRememberedInformation();
});
