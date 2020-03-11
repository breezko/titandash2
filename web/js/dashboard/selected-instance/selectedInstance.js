/**
 * selectedInstance.js
 */
$(document).ready(async function() {
    // Stopwatches.
    let stopwatches = {
        startedStopwatch: null,
        timestampStopwatch: null
    };

    // Countdowns.
    let countdowns = {
        raidAttackResetCountdown: null,
        nextBreakCountdown: null,
        breakResumeCountdown: null,
        nextMasterLevelCountdown: null,
        nextHeroesLevelCountdown: null,
        nextSkillsLevelCountdown: null,
        nextSkillsActivationCountdown: null,
        nextMiscellaneousActionsCountdown: null,
        nextHeadgearSwapCountdown: null,
        nextPerkCheckCountdown: null,
        nextPrestigeCountdown: null,
        nextRandomizedPrestigeCountdown: null,
        nextStatisticsUpdateCountdown: null,
        nextDailyAchievementCheckCountdown: null,
        nextMilestoneCheckCountdown: null,
        nextHeavenlyStrikeCountdown: null,
        nextDeadlyStrikeCountdown: null,
        nextHandOfMidasCountdown: null,
        nextFireSwordCountdown: null,
        nextWarCryCountdown: null,
        nextShadowCloneCountdown: null
    };

    async function grabData() {
        // Grabbing the instance information for the currently selected
        // instance, this is used to derive all information needed.
        return await eel.dashboard_instance_information(activeInstance())();
    }

    let panel = {
        data: await grabData(),
        baseElements: {
            instancesTable: $("#dashboardInstancesTable"),
            loader: $("#dashboardSelectedInstanceLoader"),
            content: $("#dashboardSelectedInstanceContent")
        },
        baseInformation: {
            name: $("#dashboardSelectedInstanceBaseInformationNameValue"),
            state: $("#dashboardSelectedInstanceBaseInformationStateValue"),
            session: $("#dashboardSelectedInstanceBaseInformationSessionValue"),
            started: $("#dashboardSelectedInstanceBaseInformationStartedValue"),
            function: $("#dashboardSelectedInstanceBaseInformationFunctionValue")
        },
        lastPrestigeInformation: {
            timestamp: $("#dashboardSelectedInstanceLastPrestigeTimestampValue"),
            stage: $("#dashboardSelectedInstanceLastPrestigeStageValue"),
            duration: $("#dashboardSelectedInstanceLastPrestigeDurationValue"),
            artifact: $("#dashboardSelectedInstanceLastPrestigeArtifactValue")
        },
        currentPropertiesInformation: {
            logFile: $("#dashboardSelectedInstanceCurrentPropertyLogFileValue"),
            configuration: $("#dashboardSelectedInstanceCurrentPropertyConfigurationValue"),
            window: $("#dashboardSelectedInstanceCurrentPropertyWindowValue"),
            shortcuts: $("#dashboardSelectedInstanceCurrentPropertyShortcutsValue"),
            currentStage: $("#dashboardSelectedInstanceCurrentPropertyCurrentStageValue"),
            newestHero: $("#dashboardSelectedInstanceCurrentPropertyNewestHeroValue"),
            raidAttackReset: $("#dashboardSelectedInstanceCurrentPropertyRaidAttackResetValue"),
            nextBreak: $("#dashboardSelectedInstanceCurrentPropertyNextBreakValue"),
            nextBreakResume: $("#dashboardSelectedInstanceCurrentPropertyNextBreakResumeValue"),
            nextArtifactUpgrade: $("#dashboardSelectedInstanceCurrentPropertyNextArtifactUpgradeValue"),
            nextMasterLevel: $("#dashboardSelectedInstanceCurrentPropertyNextMasterLevelValue"),
            nextHeroesLevel: $("#dashboardSelectedInstanceCurrentPropertyNextHeroesLevelValue"),
            nextSkillsLevel: $("#dashboardSelectedInstanceCurrentPropertyNextSkillsLevelValue"),
            nextSkillsActivation: $("#dashboardSelectedInstanceCurrentPropertyNextSkillsActivationValue"),
            nextMiscellaneousActions: $("#dashboardSelectedInstanceCurrentPropertyNextMiscellaneousActionsValue"),
            nextHeadgearSwap: $("#dashboardSelectedInstanceCurrentPropertyNextHeadgearSwapValue"),
            nextPerkCheck: $("#dashboardSelectedInstanceCurrentPropertyNextPerkCheckValue"),
            nextTimedThresholdPrestige: $("#dashboardSelectedInstanceCurrentPropertyNextTimedThresholdPrestigeValue"),
            nextRandomizedThresholdPrestige: $("#dashboardSelectedInstanceCurrentPropertyNextRandomizedThresholdPrestigeValue"),
            nextStatisticsUpdate: $("#dashboardSelectedInstanceCurrentPropertyNextStatisticsUpdateValue"),
            nextDailyAchievementCheck: $("#dashboardSelectedInstanceCurrentPropertyNextDailyAchievementCheckValue"),
            nextMilestoneCheck: $("#dashboardSelectedInstanceCurrentPropertyNextMilestoneCheckValue"),
            nextHeavenlyStrike: $("#dashboardSelectedInstanceCurrentPropertyNextHeavenlyStrikeValue"),
            nextDeadlyStrike: $("#dashboardSelectedInstanceCurrentPropertyNextDeadlyStrikeValue"),
            nextHandOfMidas: $("#dashboardSelectedInstanceCurrentPropertyNextHandOfMidasValue"),
            nextFireSword: $("#dashboardSelectedInstanceCurrentPropertyNextFireSwordValue"),
            nextWarCry: $("#dashboardSelectedInstanceCurrentPropertyNextWarCryValue"),
            nextShadowClone: $("#dashboardSelectedInstanceCurrentPropertyNextShadowCloneValue"),
        }
    };

    async function setupSelectedInstanceOptions(data) {
        // Update the available queued data so that we update with the
        // most recent set of information available.
        // We only do this if no data is provided on call.
        panel.data = data || await grabData();

        // The data passed in above is done so in this function to avoid the hiding/showing of
        // the panel unless the update selected instance function is called directly.
        // This happens either through a manual click of a new instance, or on refresh.
        // Real-time updates just update the information (if changed).

        // Begin setting up the values present in our current data instance.
        // Some values can be populated even if an instance is not currently running.
        // Some values require the instance to be running before we populate anything.
        let state = activeInstanceStatus();

        if (state === "stopped") {
            // First, reset all values present within our information tables. They should
            // all be set back to their base state of "------" before we populate anything.
            for (let elements of [panel.baseInformation, panel.lastPrestigeInformation, panel.currentPropertiesInformation]) {
                $.each(elements, function(index, value) {
                    // Remove any data attributes that were present
                    // and set before through information setup.
                    value.removeData();
                    // Remove any hyperlink (href) attributes that were setup
                    // dynamically before through information setup.
                    if (value.is("a")) { value.attr("href", "#"); }
                    // Reset the text for this element back to it's
                    // default "------" value.
                    value.text("------");
                });
            }
            // Let's also destroy and reset any stopwatches or countdowns
            // if they're currently not null.
            for (let timers of [stopwatches, countdowns]) {
                $.each(timers, function(index, value) {
                    // Only removing the timer (destroy), if it's
                    // not already a mull value.
                    if (value !== null) {
                        value.destroy();
                        // Update our base timer to be a null value.
                        timers[index] = null;
                    }
                });
            }
        }

        // Name Value.
        if (panel.data.name && panel.baseInformation.name.text() !== panel.data.name) {
            panel.baseInformation.name.text(panel.data.name);
        }
        // State Value.
        if (panel.data.state && panel.baseInformation.state.text() !== panel.data.state) {
            panel.baseInformation.state.text(panel.data.state);
        }

        if (state === "running" || state === "paused") {
            // Session Value.
            if (panel.data.session && panel.baseInformation.session.text() !== panel.data.session.uuid) {
                panel.baseInformation.session.attr("href", panel.data.session.url).text(panel.data.session.uuid);
            }
            // Started Value (Stopwatch).
            if (panel.data.started.datetime && panel.baseInformation.started.data("datetime") !== panel.data.started.datetime) {
                configureStopwatch("startedStopwatch", panel.data.started, panel.baseInformation.started);
            }
            // Function Value.
            if (panel.data.function && panel.baseInformation.function.text() !== panel.data.function) {
                panel.baseInformation.function.text(panel.data.function);
            }
            // Timestamp Value (Stopwatch).
            if (panel.data.last_prestige && panel.lastPrestigeInformation.timestamp.data("datetime") !== panel.data.last_prestige.timestamp.datetime) {
                configureStopwatch("timestampStopwatch", panel.data.last_prestige.timestamp.datetime, panel.lastPrestigeInformation.timestamp);
            }
            // Stage Value.
            if (panel.data.last_prestige && panel.lastPrestigeInformation.stage.text() !== panel.data.last_prestige.stage) {
                panel.lastPrestigeInformation.stage.text(panel.data.last_prestige.stage);
            }
            // Duration Value.
            if (panel.data.last_prestige && panel.lastPrestigeInformation.duration.text() !== panel.data.last_prestige.duration) {
                panel.lastPrestigeInformation.duration.text(panel.data.last_prestige.duration);
            }
            // Artifact Value.
            if (panel.data.last_prestige && panel.lastPrestigeInformation.artifact.data("pk") !== panel.data.last_prestige.artifact.pk) {
                panel.lastPrestigeInformation.artifact.data("pk", panel.data.last_prestige.artifact.pk).html(`
                    ${formatString(panel.data.last_prestige.artifact.name)}&nbsp;&nbsp;<img height="20" width="20" src="${panel.data.last_prestige.artifact.image}">
                `);
            }
            // Log File Value.
            if (panel.data.log && panel.currentPropertiesInformation.logFile.data("pk") !== panel.data.log.pk) {
                panel.currentPropertiesInformation.logFile.data("pk", panel.data.log.pk).attr("href", panel.data.log.url).text("Link");
            }
            // Configuration Value.
            if (panel.data.configuration && panel.currentPropertiesInformation.configuration.text() !== panel.data.configuration.name) {
                panel.currentPropertiesInformation.configuration.attr("href", panel.data.configuration.url).text(panel.data.configuration.name);
            }
            // Window Value.
            if (panel.data.window && panel.currentPropertiesInformation.window.text() !== panel.data.window.formatted) {
                panel.currentPropertiesInformation.window.text(panel.data.window.formatted);
            }
            // Shortcuts Value.
            if (panel.data.shortcuts !== null && panel.currentPropertiesInformation.shortcuts.data("enabled") !== panel.data.shortcuts) {
                panel.currentPropertiesInformation.shortcuts.data("enabled", panel.data.shortcuts).text(panel.data.shortcuts ? "ENABLED" : "DISABLED");
            }
            // Current Stage Value.
            if (panel.data.current_stage && panel.currentPropertiesInformation.stage.data("stage") !== panel.data.current_stage) {
                panel.currentPropertiesInformation.stage.data("stage", panel.data.current_stage).html(`
                    ${panel.data.current_stage.stage} (${panel.data.current_stage.diff} - ${panel.data.current_stage.percent})
                `);
            }
            // Newest Hero Value.
            if (panel.data.newest_hero && panel.currentPropertiesInformation.newestHero.text() !== panel.data.newest_hero) {
                panel.currentPropertiesInformation.newestHero.text(panel.data.newest_hero);
            }
            // Raid Attack Reset Value (Countdown).
            if (panel.data.next_raid_attack_reset.datetime && panel.currentPropertiesInformation.raidAttackReset.data("datetime") !== panel.data.next_raid_attack_reset.datetime) {
                configureCountdown("raidAttackResetCountdown", panel.data.next_raid_attack_reset, panel.currentPropertiesInformation.raidAttackReset);
            }
            // Next Break Value (Countdown).
            if (panel.data.next_break.datetime && panel.currentPropertiesInformation.nextBreak.data("datetime") !== panel.data.next_break.datetime) {
                configureCountdown("nextBreakCountdown", panel.data.next_break, panel.currentPropertiesInformation.nextBreak);
            }
            // Next Break Resume Value (Countdown).
            if (panel.data.break_resume.datetime && panel.currentPropertiesInformation.nextBreakResume.data("datetime") !== panel.data.break_resume.datetime) {
                configureCountdown("breakResumeCountdown", panel.data.break_resume, panel.currentPropertiesInformation.nextBreakResume);
            }
            // Next Artifact Upgrade Value.
            if (panel.data.next_artifact_upgrade && panel.currentPropertiesInformation.nextArtifactUpgrade.data("key") !== panel.data.next_artifact_upgrade.key) {
                panel.currentPropertiesInformation.nextArtifactUpgrade.data("key", panel.data.next_artifact_upgrade.key).html(`
                    ${formatString(panel.data.next_artifact_upgrade)}&nbsp;&nbsp;<img height="20" width="20" src="${panel.data.next_artifact_upgrade.image}"
                `);
            }
            // Next Master Level Value (Countdown).
            if (panel.data.next_master_level.datetime && panel.currentPropertiesInformation.nextMasterLevel.data("datetime") !== panel.data.next_master_level.datetime) {
                configureCountdown("nextMasterLevelCountdown", panel.data.next_master_level, panel.currentPropertiesInformation.nextMasterLevel);
            }
            // Next Heroes Level Value (Countdown).
            if (panel.data.next_heroes_level.datetime && panel.currentPropertiesInformation.nextHeroesLevel.data("datetime") !== panel.data.next_heroes_level.datetime) {
                configureCountdown("nextHeroesLevelCountdown", panel.data.next_heroes_level, panel.currentPropertiesInformation.nextHeroesLevel);
            }
            // Next Skills Level Value (Countdown).
            if (panel.data.next_skills_level.datetime && panel.currentPropertiesInformation.nextSkillsLevel.data("datetime") !== panel.data.next_skills_level.datetime) {
                configureCountdown("nextSkillsLevelCountdown", panel.data.next_skills_level, panel.currentPropertiesInformation.nextSkillsLevel);
            }
            // Next Skills Activation Value (Countdown).
            if (panel.data.next_skills_activation.datetime && panel.currentPropertiesInformation.nextSkillsActivation.data("datetime") !== panel.data.next_skills_activation.datetime) {
                configureCountdown("nextSkillsActivationCountdown", panel.data.next_skills_activation, panel.currentPropertiesInformation.nextSkillsActivation);
            }
            // Next Miscellaneous Value (Countdown).
            if (panel.data.next_miscellaneous_actions.datetime && panel.currentPropertiesInformation.nextMiscellaneousActions.data("datetime") !== panel.data.next_miscellaneous_actions.datetime) {
                configureCountdown("nextMiscellaneousActionsCountdown", panel.data.next_miscellaneous_actions, panel.currentPropertiesInformation.nextMiscellaneousActions);
            }
            // Next Headgear Swap (Countdown).
            if (panel.data.next_headgear_swap.datetime && panel.currentPropertiesInformation.nextHeadgearSwap.data("datetime") !== panel.data.next_headgear_swap.datetime) {
                configureCountdown("nextHeadgearSwapCountdown", panel.data.next_headgear_swap, panel.currentPropertiesInformation.nextHeadgearSwap);
            }
            // Next Perk Check (Countdown).
            if (panel.data.next_perk_check.datetime && panel.currentPropertiesInformation.nextPerkCheck.data("datetime") !== panel.data.next_perk_check.datetime) {
                configureCountdown("nextPerkCheckCountdown", panel.data.next_perk_check, panel.currentPropertiesInformation.nextPerkCheck);
            }
            // Next Timed Threshold Prestige (Countdown).
            if (panel.data.next_prestige.datetime && panel.currentPropertiesInformation.nextTimedThresholdPrestige.data("datetime") !== panel.data.next_prestige.datetime) {
                configureCountdown("nextPrestigeCountdown", panel.data.next_prestige, panel.currentPropertiesInformation.nextTimedThresholdPrestige);
            }
            // Next Randomized Threshold Prestige (Countdown).
            if (panel.data.next_randomized_prestige.datetime &&  panel.currentPropertiesInformation.nextRandomizedThresholdPrestige.data("datetime") !== panel.data.next_randomized_prestige.datetime) {
                configureCountdown("nextRandomizedPrestigeCountdown", panel.data.next_randomized_prestige, panel.currentPropertiesInformation.nextRandomizedThresholdPrestige);
            }
            // Next Statistics Update (Countdown).
            if (panel.data.next_statistics_update.datetime && panel.currentPropertiesInformation.nextStatisticsUpdate.data("datetime") !== panel.data.next_statistics_update.datetime) {
                configureCountdown("nextStatisticsUpdateCountdown", panel.data.next_statistics_update, panel.currentPropertiesInformation.nextStatisticsUpdate);
            }
            // Next Daily Achievement Check (Countdown).
            if (panel.data.next_daily_achievement_check.datetime && panel.currentPropertiesInformation.nextDailyAchievementCheck.data("datetime") !== panel.data.next_daily_achievement_check.datetime) {
                configureCountdown("nextDailyAchievementCheckCountdown", panel.data.next_daily_achievement_check, panel.currentPropertiesInformation.nextDailyAchievementCheck);
            }
            // Next Milestone Check (Countdown).
            if (panel.data.next_milestone_check.datetime && panel.currentPropertiesInformation.nextMilestoneCheck.data("datetime") !== panel.data.next_milestone_check.datetime) {
                configureCountdown("nextMilestoneCheckCountdown", panel.data.next_milestone_check, panel.currentPropertiesInformation.nextMilestoneCheck);
            }
            // Next Heavenly Strike (Countdown).
            if (panel.data.next_heavenly_strike.datetime && panel.currentPropertiesInformation.nextHeavenlyStrike.data("datetime") !== panel.data.next_heavenly_strike.datetime) {
                configureCountdown("nextHeavenlyStrikeCountdown", panel.data.next_heavenly_strike, panel.currentPropertiesInformation.nextHeavenlyStrike);
            }
            // Next Deadly Strike (Countdown).
            if (panel.data.next_deadly_strike.datetime && panel.currentPropertiesInformation.nextDeadlyStrike.data("datetime") !== panel.data.next_deadly_strike.datetime) {
                configureCountdown("nextDeadlyStrikeCountdown", panel.data.next_deadly_strike, panel.currentPropertiesInformation.nextDeadlyStrike);
            }
            // Next Hand Of Midas (Countdown).
            if (panel.data.next_hand_of_midas.datetime && panel.currentPropertiesInformation.nextHandOfMidas.data("datetime") !== panel.data.next_hand_of_midas.datetime) {
                configureCountdown("nextHandOfMidasCountdown", panel.data.next_hand_of_midas, panel.currentPropertiesInformation.nextHandOfMidas);
            }
            // Next Fire Sword (Countdown).
            if (panel.data.next_fire_sword.datetime && panel.currentPropertiesInformation.nextFireSword.data("datetime") !== panel.data.next_fire_sword.datetime) {
                configureCountdown("nextFireSwordCountdown", panel.data.next_fire_sword, panel.currentPropertiesInformation.nextFireSword);
            }
            // Next War Cry (Countdown).
            if (panel.data.next_war_cry.datetime && panel.currentPropertiesInformation.nextWarCry.data("datetime") !== panel.data.next_war_cry.datetime) {
                configureCountdown("nextWarCryCountdown", panel.data.next_war_cry, panel.currentPropertiesInformation.nextWarCry);
            }
            // Next Shadow Clone (Countdown).
            if (panel.data.next_shadow_clone.datetime && panel.currentPropertiesInformation.nextShadowClone.data("datetime") !== panel.data.next_shadow_clone.datetime) {
                configureCountdown("nextShadowCloneCountdown", panel.data.next_shadow_clone, panel.currentPropertiesInformation.nextShadowClone);
            }
        }
    }

    async function setupSelectedInstanceHandlers() {
        // The selected instance should be modified and updated when the active
        // instance is changed manually by a user.
        panel.baseElements.instancesTable.on("click", ".instance-select", updateSelectedInstance);
    }

    function configureCountdown(countdown, data, element) {
        let _countdown = countdowns[countdown];

        // Ensure that the element also has the proper data attribute
        // set. Configuration only happens based on whether or not this is set.
        element.data("datetime", data.datetime);

        // If the countdown is already set and running, we need to make sure
        // we destroy it appropriately and set it back to a null state.
        if (_countdown !== null) {
            // The countdown original date will be different if a new countdown
            // should be generated and built.
            if (_countdown.originalDateReference !== date.datetime) {
                _countdown.destroy();
                // Build out a brand new countdown now that the old one has been
                // destroyed properly, setting to null then constructing.
                countdowns[countdown] = null;
                countdowns[countdown] = new Countdown(data.datetime, data.formatted, element);
            }
        }
        // Countdown is already in a null state, go ahead and generate a
        // new one like we normally would.
        else {
            countdowns[countdown] = new Countdown(data.datetime, data.formatted, element);
        }
    }

    function configureStopwatch(stopwatch, data, element) {
        let _stopwatch = stopwatches[stopwatch];

        // Ensure that the element also has the proper data attribute
        // set. Configuration only happens based on whether or not this is set.
        element.data("datetime", data.datetime);

        // If the stopwatch is already set and running, we need to make sure
        // we destroy it appropriately and set it back to a null state.
        if (_stopwatch !== null) {
            // The stopwatch original date will be different if a new stopwatch
            // should be generated and built.
            if (_stopwatch.originalDateReference !== data.datetime) {
                _stopwatch.destroy();
                // Build out a brand new stopwatch now that the old one has been
                // destroyed properly, setting to null then constructing.
                stopwatches[stopwatch] = null;
                stopwatches[stopwatch] = new Stopwatch(data.datetime, data.formatted, element);
            }
        }
        // Stopwatch is already in a null state, go ahead and generate a
        // new one like we normally would.
        else {
            stopwatches[stopwatch] = new Stopwatch(data.datetime, data.formatted, element);
        }
    }

    async function updateSelectedInstance() {
        // Fading out the content of the panel while we handle updating
        // and setting all proper values.
        hidePanel(panel.baseElements.content, panel.baseElements.loader, async function() {
            // Once the data is completely up-to date, we can run through our
            // base selected instance options configuration to change values.
            await setupSelectedInstanceOptions();

            // Once all options are setup, we can go ahead and also display
            // our panel again.
            showPanel(panel.baseElements.content, panel.baseElements.loader);
        });
    }

    function initializeSelectedInstancePanel() {
        // Run our base setup function to make sure all data is displayed and setup
        // for the selected instance.
        setupSelectedInstanceOptions();

        // Display the panel and hide our loader once the options
        // have been setup and configured successfully.
        showPanel(panel.baseElements.content, panel.baseElements.loader);
    }

    // Begin functionality here, setting up our panel and initializing it once.
    // Additional updates are handled through update functions or instance selection
    // event handlers.
    initializeSelectedInstancePanel();
    // Setup any of the listeners or events built
    // out and used by the selected instance panel.
    await setupSelectedInstanceHandlers();

    // Ensure the selected instance panel has it's update function
    // included and executable through our global update functions.
    updateFunctions["selectedInstance"] = setupSelectedInstanceOptions;
});