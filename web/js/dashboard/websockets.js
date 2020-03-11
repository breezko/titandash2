/**
 * websockets.js
 */
$(document).ready(function() {
    let elements = {
        instancesTable: $("#dashboardInstancesTable"),
        queueFunctionTableBody: $("#dashboardQueueFunctionQueuedTableBody")
    };

    function updateInstanceState(instance, state) {
        // Update the status of the specified instances table row.
        elements.instancesTable.find(`tr[data-pk="${instance}"] .instance-state`).text(state);
    }

    eel.expose(base_generate_toast);
    function base_generate_toast(sender, message, typ, timeout) {
        // Same arguments as base toast utility.
        generateToast(sender, message, typ, timeout);
    }

    eel.expose(base_instance_stopped);
    function base_instance_stopped(pk) {
        // Whenever a bot instance is stopped, we need to properly update the different
        // dashboard panels to make sure proper data and available options are present.
        let selected = activeInstance();
        let instance = pk;

        // Update the status of the instance that has been stopped,
        // regardless of whether or not it's the selected instance.
        updateInstanceState(instance, "stopped");

        // If the instance stopped is also our selected instance,
        // we can perform some additional functionality to ensure
        // the dashboard is in the correct state.
        if (selected === instance) {
            updateFunctions["settings"]();
            updateFunctions["actions"]();
            updateFunctions["queueFunction"]();
        }
    }

    eel.expose(base_instance_started);
    function base_instance_started(pk) {
        // Whenever a bot instance is started, we need to properly update the different
        // dashboard panels to make sure proper data and available options are present.
        let selected = activeInstance();
        let instance = pk;

        // Update the status of the instance that has been stopped,
        // regardless of whether or not it's the selected instance.
        updateInstanceState(instance, "running");

        // If the instance started is also our selected instance,
        // we can perform some additional functionality to ensure
        // the dashboard is in the correct state.
        if (selected === instance) {
            updateFunctions["settings"]();
            updateFunctions["actions"]();
            updateFunctions["queueFunction"]();
        }
    }

    eel.expose(base_instance_updated);
    function base_instance_updated(pk, data) {
        // Whenever the base instance is updated properly, we can go ahead
        // and try to update the selected instance table.
        let selected = activeInstance();
        let instance = pk;

        // If the instance updated is also the one selected, we can perform
        // some additional functionality here.
        if (selected === instance) {
            // Include data to override the normal data retrieval.
            updateFunctions["selectedInstance"](data);
        }
    }

    eel.expose(base_queue_function_remove);
    function base_queue_function_remove(pk) {
        // Since we are using the unique primary key associated with a queued
        // function, we can just look to see if any queued function are present
        // within the table that match.
        elements.queueFunctionTableBody.find(`tr[data-pk="${pk}"`).fadeOut(100, function() {
            $(this).remove();
        });
    }

    eel.expose(base_queue_function_add);
    function base_queue_function_add(instance) {
        // Using the unique primary key to add the queued function directly
        // to the table that contains all functions.
        let tableRow = $(`
            <tr data-pk="${instance.pk}" style="display: none;">
                <td>${formatString(instance.function)}</td>
                <td>${instance.queued}</td>
                <td>${instance.eta}</td>
            </tr>
        `);

        // Add the row to our table and fade it in afterwords.
        tableRow.appendTo(elements.queueFunctionTableBody).fadeIn(100);
    }
});