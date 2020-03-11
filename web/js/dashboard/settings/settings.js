/**
 * settings.js
 */
$(document).ready(async function() {
    /**
     * Grab the asynchronous data used by the settings panel.
     */
    async function grabData() {
        // We include the active instance so we can retrieve whether or not
        // the selected instance is active or paused, in which case we should disable options.
        return await eel.dashboard_settings_information(activeInstance())();
    }

    let panel = {
        data: await grabData(),
        elements: {
            instanceTable: $("#dashboardInstancesTable"),
            loader: $("#dashboardSettingsLoader"),
            content: $("#dashboardSettingsContent"),
            configuration: $("#dashboardSettingsSelectConfiguration"),
            window: $("#dashboardSettingsSelectWindow"),
            shortcuts: $("#dashboardSettingsCheckboxShortcuts")
        }
    };

    /**
     * Enable or disable the inputs available on the settings tab.
     */
    function enableOrDisable(active) {
        // Enable or disable the settings options based on the enabled flag.
        // Options should only be enabled when the selected instance isn't currently running.
        panel.elements.configuration.attr("disabled", active);
        panel.elements.window.attr("disabled", active);
        panel.elements.shortcuts.attr("disabled", active);
        // Additionally, if the instance is already active, we can also fade out the entire container
        // so that the content looks more "locked".
        panel.elements.content.css("opacity", active ? "0.65" : "1");
    }

    /**
     * Initial settings panel options setup functionality. Make sure we populate our select options.
     */
    function setupSettingsOptions() {
        // Clear options initially before any appending or
        // settings of settings chosen for instance.
        panel.elements.configuration.empty();
        panel.elements.window.empty();
        panel.elements.shortcuts.prop("checked", false);

        // Begin populating the available options and their
        // associated values for each select option.
        panel.elements.configuration.append($("<option disabled selected>Choose Configuration...</option>"));
        $(panel.data.configurations).each(function(i, v) {
            panel.elements.configuration.append($("<option>", {value: v.pk, html: v.name}))
        });

        panel.elements.window.append($("<option disabled selected>Choose Window...</option>"));
        // Ensuring we include a header for our filtered windows
        // present in the windows select box.
        panel.elements.window.append($("<option disabled>---------------- Filtered Windows ----------------</option>"));
        // Looping through all filtered windows and including each one in the options.
        $(panel.data.windows.filtered).each(function(i, v) {
            panel.elements.window.append($("<option>", {value: v.hwnd, html: v.formatted}));
        });

        // Ensuring we include a header for all windows options.
        panel.elements.window.append($("<option disabled>----------------  All Windows ----------------</option>"));
        // Looping through all available windows and including each one in the options.
        $(panel.data.windows.all).each(function(i, v) {
            panel.elements.window.append($("<option>", {value: v.hwnd, html: v.formatted}));
        });

        // Let's also make sure we check the shortcuts checkbox if an active instance is available
        // and shortcuts are currently enabled.
        if (panel.data.active) {
            panel.elements.configuration.val(panel.data.instance.configuration);
            panel.elements.window.val(panel.data.instance.window);
            panel.elements.shortcuts.prop("checked", panel.data.shortcuts);
        } else {
            panel.elements.configuration[0].selecedIndex = 0;
            panel.elements.window[0].selecedIndex = 0;
            panel.elements.shortcuts.prop("checked", false);
        }

        // Also make sure we disable settings selection and options if the instance
        // that's active is currently running.
        enableOrDisable(panel.data.active);
    }

    /**
     * Call this function to update the settings panel.
     */
    async function updateSettings() {
        // Hide settings panel and begin the process to grab new information.
        // about the selected bot instance and it's settings.
        hidePanel(panel.elements.content, panel.elements.loader, async function() {
            // Update our panel data to reflect the newest instance.
            panel.data = await grabData($(this).closest("tr").data("pk"));
            // Once the panel data is updated, we can re-run our settings
            // setup function and change the proper select options.
            setupSettingsOptions();

            // Display the panel now that new data is setup and available.
            // Settings have now been setup based on instance selected.
            showPanel(panel.elements.content, panel.elements.loader);
        });
    }

    /**
     * Build out listeners and events that deal with the settings panel.
     */
    async function setupSettingsHandlers() {
        // Settings should be modified properly when the active instance
        // is changed to a different instance within the dashboard.
        panel.elements.instanceTable.on("click", ".instance-select", updateSettings);
    }

    function initializeSettingsPanel() {
        // Begin by populating the settings options dynamically
        // once when we initialize.
        setupSettingsOptions();

        // Hide the loader and display the configured
        // settings panel in the proper state.
        panel.elements.loader.fadeOut(50, function() {
            panel.elements.content.fadeIn(100);
        });
    }

    // Begin the actual functionality to call and populate
    // our settings dashboard panel.
    initializeSettingsPanel();
    // Setup any of the listeners of events
    // used bu the settings panel.
    await setupSettingsHandlers();

    // Ensure our settings panel update function is added to globally
    // available update functions.
    updateFunctions["settings"] = updateSettings;
});