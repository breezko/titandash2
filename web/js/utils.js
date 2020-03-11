/**
 * utils.js
 *
 * Placing all utility type functions that make dealing with data and eel more manageable.
 *
 * This file should be imported before any other javascript files to ensure functionality is available in scope.
 */

/**
 * Initialized panels can be placed into here so that functionality can be used by other dashboard pieces.
 */
let updateFunctions = {};

/**
 * Return the currently selected bot instances current primary key value.
 */
let activeInstance = function() {
    return $(".instance-select:disabled").closest("tr").data("pk");
};

/**
 * Return the currently selected bot instances current name.
 */
let activeInstanceName = function() {
    return $(".instance-select:disabled").closest("tr").data("name");
};

/**
 * Return the currently selected bot instances current state.
 */
let activeInstanceStatus = function() {
    return $(".instance-select:disabled").closest("tr").find(".instance-state").text();
};

/**
 * Return the currently selected configuration value.
 */
let selectedConfiguration = function() {
    return $("#dashboardSettingsSelectConfiguration").val();
};

/**
 * Return the currently selected window value.
 */
let selectedWindow = function() {
    return $("#dashboardSettingsSelectWindow").val();
};

/**
 * Return whether or not shortcuts are currently enabled.
 */
let shortcutsEnabled = function() {
    return $("#dashboardSettingsCheckboxShortcuts").prop("checked");
};

/**
 * Hide the specified panel, displaying a loader while hidden.
 */
let hidePanel = function(content, loader, cb) {
    content.fadeOut(50, function() {
        loader.fadeIn(50, cb);
    });
};

/**
 * Show the specified panel, hiding the loader while shown.
 */
let showPanel = function(content, loader, cb) {
    loader.fadeOut(50, function() {
        content.fadeIn(50, cb);
    });
};

/**
 * Return the current timestamp based on the users timezone information.
 */
let currentTimestamp = function() {
    let date = new Date();
    let format = "AM";
    let hour = date.getHours();
    let minute = date.getMinutes();
    let second = date.getSeconds();

    if (hour > 11)
        format = "PM";
    if (hour > 12)
        hour = hour - 12;
    if (hour === 0)
        hour = 12;
    if (minute < 10)
        minute = "0" + minute;
    if (second < 10)
        second = "0" + second;

    return `
        ${date.getMonth() + 1}/${date.getDate()}/${date.getFullYear()} ${hour}:${minute}:${second} ${format}
    `;
};

/**
 * Generate an alert within the dashboard, displaying in a general view, and also
 * being placed within the alerts tab on the dashboard.
 */
let generateToast = function(sender, message, typ, timeout) {
    let icon;
    let remove = timeout | 5000;

    switch (typ) {
        case "success":
            icon = "fa-check";
            break;
        case "info":
            icon = "fa-info";
            break;
        case "warning":
            icon = "fa-exclamation-triangle";
            break;
        case "danger":
            icon = "fa-exclamation-circle";
            break;
    }

    let toast = $(`
        <div class="toast ml-auto" style="z-index: 10000 !important;" role="alert" data-delay="700" data-autohide="false">
            <div class="toast-header">
                <span class="mr-2 fas ${icon} text-${typ}"></span>
                <strong class="mr-auto text-${typ}">${sender}</strong>
                <small>${currentTimestamp()}</small>
                <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="toast-body">${message}</div>
        </div>
    `);
    toast.appendTo($("#toastContainer"));
    toast.toast("show");

    setTimeout(function () {
        toast.fadeOut(400, function () {
            toast.remove();
        });
    }, remove);
};


/**
 * Format the given value into a proper titled string.
 */
let formatString = function(value) {
    // Replace all underscores with a proper space.
    value = value.replace(/_/g, " ")
    // Begin capitalizing each word available in the
    // value without any underscores.
    let _split = value.toLowerCase().split(" ");

    for (let i = 0; i < _split.length; i++) {
        // Assign back to the array as proper title case.
        _split[i] = _split[i].charAt(0).toUpperCase() + _split[i].substring(1);
    }

    // Join the split string back together now that
    // parsing is finished.
    return _split.join(" ");
};

