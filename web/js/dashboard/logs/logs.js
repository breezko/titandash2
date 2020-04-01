/**
 * logs.js
 */
$(document).ready(async function() {
    // No need to worry about initial data grabbing or other functionality
    // here, since logs are only ever outputted in the frontend when one
    // is emitted and the instance selected is where the log originated from.
    let panel = {
        elements: {
            instancesTable: $("#dashboardInstancesTable"),
            initial: $("#dashboardLogInitialText"),
            body: $("#dashboardLogBody"),
            content: $("#dashboardLogRecords")
        }
    };

    function removeFirstRecord() {
        // Remove the first available record from the log content.
        $(".log-record").first().remove();
    }

    function currentRecords() {
        return $(".log-record").length;
    }

    function addRecord(instance, record) {
        // Only even attempt to add the log record when
        // the selected instance is the same as the emitted one.
        if (activeInstance() === instance) {
            // If there's already the maximum amount of log records present,
            // go ahead and remove the first one to avoid lagging.
            if (currentRecords() >= 3000) {
                removeFirstRecord();
            }
            // If no logs are present yet, make sure we remove the initial
            // text before adding any logs.
            if (currentRecords() === 0) {
                panel.elements.initial.hide();
            }

            let encodedElement = $("<div>");

            // Set the text of our encoded element
            // to the records current state.
            encodedElement.text(record);

            panel.elements.content.append(`
                <code class="text-dark text-uppercase">
                    <small>
                        <strong>${encodedElement.html()}</strong>
                    </small>
                 </code>
                 <br/>
            `);

            // Make sure we auto-scroll to the bottom of the panel
            // since many logs can be present.
            panel.elements.body.scrollTop(panel.elements.body.prop("scrollHeight"));
        }
    }

    function clearLogs() {
        // Attempting to clear out all the logs from our log container,
        // this proves useful when a new instance is started.
        panel.elements.content.empty();
    }

    function initializeLogPanel() {
        // Initialize the log panel to a default state,
        // removing any log instances, and re-showing the
        // initial text present on first load.
        clearLogs();
        // Fade initial text in again.
        panel.elements.initial.fadeIn(100);
    }

    function setupLogPanelHandlers() {
        // Setup the event listeners and handlers used
        // that deal with the log panel.
        panel.elements.instancesTable.on("click", ".instance-select", initializeLogPanel);
    }

    // Setup all of the handlers associated
    // with the log panel.
    setupLogPanelHandlers();

    // The initialize function should also be included as a global.
    updateFunctions["initLogs"] = initializeLogPanel;
    // Make sure the add record function is available as a global
    // function so that we can use it elsewhere.
    updateFunctions["addLog"] = addRecord;
    // Make sure the clear function is included as a global function
    // as well so we can clear logs from anywhere.
    updateFunctions["clearLogs"] = clearLogs;
});