/**
 * artifacts.js
 */
$(document).ready(function() {
    let elements = {
        artifactsTableLoader: $(".artifactsTableLoader"),
        artifactsSelectorContainer: $("#artifactsInstanceSelectorContainer"),
        artifactsSelectorSelect: $("#artifactsInstanceSelectorSelect"),
        artifactsContent: $("#artifactsContent"),
        artifactsTableContainer: $("#artifactsTableContainer"),
    };

    function buildTable(instance) {
        // Build the actual artifacts table.
        // Ensuring we empty the table before anything.
        elements.artifactsTableContainer.empty();

        let html = `
            <table id="artifactsTable" class="table table-sm table-hover">
                <thead>
                    <tr>
                        <th>Image</th>
                        <th>Key</th>
                        <th>Name</th>
                        <th>Tier</th>
                        <th>Owned</th>
                        <th>Toggle</th>
                    </tr>
                </thead>
                <tbody>
        `;
        for (let artifact of instance.artifacts.artifacts) {
            html += `
                <tr data-artifact="${artifact.artifact.key}" data-instance="${instance.pk}">
                    <td><img height="25" width="25" src="${artifact.artifact.image}"></td>
                    <td>${artifact.artifact.key}</td>
                    <td>${formatString(artifact.artifact.name)}</td>
                    <td data-order="${artifact.artifact.tier.pk}">${artifact.artifact.tier.name}</td>
                    <td class="artifact-owned" data-owned="${artifact.owned}" data-order="${artifact.owned ? 1 : 0}">${artifact.owned ? `<span class="fa fa-2x fa-check text-primary"></span>` : `<span class="fa fa-2x fa-times text-danger"></span>`}</td>
                    <td><button class="btn btn-sm btn-primary toggle-artifact">Toggle</button></td>
                </tr>
            `;
        }
        // Ensure we include the ending element before appending our table
        // to the table element.
        html += "</tbody></table>";

        // Add dynamic content to the artifacts table now.
        elements.artifactsTableContainer.append(html);

        let table = $("#artifactsTable");

        // Ensure our table is also initialized as a datatable.
        // This happens each time a new instance is selected.
        table.DataTable({
            lengthChange: false,
            pageLength: 50,
            order: [[3, "asc"]],
            columnDefs: [
                {targets: [0], orderable: false}
            ]
        });

        // Update the table to also support our click callbacks
        // on any of the toggle buttons.
        table.on("click", ".toggle-artifact", toggleOwnedValue)
    }

    async function reloadArtifactsTable(instance, hideAndShow) {
        if (typeof instance !== "object") {
            instance = await eel.artifacts_information(instance)();
        }

        if (hideAndShow) {
            // Hide the panel and then begin building out
            // the table the contains all instance artifacts.
            hidePanel(elements.artifactsContent, elements.artifactsTableLoader, function() {
                buildTable(instance);
                // Display the panel once our table is built out.
                showPanel(elements.artifactsContent, elements.artifactsTableLoader);
            });
        } else {
            // Hiding and showing will not take place, just build our table
            // and display our panel.
            buildTable(instance);
            // Display the panel once our table is built out.
            showPanel(elements.artifactsContent, elements.artifactsTableLoader);
        }
    }

    function buildArtifactsTable(data) {
        // Build out the artifacts table.
        // We display all artifacts and provide
        // an interface to allow toggling of owned/unowned.

        // If multiple instances are currently available,
        // we should display a selector to change the the selected
        // instances information.
        if (data.instances.length > 1) {
            // Make sure the container has been properly
            // shown so that on main display, it can be used.
            elements.artifactsSelectorContainer.show();
            // Update the selector to contain all proper
            // options that we can select.
            for (let instance of data.instances) {
                elements.artifactsSelectorSelect.append($("<option>", {value: instance.pk, text: instance.name}));
            }

            // Setup the click listener so we can properly swap between instances.
            // Swapping between them should reload the table with information
            // for the instance.
            elements.artifactsSelectorSelect.change(function() {
                reloadArtifactsTable($(this).val(), true);
            });
        }

        // Load the base table with our current instance information.
        // Regardless of whether or not multiple instances are available.
        reloadArtifactsTable(data.instances[0]);

        // Hide out loader and display our table once it's been built
        // out successfully and everything is ready to be displayed.
        elements.artifactsTableLoader.fadeOut(50, function() {
            elements.artifactsContent.fadeIn(100);
        });
    }

    async function loadArtifactsTable() {
        // Load the artifacts table by grabbing the artifacts information
        // asynchronously to display all artifacts available.
        let data = await eel.artifacts_information()();

        // Using the eel module to communicate with the backend
        // so we have the data needed to populate tables.
        buildArtifactsTable(data);
    }

    async function toggleOwnedValue(button) {
        // Whenever a toggle button is pressed, we can use this function
        // to send the signal to our backend to update the owned status of the
        // artifact in question for the instance.
        let row = $(button.target).closest("tr");
        let owned = $(button.target).closest("tr").find(".artifact-owned");

        // Grab and flip the old owned state before
        // messing with any of our frontend values.
        let newStatus = !owned.data("owned");

        // Update the owned row's data and our html.
        // Changing span value and data.
        owned.data("owned", newStatus);
        owned.attr("data-order", newStatus ? 1 : 0);
        owned.html(newStatus ? `<span class="fa fa-2x fa-check text-primary"></span>` : `<span class="fa fa-2x fa-times text-danger"></span>`);

        // Update the datatable so that we can properly sort by the owned
        // value of the artifact toggled.
        let table = $("#artifactsTable");
        // Grab row and invalidate it now that our attributes
        // have been updates as intended.
        table.DataTable().rows(row).invalidate();

        // Send signal to backend to update the owned artifact
        // for this particular instance.
        await eel.artifacts_toggle(row.data("artifact"), row.data("instance"), newStatus)();
    }

    // Run our load artifacts function once when everything
    // is ready and defined.
    loadArtifactsTable();
});