let Countdown = function(datetime, formatted, element, disablePadding) {
    // Create a reference to the original datetime that this countdown
    // is tracking to. We can use this to derive next steps when checking information.
    this.originalDateReference = datetime;
    this.originalDate = new Date(datetime);

    // Create the interval functionality that will count up while running
    // to update the stopwatch value.
    let interval = setInterval(function() {
        // Retrieve the current timestamp that can be used to determine
        // the distance between the original datetime and the current datetime.
        let distance = this.originalDate - new Date().getTime();

        // Derive the hours minutes and seconds before
        // applying any of our padding options.
        let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        let seconds = Math.floor((distance % (1000 * 60)) / 1000);

        if (hours < 0) { hours = 0; }
        if (minutes < 0) { minutes = 0; }
        if (seconds < 0) { seconds = 0; }

        // Apply our default padding, this can be disabled by ensuring that
        // the disable padding argument is included.
        if (!disablePadding) {
            if (hours < 10) { hours = "0" + hours; }
            if (minutes < 10) { minutes = "0" + minutes; }
            if (seconds < 10) { seconds = "0" + seconds; }
        }

        // We always want to at least update our element so that the countdown
        // contains the properly formatted time until the countdown is done.
        element.text(`(${formatted} (${hours}:${minutes}:${seconds})`);

        // If the distance has exceeded zero (completed), we should also go ahead and destroy our
        // interval manually and update the text to the proper "ready" text.
        if (distance <= 0) {
            // Clear the interval we're actually in now.
            // Ensure update doesn't happen after setting ready state.
            clearInterval(interval);
            // Update elements html so that a proper "ready" text is present.
            element.text("ready...");
        }
    }.bind(this), 1000);

    /**
     * Destroy Stopwatch.
     */
    this.destroy = function() {
        // Call clear interval to ensure that updates are stopped
        // once this is called on the stopwatch instance.
        clearInterval(interval);
    }
};

let Stopwatch = function(datetime, formatted, element, disablePadding) {
    // Create a reference to the original datetime that this stopwatch
    // is tracking from. We can use this to derive next steps when checking information.
    this.originalDateReference = datetime;
    this.originalDate = new Date(datetime).getTime();

    // Create the interval functionality that will count up while running
    // to update the stopwatch value.
    let interval = setInterval(function() {
        // Retrieve the current timestamp that can be used to determine
        // the distance between now and the original datetime.
        let distance = new Date().getTime() - this.originalDate;
        let output;

        // Derive the days, hours, minutes, seconds and milliseconds
        // before applying any padding options.
        let days = Math.floor(distance / (1000 * 60 * 60 * 24)); distance = distance % (1000 * 60 * 60 * 24);
        let hours = Math.floor(distance / (1000 * 60 * 60)); distance = distance % (1000 * 60 * 60);
        let minutes = Math.floor(distance / (1000 * 60)); distance = distance % (1000 * 60);
        let seconds = Math.floor(distance / (1000)); distance = distance % (1000);
        let milliseconds = distance;

        // Apply default padding, this can be disabled by ensuring that
        // the disable padding argument is included.
        if (!disablePadding) {
            if (days < 10) { days = "0" + days; }
            if (hours < 10) { hours = "0" + hours; }
            if (minutes < 10) { minutes = "0" + minutes; }
            if (seconds < 10) { seconds = "0" + seconds; }
            if (milliseconds < 10) { milliseconds = "00" + milliseconds; }
            if (milliseconds < 100 && milliseconds > 10) { milliseconds = "0" + milliseconds; }
        }

        // Determine what format should be used to actually set and display
        // the information about this stopwatch.
        if (distance < 0) { output = "00:00:00:00.000"; }
        else if (days > 0) { output = `${days}:${hours}:${minutes}:${seconds}.${milliseconds}`; }
        else { output = `${hours}:${minutes}:${seconds}.${milliseconds}`; }

        // Finally, set the output, ensuring the text is set to
        // whatever distance value was parsed above.
        element.text(`${formatted} (${output})`);
    }.bind(this), 20);

    /**
     * Destroy Stopwatch.
     */
    this.destroy = function() {
        // Call clear interval to ensure that updates are stopped
        // once this is called on the stopwatch instance.
        clearInterval(interval);
    }
};