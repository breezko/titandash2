/**
 * actions.js
 */
$(document).ready(async function() {
    /**
     * Grab the asynchronous data used by the actions panel.
     */
    async function grabData(selectedInstance) {
        // Including the active instance so we can retrieve the state of the current instance,
        // which will allow us to determine which actions to enable or disable.
        return await eel.dashboard_actions_information(selectedInstance || activeInstance())();
    }

    let panel = {
        data: await grabData(),
        elements: {
            instanceTable: $("#dashboardInstancesTable"),
            loader: $("#dashboardActionsLoader"),
            content: $("#dashboardActionsContent"),
            play: $("#dashboardActionsPlay"),
            pause: $("#dashboardActionsPause"),
            stop: $("#dashboardActionsStop"),
            kill: $("#dashboardActionsKillRunningInstance")
        }
    };

    /**
     * Modify the specified action element (play, pause stop).
     */
    function modifyAction(action, enabled) {
        let elem = null;

        // Switch case through all available actions and set the
        // element that will be modified.
        switch (action) {
            case "play":
                elem = panel.elements.play;
                break;
            case "pause":
                elem = panel.elements.pause;
                break;
            case "stop":
                elem = panel.elements.stop;
                break;
        }

        // Enable or disable the element derived through
        // switch statement above.
        if (enabled) {
            elem.css("cursor", "pointer").removeClass("text-light").hover(function() {
                $(this).css("filter", "brightness(115%)");
            }, function() {
                $(this).css("filter", "brightness(100%)");
            }).off("click").click(function() {
                // When enabled, we need to make sure that we can properly
                // send a signal to the backend for the currently selected
                // instance that's going to be used.
                sendSignal(action);
            });
        }

        // Action should be disabled, We want to remove any of our
        // element events and make sure clicking will not send signals.
        else {
            elem.css({cursor: "unset", filter: "brightness(80%)"}).off("mouseenter").off("mouseleave").off("click").addClass("text-light");
        }
    }

    /**
     * Setup the actions panel options, checking the current panels data to determine which actions to enable or disable.
     */
    function setupActionsOptions() {
        switch (panel.data.state) {
            case "running":
                modifyAction("play", false);
                modifyAction("pause", true);
                modifyAction("stop", true);
                break;
            case "paused":
                modifyAction("play", true);
                modifyAction("pause", false);
                modifyAction("stop", false);
                break;
            case "stopped":
                modifyAction("play", true);
                modifyAction("pause", false);
                modifyAction("stop", false);
                break;
        }
    }

    /**
     * Call this function to update the actions panel.
     */
    async function updateActions() {
        // Let's go ahead and fade out our content and display our loader
        // while the new data is being loaded.
        hidePanel(panel.elements.content, panel.elements.loader, async function() {
            // Update our panel data to reflect the newest instance.
            panel.data = await grabData($(this).closest("tr").data("pk"));
            // Once the panel data is updated, we can re-run our actions
            // setup function to change the enabled/disabled actions.
            setupActionsOptions();

            // Display the panel now that new data is setup and available.
            // Actions have now been setup based on instance selected.
            showPanel(panel.elements.content, panel.elements.loader);
        });
    }

    async function setupActionsHandlers() {
        // The actions should be modified properly when the active instance is changed
        // to a different instance selection.
        panel.elements.instanceTable.on("click", ".instance-select", updateActions);

        // The kill instance option should attempt to send a stop signal
        // to the currently selected bot instance if it's currently running.
        panel.elements.kill.click(async function() {
            // Send a signal to the eel backend to attempt to kill the selected
            // instance, response will depend on if one is running or not.
            let data = await eel.dashboard_actions_kill(activeInstance())();

            if (data.status === "success") {
                generateToast("Kill Instance", `Kill request has been successfully sent to: <em>${activeInstanceName()}</em>.`, data.status);
            } else {
                // Generate a toast message letting the user know that
                // the kill request has been sent for this instance.
                generateToast("Kill Instance", `Kill request could not be sent to: <em>${activeInstanceName()}</em> because the instance is not currently running.`, data.status);
            }
        });
    }

    /**
     * Attempt to send a signal to the backend to play, pause or stop the selected instance.
     */
    async function sendSignal(action) {
        // Generate an alert about the action that's being sent to the backend.
        // Including the name of the selected instance.
        let actionCap = action.charAt(0).toUpperCase() + action.slice(1);
        let message = `Sending <strong>${action}</strong> signal to: <em>${activeInstanceName()}</em>.`;
        let sender = `Send ${actionCap} Signal`;

        // Generate an informational toast that will be displayed with
        // information about the signal that's being sent.
        generateToast(sender, message, "info");

        // Send the signal to the backend, which should start/stop/pause the selected
        // instance if possible.
        eel.dashboard_actions_signal(
            activeInstance(),
            selectedConfiguration(),
            selectedWindow(),
            shortcutsEnabled(),
            action
        );
    }

    /**
     * Initialize the actions panel, making sure we check that the current active instance's state,
     * so we can properly enable or disable certain action buttons.
     */
    function initializeActionsPanel() {
        // Setup the actions options once during initialization.
        // Making sure we setup the options correctly on first load.
        setupActionsOptions();

        // Hide the loader and display the configured actions
        // panel with proper actions setup.
        panel.elements.loader.fadeOut(50, function() {
            panel.elements.content.fadeIn(100);
        });
    }

    // Begin the actual functionality to initialize and setup
    // the actions panel.
    initializeActionsPanel();
    // Setup any of the listeners or events used by the
    // actions panel.
    await setupActionsHandlers();

    // Ensure our actions panel update function is added to globally
    // available update functions.
    updateFunctions["actions"] = updateActions;
});