/**
 * prestiges.js
 */
$(document).ready(function() {
    let elements = {
        prestigesTableLoader: $(".prestigesTableLoader"),
        prestigesSelectorContainer: $("#prestigesInstanceSelectorContainer"),
        prestigesSelectorSelect: $("#prestigesInstanceSelectorSelect"),
        prestigesContent: $("#prestigesContent"),
        prestigesTableContainer: $("#prestigesTableContainer")
    };

    function buildTable(instance) {
        // Build the actual prestiges table.
        // Ensuring we empty the table before anything.
        elements.prestigesTableContainer.empty();

        let html = `
            <div class="row">
                <div class="col-sm text-center">
                    <small>Total Prestiges</small>   
                    <br/>
                    <strong>${instance.prestiges.count ? instance.prestiges.count : "N/A"}</strong> 
                </div>
                <div class="col-sm text-center">
                    <small>Average Duration</small>
                    <br/>
                    <strong>${instance.prestiges.average_duration ? instance.prestiges.average_duration : "N/A"}</strong>
                </div>
                <div class="col-sm text-center">
                    <small>Average Stage</small>
                    <br/>
                    <strong>${instance.prestiges.average_stage ? instance.prestiges.average_stage : "N/A"}</strong>
                </div>
            </div>
            <br/>
            <table id="prestigesTable" class="table table-sm table-hover">
                <thead>
                    <tr>
                        <th>Id</th>
                        <th>Session</th>
                        <th>Timestamp</th>
                        <th>Duration</th>
                        <th>Stage</th>
                        <th>Artifact</th>
                    </tr>
                </thead>
                <tbody>        
        `;
        for (let prestige of instance.prestiges.prestiges) {
            html += `
                <tr>
                    <td>${prestige.pk}</td>
                    <td><a href="${prestige.session.url}">${prestige.session.uuid}</a></td>
                    <td data-order="${prestige.timestamp.epoch}">${prestige.timestamp.formatted}</td>
                    <td data-order="${prestige.duration.seconds}">${prestige.duration.formatted}</td>
                    <td>${prestige.stage}</td>
                    <td>${prestige.artifact ? `<img height="25" width="25" src="${prestige.artifact.image}">` : "N/A"}</td>
                </tr>   
            `;
        }
        // Ensurwe we include the ending element before appending our
        // table to the table element.
        html += "</tbody></table>";

        // Add dynamic content to the prestiges table now.
        elements.prestigesTableContainer.append(html);

        // Grab an instance of our dynamic table now.
        // We can use this to setup the datatable and deal
        // with any additional functionality required.
        let table = $("#prestigesTable");

        // Initialize datatable proper.
        table.DataTable({
            searching: false,
            lengthChange: false,
            pageLength: 50,
            order: [[2, "desc"]],
            columnDefs: [
                {targets: [5], orderable: false}
            ]
        });
    }

    async function reloadPrestigesTable(instance, hideAndShow) {
        // Reload the prestiges table (or just load). Based on whether or not
        // we are initializing or selecting a different instance. Show information
        // required within the table.
        if (typeof instance !== "object") {
            // Instance is not an object, so it's probably an id of the
            // instance selected, grab the data we need.
            instance = await eel.prestiges_information(instance)();
        }

        if (hideAndShow) {
            // Hiding the panel before building our table and displaying it.
            // We do this so we can switch between instances without weird html effects.
            hidePanel(elements.prestigesContent, elements.prestigesTableLoader, function() {
                buildTable(instance);
                // Display the panel again once building of the
                // table has concluded properly.
                showPanel(elements.prestigesContent, elements.prestigesTableLoader);
            });
        } else {
            // Otherwise, just build the table and then display
            // our prestiges content like we normally would.
            buildTable(instance);
            // Display panel once table is built out.
            showPanel(elements.prestigesContent, elements.prestigesTableLoader);
        }
    }

    function buildPrestigesTable(data) {
        // Build out the prestiges table.
        // We display all prestiges and provide
        // a simple table to view information.

        // If multiple instances are currently available, we should display
        // a selector to change the selected instances information.
        if (data.instances.length > 1) {
            // Make sure the container has been properly shown, so that
            // on main display, it can be used by the user.
            elements.prestigesSelectorContainer.show();
            // Update the selector to contain all proper options
            // that can choose from as a user.
            for (let instance of data.instances) {
                elements.prestigesSelectorSelect.append($("<option>", {value: instance.pk, text: instance.name}));
            }

            // Setup the click listener so we can properly swap betwwen instances.
            // Swapping an instance should reload the table with newest information.
            elements.prestigesSelectorSelect.change(function() {
                reloadPrestigesTable($(this).val(), true);
            });
        }

        // Load the base table with our current information.
        // Regardless of whether or not multiple instances are available.
        reloadPrestigesTable(data.instances[0]);

        // Hide our loader and display the table once it's been built
        // out properly and everything is now ready.
        showPanel(elements.prestigesContent, elements.prestigesTableLoader);
    }

    async function loadPrestigesTable() {
        // Load the prestiges table by grabbing the prestiges information
        // asyynchronously to display all prestiges available.
        let data = await eel.prestiges_information()();

        // Using the data retrieved through eel to ensure
        // that we properly build the table.
        buildPrestigesTable(data);
    }

    // Run our load prestiges function once everything is ready.
    loadPrestigesTable();
});