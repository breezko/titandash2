/**
 * instances.js
 */
$(document).ready(async function() {
    /**
     * Grab the asynchronous data used by the instances panel.
     */
    async function grabData() {
        // Just grabbing instances information with no additional
        // information needed.
        return await eel.base_instances_available()()
    }

    let panel = {
        data: await grabData(),
        elements: {
            removeModal: $("#dashboardRemoveInstanceModal"),
            loader: $("#dashboardInstancesLoader"),
            content: $("#dashboardInstancesContent"),
            table: $("#dashboardInstancesTable"),
            addButton: $("#dashboardInstanceAddButton"),
            confirmRemoveButton: $("#dashboardConfirmRemoveInstance")
        },
    };

    /**
     * Given an instance, add the instance to the table of available instances.
     */
    function addToTable(instance) {
        // Generate the html that will be appended to the table body that's
        // available and present already.
        let html = `
            <tr data-pk="${instance.pk}" data-name="${instance.name}">
                <td>${instance.name}&nbsp;&nbsp;<span class="fas fa-edit instance-name" style="cursor: pointer;"></span></td>
                <td class="text-uppercase instance-state">${instance.state}</td>
                <td><button class="btn w-100 btn-sm btn-primary instance-select">Select</button></td>
                <td><button class="btn w-100 btn-sm btn-primary instance-remove">Remove</button></td>
            </tr>
        `;

        // Add newly created html to the table.
        panel.elements.table.find("tbody").append(html);
    }

    /**
     * Retrieve a count of the current amount of instances available within the instances panel.
     */
    function instancesPresent() {
        return $(".instance-select").length;
    }

    function instanceIsSelected() {
        return $(".instance-select:disabled").length;
    }

    function initializeInstancesPanel() {
        // Begin by initializing and building out the instances table
        // with the information about instances currently available.
        panel.elements.table.empty();

        // Begin building the html that will be inserted
        // into the instances table.
        let html = `
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Status</th>
                    <th>Select</th>
                    <th>Remove</th>
                </tr>
            </thead>
            <tbody>
        `;

        // We need to loop through our available instances
        // data so we can add each set of information proper.
        $.each(panel.data, function(index, value) {
            if (index === 0) {
                html += `
                    <tr data-pk="${value.pk}" data-name="${value.name}">
                        <td>${value.name}&nbsp;&nbsp;<span class="fas fa-edit instance-name" style="cursor: pointer;"></span></td>
                        <td class="text-uppercase instance-state">${value.state}</td>
                        <td><button disabled class="btn w-100 btn-sm btn-success instance-select">Selected</button></td> 
                        <td><button disabled class="btn w-100 btn-sm btn-primary instance-remove">Remove</button></td>
                    </tr>
                `;
            } else {
                html += `
                    <tr data-pk="${value.pk}" data-name="${value.name}">
                        <td>${value.name}&nbsp;&nbsp;<span class="fas fa-edit instance-name" style="cursor: pointer;"></span></td>
                        <td class="text-uppercase instance-state">${value.state}</td>
                        <td><button class="btn w-100 btn-sm btn-primary instance-select">Select</button></td> 
                        <td><button class="btn w-100 btn-sm btn-primary instance-remove">Remove</button></td>
                    </tr>
                `;
            }
        });

        // Ensure data is appended to our table element.
        // Before showing anything.
        panel.elements.table.append(html);

        // The initial initialization should also deal with only a "single"
        // instance being available, which should disable the option to remove.
        if (instancesPresent() <= 1) {
            panel.elements.table.find(".instance-remove").attr("disabled", true);
        }

        // Hide the loader and display the newly configured
        // table with all data present.
        panel.elements.loader.fadeOut(50, function() {
            panel.elements.content.fadeIn(100);
        });
    }

    /**
     * Build out the click listeners that are used to deal with instances functionality.
     */
    async function setupInstancesPanelHandlers() {
        // We should be able to click on different instances to "select" them,
        // making sure we only have one "selected" at any given time.
        panel.elements.table.on("click", ".instance-select", function() {
            // The instance that was previously selected should
            // be made into a normal non disabled button.
            $(".instance-select:disabled").attr("disabled", false).closest("tr").find(".instance-remove").attr("disabled", false);

            // The instance clicked on should be made into the
            // currently "active" one (ie: disabled).
            $(this).attr("disabled", true);
            // The remove button for an instance should be disabled
            // if the instance is selected.
            $(this).closest("tr").find(".instance-remove").attr("disabled", true);

            // Before swapping the text to proper "Selected", set all buttons
            // to "select, since we are swapping.
            $(".instance-select:contains('Selected')").text("Select").removeClass("btn-success").addClass("btn-primary");
            // Instance clicked on should have it's text modified to be "selected", and change
            // the class so that the color is different for selected instances.
            $(this).text("Selected").removeClass("btn-primary").addClass("btn-success");
        });

        // We should be able to open and click on the "add instance" context
        // menu option to generate a new instance in the database.
        panel.elements.addButton.click(async function() {
            // Add a new instance through our eel instance, data returned
            // will be the json for the new instance.
            let instance = await eel.dashboard_add_instance()();

            // Add the new instance to our table of information.
            // Simply just appending it to the bottom of the table.
            addToTable(instance);

            // If only a single instance is present after being added, we need to
            // default to this being the selected instance, and disabling the option to remove.
            if (instancesPresent() <= 1) {
                panel.elements.table.find(".instance-select").click();
                panel.elements.table.find(".instance-remove").attr("disabled", true);
            }

            // Generate a toast to display information about the new instance that's
            // been created in the backend.
            generateToast("Add Bot Instance", `<em>${instance.name}</em> has been added successfully.`, "success")
        });

        // We should be able to delete any of the instances present
        // by clicking on the "remove" buttons available.
        panel.elements.table.on("click", ".instance-remove", function() {
            // Before even opening up the modal, make sure we
            // update the confirmation button to contain the proper
            // id that will be removed if "yes" is selected.
            panel.elements.confirmRemoveButton.data("pk", $(this).closest("tr").data("pk"));
            panel.elements.confirmRemoveButton.data("name", $(this).closest("tr").data("name"));

            // Open up the modal that contains a warning about
            // removing instances and providing a confirmation.
            panel.elements.removeModal.modal("show");
        });

        // Make sure the removal confirmation button will properly remove the instance
        // and remove the table row from our table.
        panel.elements.confirmRemoveButton.click(async function() {
            // Grab the primary key for this instance since clicking and showing
            // the remove button will include it as data on the button.
            let instancePk = $(this).data("pk");

            await eel.dashboard_remove_instance(instancePk)();

            // Remove the table row from our table that is present
            // for our currently selected instance for deletion.
            panel.elements.table.find(`tr[data-pk="${instancePk}"`).remove();

            // Hide the modal after we've successfully removed the instance
            // from the database.
            panel.elements.removeModal.modal("hide");

            // If only a single instance is present now, we need to disable the
            // option to remove the last remaining instance.
            if (instancesPresent() <= 1) {
                panel.elements.table.find(".instance-remove").attr("disabled", true);
            }
            // We also need to make sure that on removal, we ensure that an instance
            // is still selected.
            if (!instanceIsSelected()) {
                panel.elements.table.find(".instance-select").first().click();
            }
            // Display a toast message about the instance that's being removed.
            generateToast("Remove Bot Instance", `<em>${$(this).data("name")}</em> has been removed successfully.`, "success");

            // Reset data attribute.
            $(this).data("pk", null);
            $(this).data("name", null);

            // Ensure we perform a click on the selected instance, regardless
            // the ones that's selected, we need to make sure all proper
            // panels are updated on this event.
            panel.elements.table.find(".instance-select:disabled").click();
        });

        // If a user hovers over the instance name change button, we should modify the look slightly
        // to treat the icon as a button.
        panel.elements.table.on("mouseenter", ".instance-name", function() {
            $(this).css({filter: "brightness(0.7)"});
        });
        // Mouse leave should also set our brightness back to default.
        panel.elements.table.on("mouseleave", ".instance-name", function() {
           $(this).css({filter: "brightness(1)"});
        });

        // If a user presses on any of the instance name change buttons, we should initiate the functionality
        // to allow a user to change the name of the instance.
        panel.elements.table.on("click", ".instance-name", function() {
            // Store the information about the current name.
            let current = $(this).closest("tr").data("name");
            let content = $(this).closest("td");

            // Begin by making sure we've swapped out the current name and button
            // into an input field with a confirmation and cancel button to update.
            content.html(`
                <div class="form-group form-inline m-0">
                    <input class="form-control instance-new-name" style="height: 32px;;" type="text" value="${current}">
                    <span class="fa fa-times text-danger ml-2 instance-cancel-new-name"></span>
                    <span class="fa fa-check text-success ml-2 instance-save-new-name"></span>
                </div>
            `);
        });

        // If a user pressed the save button while editing an instance name, update the instance associated
        // with that table row and revert the row back to it's original state with the new name.
        panel.elements.table.on("click", ".instance-save-new-name", async function() {
            // This element is present if the save new name button is available.
            let newName = $(this).closest("td").find(".instance-new-name").val();
            let instance = $(this).closest("tr").data("pk");

            // Attempt to save the instance through the eel module.
            // Asynchronous call to backend.
            await eel.dashboard_save_instance_name(instance, newName)();

            // After the save, we should put the name row back to it's original state.
            // Update data name to newest value.
            $(this).closest("tr").data("name", newName);
            // Revert html of table element to original state.
            $(this).closest("td").html(`
                ${newName}&nbsp;&nbsp;
                <span class="fas fa-edit instance-name" style="cursor: pointer;"></span>
            `);

            // Generate a toast with some information about the new name
            // for the instance being modified.
            generateToast("Rename Bot Instance", `<em>${newName}</em> has been renamed successfully.`, "success");
        });

        // If a user pressed the cancel button while editing an instance name, just revert the html back
        // to the original state.
        panel.elements.table.on("click", ".instance-cancel-new-name", function() {
            // Grab the current name that is not changing.
            let currentName = $(this).closest("tr").data("name");
            // Only need to update html here.
            $(this).closest("td").html(`
                ${currentName}&nbsp;&nbsp;
                <span class="fas fa-edit instance-name" style="cursor: pointer;"></span>
            `);
        });
    }

    // Begin the actual functionality to call and populate our
    // instances table.
    initializeInstancesPanel();
    // Set-up any of the click listeners that are dealt with
    // by the instances panel on the dashboard.
    await setupInstancesPanelHandlers();
});