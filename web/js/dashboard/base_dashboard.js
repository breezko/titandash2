/**
 * Helper function available throughout dashboard extensions to retrieve the application data values.
 */
function baseApplicationData() {
    return $(".application-data").data("application");
}

/**
 * base_dashboard.js
 *
 * Base dashboard functionality should handle the pre-populating of our base dashboard data container.
 */
$(document).ready(function() {
    let baseElements = {
        applicationData: $(".application-data"),
        baseLoaderContainer: $(".loader"),
        baseContainer: $("#wrapper"),
        brandTextVersion: $("#brandTextVersion"),
        usernameValue: $("#usernameValue"),
    };

    /**
     * Populate the version number next to the sidebar's title.
     */
    function setupBrandTextVersion() {
        baseElements.brandTextVersion.text(baseApplicationData().app.version);
    }

    /**
     * Populate the username available for the user currently signed in.
     */
    function setupUsername() {
        baseElements.usernameValue.text(baseApplicationData().user.username)
    }

    /**
     * Make an asynchronous request to retrieve all of the base information about the application
     * and user that's currently signed in. Our dashboard is not actually shown until this is
     * all complete and data has been populated where needed.
     */
    async function loadBaseInformation() {
        // Using Eel to grab all the information through js -> python calls.
        let data = await eel.base_information()();

        // Place a small check here to ensure that a person who has not logged in,
        // is sent back to the login screen if they've accessed this page.
        if (data.user === null) {
            window.location = "/templates/login.html"
        }

        // Set the base elements application data within the container for
        // use in other places if needed.
        baseElements.applicationData.data("application", data);

        setupBrandTextVersion();
        setupUsername();

        baseElements.baseLoaderContainer.fadeOut(50, function() {
            baseElements.baseContainer.fadeIn(100);
        });
    }

    // On init or document ready, ensure we run our base information retrieval once.
    // This makes sure our loader is hidden once the data is grabbed and that all data
    // points are populated properly into the template.
    loadBaseInformation();
});