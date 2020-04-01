/**
 * sessions.js
 */
$(document).ready(function() {
    let elements = {
        sessionsTableLoader: $(".sessionsTableLoader"),
        sessionsSelectorContainer: $("#sessionsInstanceSelectorContainer"),
        sessionsSelectorSelect: $("#sessionsInstanceSelectorSelect"),
        sessionsContent: $("#sessionsContent"),
        sessionsTableContainer: $("#sessionsTableContainer")
    };

    function buildTable(instance) {
        // Build the actual sessions table.
        // Ensuring we empty the table before anything.
        elements.sessionsTableContainer.empty();

        let html = `
            <table id="sessionsTable" class="table table-sm table-hover">
                <thead>
                    <tr>
                        <th>UUID</th>
                        <th>Started</th>
                        <th>Stopped</th>
                        <th>Duration</th>
                        <th>Version</th>
                        <th>Prestiges</th>
                    </tr>
                </thead>
                <tbody>        
        `;
        for (let session of instance.sessions.sessions) {
            html += `
                <tr>
                    <td><a href="${session.url}">${session.uuid}</a></td>
                    <td data-order="${session.started.epoch}">${session.started.formatted}</td>
                    <td data-order="${session.stopped.epoch}">${session.stopped.formatted}</td>
                    <td data-order="${session.duration.seconds}">${session.duration.formatted}</td>
                    <td>${session.version}</td>
                    <td>${session.prestiges.length}</td>
                </tr>   
            `;
        }
        // Ensurwe we include the ending element before appending our
        // table to the table element.
        html += "</tbody></table>";

        // Add dynamic content to the sessions table now.
        elements.sessionsTableContainer.append(html);

        // Grab an instance of our dynamic table now.
        // We can use this to setup the datatable and deal
        // with any additional functionality required.
        let table = $("#sessionsTable");

        // Initialize datatable proper.
        table.DataTable({
            searching: false,
            lengthChange: false,
            pageLength: 50,
            order: [[1, "desc"]],
            columnDefs: [
                {targets: [5], orderable: false}
            ]
        });
    }

    async function reloadSessionsTable(instance, hideAndShow) {
        // Reload the sessions table (or just load). Based on whether or not
        // we are initializing or selecting a different instance. Show information
        // required within the table.
        if (typeof instance !== "object") {
            // Instance is not an object, so it's probably an id of the
            // instance selected, grab the data we need.
            instance = await eel.sessions_information(instance)();
        }

        if (hideAndShow) {
            // Hiding the panel before building our table and displaying it.
            // We do this so we can switch between instances without weird html effects.
            hidePanel(elements.sessionsContent, elements.sessionsTableLoader, function() {
                buildTable(instance);
                // Display the panel again once building of the
                // table has concluded properly.
                showPanel(elements.sessionsContent, elements.sessionsTableLoader);
            });
        } else {
            // Otherwise, just build the table and then display
            // our sessions content like we normally would.
            buildTable(instance);
            // Display panel once table is built out.
            showPanel(elements.sessionsContent, elements.sessionsTableLoader);
        }
    }

    function buildSessionsTable(data) {
        // Build out the sessions table.
        // We display all sessions and provide
        // a simple table to view information.

        // If multiple instances are currently available, we should display
        // a selector to change the selected instances information.
        if (data.instances.length > 1) {
            // Make sure the container has been properly shown, so that
            // on main display, it can be used by the user.
            elements.sessionsSelectorContainer.show();
            // Update the selector to contain all proper options
            // that can choose from as a user.
            for (let instance of data.instances) {
                elements.sessionsSelectorSelect.append($("<option>", {value: instance.pk, text: instance.name}));
            }

            // Setup the click listener so we can properly swap betwwen instances.
            // Swapping an instance should reload the table with newest information.
            elements.sessionsSelectorSelect.change(function() {
                reloadSessionsTable($(this).val(), true);
            });
        }

        // Load the base table with our current information.
        // Regardless of whether or not multiple instances are available.
        reloadSessionsTable(data.instances[0]);

        // Hide our loader and display the table once it's been built
        // out properly and everything is now ready.
        showPanel(elements.sessionsContent, elements.sessionsTableLoader);
    }

    async function loadSessionsTable() {
        // Load the sessions table by grabbing the sessions information
        // asyynchronously to display all sessions available.
        let data = await eel.sessions_information()();

        // Using the data retrieved through eel to ensure
        // that we properly build the table.
        buildSessionsTable(data);
    }

    // Run our load sessions function once everything is ready.
    loadSessionsTable();
});