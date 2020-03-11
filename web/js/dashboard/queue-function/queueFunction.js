/**
 * queueFunction.js
 */
$(document).ready(async function() {
    /**
     * Grab the asynchronous data used by the queue function panel.
     */
    async function grabData() {
        // Including selected instance to ensure we can grab
        // current queueables on load.
        return await eel.dashboard_queue_function_information(activeInstance())();
    }

    let panel = {
        data: await grabData(),
        elements: {
            instanceTable: $("#dashboardInstancesTable"),
            loader: $("#dashboardQueueFunctionLoader"),
            content: $("#dashboardQueueFunctionContent"),
            queueablesContent: $("#dashboardQueueFunctionQueueablesContent"),
            queuedTableBody: $("#dashboardQueueFunctionQueuedTableBody"),
            customSearch: $("#dashboardQueueFunctionSearch"),
            customOptions: $("#dashboardQueueFunctionCustomOptions"),
            customNow: $("#dashboardQueueFunctionNow"),
            customCustom: $("#dashboardQueueFunctionCustom"),
            customDurationType: $("#dashboardQueueFunctionCustomDurationType"),
            customDuration: $("#dashboardQueueFunctionCustomDuration"),
            customDurationSeconds: $("#dashboardQueueFunctionCustomDurationSeconds"),
            customDurationMinutes: $("#dashboardQueueFunctionCustomDurationMinutes"),
            customDurationHours: $("#dashboardQueueFunctionCustomDurationHours"),
            flushQueue: $("#dashboardQueueFunctionFlush")
        }
    };

    /**
     * Call this function to update the queue functions panel.
     */
    async function updateQueueFunctions() {
        // Go ahead and fade out our content and display our loader
        // while new data is being loaded.
        hidePanel(panel.elements.content, panel.elements.loader, async function() {
            // Update panel data to reflect up-to date set of
            // queueable functions available.
            panel.data = await grabData();
            // Once our data is upto date, run our setup function to populate
            // the queued functions available on the dashboard.
            setupQueueFunctionOptions();

            // We also need to make sure we populate the current available
            // set of queued functions for the selected instance.
            setupQueueFunctionQueued();

            // Display the panel now that new data is setup and available.
            showPanel(panel.elements.content, panel.elements.loader);
        });
    }

    /**
     * Clear an regenerate the available queueables within the container for them.
     */
    function generateAvailableQueueables(term) {
        panel.elements.queueablesContent.empty();

        // Create a copy of all queueables.
        let queueables = panel.data.queueables;

        // If a term has been included, try and filter the list
        // down to only contain names that match.
        if (term) {
            queueables = queueables.filter(function(element) {
                return formatString(element.name).toLowerCase().includes(term);
            });
        }

        // Loop through all available functions, placing them into
        // the content as small buttons that may be used while an instance
        // is active.
        $(queueables).each(function(i, v) {
            let format = formatString(v.name);
            // Add the button to the available queueables.
            // Including data attributes for searching.
            panel.elements.queueablesContent.append(`
                <button data-formatted="${format}" data-function="${v.name}" type="button" class="m-1 btn btn-sm btn-primary queue-function" style="font-size: 12px;">
                    ${format}
                </button>
            `);
        });
    }

    /**
     * Clear and regenerate the available queued functions within the container for them.
     */
    function generateAvailableQueued() {
        // Clear out any content present in the table before.
        panel.elements.queuedTableBody.empty();

        // Loop through all current queued functions, adding them to the
        // table that contains all queued for the current instance.
        $(panel.data.queued).each(function(i, v) {
            // Add function to available current queued functions.
            // Note that only the ones that exist on request are shown.
            panel.elements.queuedTableBody.append(`
                <tr data-pk="${v.pk}">
                    <td>${formatString(v.function)}</td>
                    <td>${v.queued}</td>
                    <td>${v.eta}</td>
                </tr>
            `);
        });
    }

    /**
     * Setup the queue functions panel, populating the content with all available functions.
     */
    function setupQueueFunctionOptions() {
        // Generate all available queueables, no search term
        // included at this point.
        generateAvailableQueueables();
    }

    /**
     * Setup the table that contains information about the currently queued functions for an instance.
     */
    function setupQueueFunctionQueued() {
        // Generate all currently queued functions.
        generateAvailableQueued();
    }

    /**
     * Initialize the queue function panel, setting up available queued functions.
     */
    function initializeQueueFunctionPanel() {
        // Setup the queueables options once during initialization,
        // making sure we setup the options on initial load.
        setupQueueFunctionOptions();
        // Setup queued functions for the selected instance
        // once during initialization.
        setupQueueFunctionQueued();

        // Hide the loader and display the configured queueables
        // that have been setup above.
        showPanel(panel.elements.content, panel.elements.loader);
    }

    /**
     * Build out the listeners and events that deal with queue functions.
     */
    async function setupQueueFunctionHandlers() {
        // The queue function panel should be modified properly
        // when the active instance is changed to a different instance selection.
        panel.elements.instanceTable.on("click", ".instance-select", updateQueueFunctions);

        // Searching for a function should modify the content to only
        // display functions that match based on name.
        panel.elements.customSearch.keyup(function() {
            // Regenerate all available queueables to match the search
            // terms provided.
            generateAvailableQueueables($(this).val());
        });

        // Make sure our custom duration type buttons all properly update
        // the main duration type button's text.
        panel.elements.customDurationSeconds.click(function() {
            // Update main dropdown button to use proper seconds text.
            panel.elements.customDurationType.text("Seconds");
        });
        panel.elements.customDurationMinutes.click(function() {
            // Update main dropdown button to use proper minutes text.
            panel.elements.customDurationType.text("Minutes");
        });
        panel.elements.customDurationHours.click(function() {
            // Update main dropdown button to use proper hours text.
            panel.elements.customDurationType.text("Hours");
        });


        // Setup the listeners that deal with selecting a certain duration
        // amount for the queued function, "now" or "custom" can be chosen.
        panel.elements.customNow.click(function() {
            // Make sure the custom now button is set to a disabled state.
            // and the custom custom button is enabled.
            panel.elements.customNow.attr("disabled", true);
            panel.elements.customCustom.attr("disabled", false);

            // Make sure we modify the "Custom" button to use the
            // proper border radius, since no additional options are present now.
            panel.elements.customCustom.css({
                "border-top-right-radius": "5px",
                "border-bottom-right-radius": "5px"
            });

            // Hide any of our custom custom content that is only
            // enabled when the custom button is enabled.
            panel.elements.customDuration.attr("disabled", true).fadeOut(100);
            panel.elements.customDurationType.attr("disabled", true).fadeOut(100);
        });

        // Setup the listeners that deal with selecting the custom option
        // for choosing queued function durations.
        panel.elements.customCustom.click(function() {
            // Make sure the custom custom button is set to a disabled state
            // and the custom now button is enabled.
            panel.elements.customCustom.attr("disabled", true);
            panel.elements.customNow.attr("disabled", false);

            // Make sure we modify the "custom" button to now use
            // proper border radius.
            panel.elements.customCustom.css({
                "border-top-right-radius": "0",
                "border-bottom-right-radius": "0"
            });

            // Display the custom content that is only enabled when
            // the custom button is enabled.
            panel.elements.customDuration.attr("disabled", false).fadeIn(100);
            panel.elements.customDurationType.attr("disabled", false).fadeIn(100);
        });

        // Clicking on the queue flush button should attempt to clear
        // out all functions currently queued for the selected instance.
        panel.elements.flushQueue.click(function() {
            // Collect some information before deciding how to
            // deal with the queue flushing.
            let instance = activeInstance();
            let name = activeInstanceName();
            let state = activeInstanceStatus();

            // We should only even try to flush a queue if
            // the selected instance is running.
            if (state === "stopped") {
                // Instance selected is stopped, notify user about
                // inability to handle flushing.
                generateToast("Flush Queue", `Queued functions cannot be flushed while <em>${name}</em> is stopped.`, "warning");
            } else {
                // Instance selected is running or paused, generate a warning if no queued
                // functions are even present, or run functionality to flush.
                if (panel.elements.queuedTableBody.find("tr").length === 0) {
                    // No queued functions.
                    generateToast("Flush Queue", `No functions are currently queued up to execute against <em>${name}</em>.`, "warning");
                } else {
                    // Some queued functions are present, let's go ahead and remove them.
                    eel.dashboard_queue_function_flush(instance)();
                }
            }

        });

        // Clicking on any of the function buttons should attempt to
        // queue up the function for the instance that's selected.
        panel.elements.queueablesContent.on("click", ".queue-function", function() {
            // Collect some information before deciding how to
            // treat the potential queued function.
            let _function = $(this).data("function");
            let formatted = $(this).data("formatted").toLowerCase();
            // Instance information.
            let instance = activeInstance();
            let name = activeInstanceName();
            let state = activeInstanceStatus();

            // We should only ever actually send the queue function
            // signal if the selected instance is running.
            if (state === "stopped") {
                // Instance selected is stopped, generate a toast letting
                // the user know that they can not queue functions yet.
                generateToast("Queue Function", `Function: <strong>${formatted}</strong> cannot be queued while <em>${name}</em> is stopped.`, "warning");
            } else {
                let duration = 0;
                let durationType = panel.elements.customDurationType.text();

                // We need to derive some information about what kind of duration
                // or wait period will be used for the function.
                if (panel.elements.customCustom.is(":disabled")) {
                    // A custom duration is being used. Make sure the user
                    // has entered a custom value of some sort.
                    if (panel.elements.customDuration.val()) {
                        duration = panel.elements.customDuration.val();
                    } else {
                        return generateToast("Queue Function", `You must enter a valid <strong>duration</strong> if the <em>custom</em> duration button is selected.`, "danger");
                    }
                }

                // The instance selected is either running or paused,
                // we can go ahead and queue up our function.
                // Messages and modifications to the content are handled
                // by our websockets, so we can fire and forget this function.
                eel.dashboard_queue_function(instance, _function, duration, durationType)();
            }
        });
    }

    // Begin functionality to actually initialize and setup queue functions panel.
    initializeQueueFunctionPanel();
    // Setup any listeners or events used by queue function panel.
    await setupQueueFunctionHandlers();

    // Ensure our queue function panel os present within the globally
    // available update functions, so that we can properly update on instance selection change.
    updateFunctions["queueFunction"] = updateQueueFunctions;
});