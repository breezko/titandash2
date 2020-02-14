/**
 * index.js
 *
 * We must ensure that we are grabbing valid information for the user as their homepage is loaded.
 */
$(document).ready(function() {
    let elements = {
        // Loader (Spinner).
        loaderContainer: $(".loader"),
        // Base Container.
        container: $("#wrapper")
    };

    /**
     * Make a asynchronous request to the authentication backend to receive information about
     * the users account.
     */
    async function loadUserInformation() {
        let information = await eel.load_user_information()();

        elements.loaderContainer.fadeOut(50, function() {
            elements.container.fadeIn(200);
        });
    }

    // Loading user data before anything is shown on the index page.
    // Following same "flow" as logging in, so proper loaders are shown and hidden.
    loadUserInformation();
});