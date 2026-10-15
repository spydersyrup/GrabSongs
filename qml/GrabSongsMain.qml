import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import QtQuick.Effects
import "ThemeColors.js" as ThemeColors

ApplicationWindow {
    id: window
    visible: true
    width: Screen.desktopAvailableWidth > 100 ? Math.min(1240, Screen.desktopAvailableWidth) : 1240
    height: Screen.desktopAvailableHeight > 100 ? Math.min(760, Screen.desktopAvailableHeight) : 760
    x: Screen.desktopAvailableWidth > width ? Math.round((Screen.desktopAvailableWidth - width) / 2) : 0
    y: Screen.desktopAvailableHeight > height ? Math.round((Screen.desktopAvailableHeight - height) / 2) : 0
    minimumWidth: 780
    minimumHeight: 520
    title: "GrabSongs"
    color: surfaceBase
    flags: Qt.Window | Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint

    // -------------------------------------------------------------
    // HUMAN-TONED PALETTE: Natural Warmth on Shades of Soot Black
    // Zero glow, zero artificial neon, matte paper, linen & clay craft
    // -------------------------------------------------------------
    property string accentName: "terracotta"
    property string customAccentColor: "#D95D39"
    readonly property var accentColorMap: ({
        "terracotta": { base: "#D95D39", hover: "#E86945", text: "#E86945", darkText: "#FFFFFF" },// Warm Terracotta / Burnt Coral
        "tangerine":  { base: "#F05423", hover: "#FA6232", text: "#FA6232", darkText: "#FFFFFF" },// Industrial Signal Orange
        "pine":       { base: "#3D7A5A", hover: "#4B8F6B", text: "#5EA67E", darkText: "#FFFFFF" },// Nordic Forest / Botanical Pine
        "ochre":      { base: "#C88A2E", hover: "#D99B3D", text: "#E5A749", darkText: "#141312" },// Warm Ochre / Earthy Dijon
        "linen":      { base: "#E4DFD7", hover: "#F2EDE6", text: "#E4DFD7", darkText: "#161514" } // Warm Unbleached Linen / Bone
    })

    property color recordRed: accentName === "custom"
        ? Qt.color(customAccentColor)
        : (accentColorMap[accentName] || accentColorMap["terracotta"]).base
    property color recordRedHover: accentName === "custom"
        ? Qt.lighter(Qt.color(customAccentColor), 1.15)
        : (accentColorMap[accentName] || accentColorMap["terracotta"]).hover
    property color accentText: accentName === "custom"
        ? Qt.color(customAccentColor)
        : (accentColorMap[accentName] || accentColorMap["terracotta"]).text
    property color accentButtonText: (accentColorMap[accentName] || accentColorMap["terracotta"]).darkText

    property color brandAccent: recordRed
    property color brandAccentHover: recordRedHover
    property color brandAccentText: accentText

    onAccentNameChanged: {
        const item = accentColorMap[accentName] || accentColorMap["terracotta"]
        recordRed = (accentName === "custom" ? Qt.color(customAccentColor) : item.base)
        recordRedHover = (accentName === "custom" ? Qt.lighter(Qt.color(customAccentColor), 1.15) : item.hover)
        accentText = (accentName === "custom" ? Qt.color(customAccentColor) : item.text)
        accentButtonText = (accentName === "custom" ? "#FFFFFF" : item.darkText)
        brandAccent = recordRed
        brandAccentHover = recordRedHover
        brandAccentText = accentText
    }

    // Rich soot & obsidian dark palette (Clean, deep, non-muddy, human warmth)
    readonly property color surfaceDeep: "#090909"
    readonly property color surfaceBase: "#0E0E0E"
    readonly property color surfaceSidebar: "#131313"
    readonly property color surfaceDock: "#151515"
    readonly property color surfaceCard: "#181818"
    readonly property color surfaceInput: "#141414"
    readonly property color surfaceCardHover: "#1F1F1F"
    readonly property color surfaceElevated: "#242424"
    readonly property color surfaceTag: "#1B1B1B"
    readonly property color surfaceSelected: "#242424"

    readonly property color silver: "#E5E2DC"
    readonly property color silverDim: "#8C867E"
    readonly property color textPrimary: "#F4F1EB"
    readonly property color textSecondary: "#9E978E"
    readonly property color textMuted: "#938A80"
    readonly property color danger: "#D65A5A"
    readonly property color success: "#5EA67A"

    readonly property color borderSubtle: "#222222"
    readonly property color borderVariant: "#2B2B2B"
    readonly property color borderCard: borderVariant

    // Typography
    readonly property string displayFont: (typeof displayFontFamily !== "undefined" && displayFontFamily) ? displayFontFamily : "IBM Plex Sans"
    readonly property string bodyFont: (typeof bodyFontFamily !== "undefined" && bodyFontFamily) ? bodyFontFamily : "IBM Plex Sans"
    readonly property string monoFont: (typeof monoFontFamily !== "undefined" && monoFontFamily) ? monoFontFamily : "IBM Plex Mono"

    // App State matching Main.qml
    property string page: "explore" // "explore", "queue", "library", "settings"
    property bool sidebarCollapsed: false
    property bool nowPlayingOpen: false
    property bool accessHintsVisible: false
    property real albumArtRadius: 8

    // Downloader backend
    property var downloaderBridge: typeof downloader !== "undefined" ? downloader : null
    property string activePlatform: "all" // "all", "spotify", "apple", "youtube", "deezer"
    property var searchResults: []
    property var resolvedCollection: null
    property var activeJobs: []
    property var downloadedFiles: []
    property bool isSearching: downloaderBridge ? downloaderBridge.isSearching : false

    onPageChanged: {
        if (page === "library" && downloaderBridge) {
            window.downloadedFiles = downloaderBridge.getDownloadedFiles()
        }
    }
    property string searchError: ""
    property string libraryViewMode: "grid" // "grid" or "list"

    // Poll the download queue. The library is deliberately not polled here:
    // getDownloadedFiles() walks the whole directory and parses tags, which is
    // far too expensive to run every second while the library page is open.
    // It refreshes from onJobFinished / onDownloadedFilesChanged instead, and
    // onPageChanged covers entering the page with files added outside the app.
    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
            if (downloaderBridge) {
                window.activeJobs = downloaderBridge.getActiveJobs()
            }
        }
    }

    Connections {
        target: downloaderBridge
        function onSearchStarted() {
            window.isSearching = true
            window.searchError = ""
            window.searchResults = []
            window.resolvedCollection = null
        }
        function onSearchFinished(tracks, collection) {
            window.isSearching = false
            window.searchResults = tracks
            window.resolvedCollection = collection || null
        }
        function onSearchFailed(err) {
            window.isSearching = false
            window.searchError = err
        }
        function onJobProgress(job_id, percent, speed, eta) {
            if (downloaderBridge && window.page === "queue") {
                window.activeJobs = downloaderBridge.getActiveJobs()
            }
        }
        function onJobFinished(job_id, success, msg) {
            if (downloaderBridge) {
                window.activeJobs = downloaderBridge.getActiveJobs()
                window.downloadedFiles = downloaderBridge.getDownloadedFiles()
            }
        }
        function onDownloadedFilesChanged() {
            if (downloaderBridge) {
                window.downloadedFiles = downloaderBridge.getDownloadedFiles()
            }
        }
        function onConfigChanged() {
            if (downloaderBridge && downloaderBridge.accentName) {
                window.accentName = downloaderBridge.accentName
            }
        }
    }

    Component.onCompleted: {
        if (downloaderBridge) {
            window.activeJobs = downloaderBridge.getActiveJobs()
            window.downloadedFiles = downloaderBridge.getDownloadedFiles()
            if (downloaderBridge.accentName) {
                window.accentName = downloaderBridge.accentName
            }
        }
    }

    function triggerSearch(textToSearch) {
        const q = (textToSearch !== undefined ? textToSearch : pageSearchInput.text).trim()
        if (!q || !downloaderBridge) return
        downloaderBridge.search(q, window.activePlatform)
    }

    function toggleMaximize() {
        if (window.visibility === Window.Maximized) {
            window.showNormal()
        } else {
            window.showMaximized()
        }
    }

    function formatTime(ms) {
        if (!ms || ms < 0) return "0:00"
        const totalSec = Math.floor(ms / 1000)
        const mins = Math.floor(totalSec / 60)
        const secs = totalSec % 60
        return mins + ":" + (secs < 10 ? "0" : "") + secs
    }

    function formatServiceName(s) {
        if (!s) return ""
        const lower = s.toLowerCase()
        if (lower === "apple_music" || lower === "apple") return "Apple Music"
        if (lower === "spotify") return "Spotify"
        if (lower === "youtube") return "YouTube"
        if (lower === "deezer") return "Deezer"
        return s.replace(/_/g, " ")
    }

    Rectangle {
        id: customTitleBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 42
        color: surfaceBase
        z: 100

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton
            onPressed: window.startSystemMove()
            onDoubleClicked: toggleMaximize()
        }

        // Left Sidebar Header Compartment (Matches sidebarPanel width and surfaceSidebar background)
        Rectangle {
            id: sidebarHeaderSection
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            width: sidebarPanel.width
            color: surfaceSidebar
            clip: true

            // Continuous vertical divider connecting with sidebarPanel's right border
            Rectangle {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.right: parent.right
                width: 1
                color: borderSubtle
            }

            // Typographic application title (aligned with sidebar content padding)
            Label {
                anchors.left: parent.left
                anchors.leftMargin: window.sidebarCollapsed ? 18 : 24
                anchors.verticalCenter: parent.verticalCenter
                text: window.sidebarCollapsed ? "GS" : "GrabSongs"
                color: textPrimary
                font.family: displayFont
                font.pixelSize: 15
                font.weight: Font.Bold
                font.letterSpacing: -0.2
            }
        }

        // Workspace Titlebar Drag Area
        Item {
            anchors.left: sidebarHeaderSection.right
            anchors.right: windowControlsRow.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
        }

        // Window Controls (minBtn, maxBtn, closeBtn)
        Row {
            id: windowControlsRow
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            // Minimize
            Rectangle {
                id: minBtn
                width: 44
                height: 42
                color: minBtnMouse.containsMouse ? surfaceElevated : "transparent"

                LucideIcon {
                    anchors.centerIn: parent
                    width: 14
                    height: 14
                    icon: "minus"
                    color: minBtnMouse.containsMouse ? textPrimary : silverDim
                }

                MouseArea {
                    id: minBtnMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.ArrowCursor
                    onClicked: window.showMinimized()
                }
            }

            // Maximize / Restore
            Rectangle {
                id: maxBtn
                width: 44
                height: 42
                color: maxBtnMouse.containsMouse ? surfaceElevated : "transparent"

                LucideIcon {
                    anchors.centerIn: parent
                    width: 12
                    height: 12
                    icon: "maximize-2"
                    color: maxBtnMouse.containsMouse ? textPrimary : silverDim
                }

                MouseArea {
                    id: maxBtnMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.ArrowCursor
                    onClicked: toggleMaximize()
                }
            }

            // Close
            Rectangle {
                id: closeBtn
                width: 44
                height: 42
                color: closeBtnMouse.containsMouse ? recordRed : "transparent"

                LucideIcon {
                    anchors.centerIn: parent
                    width: 14
                    height: 14
                    icon: "x"
                    color: closeBtnMouse.containsMouse ? "#FFFFFF" : silverDim
                }

                MouseArea {
                    id: closeBtnMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.ArrowCursor
                    onClicked: window.close()
                }
            }
        }
    }

    Item {
        id: appArea
        anchors.top: customTitleBar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        Item {
            id: mainBodyArea
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: miniPlayerDock.top

            Rectangle {
                id: sidebarPanel
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.bottom: parent.bottom
                width: window.sidebarCollapsed ? 64 : 200
                color: surfaceSidebar
                clip: true

                Behavior on width {
                    NumberAnimation { duration: 220; easing.type: Easing.OutCubic }
                }

                // Subtle right border
                Rectangle {
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    width: 1
                    color: borderSubtle
                }

                // Top Navigation Items (NavItem from main app)
                Column {
                    id: navTopColumn
                    anchors.top: parent.top
                    anchors.topMargin: 10
                    anchors.left: parent.left
                    anchors.right: parent.right
                    spacing: 4

                    NavItem {
                        appWindow: window
                        sidebarWidth: sidebarPanel.width
                        sidebarCollapsed: window.sidebarCollapsed
                        destination: "explore"
                        iconName: "search"
                        label: "Search"
                    }

                    NavItem {
                        appWindow: window
                        sidebarWidth: sidebarPanel.width
                        sidebarCollapsed: window.sidebarCollapsed
                        destination: "queue"
                        iconName: "arrow-down"
                        label: "Downloads"
                    }

                    NavItem {
                        appWindow: window
                        sidebarWidth: sidebarPanel.width
                        sidebarCollapsed: window.sidebarCollapsed
                        destination: "library"
                        iconName: "music"
                        label: "Library"
                    }
                }

                // Bottom Navigation Items (Folder action, Settings, Collapse Toggle)
                Column {
                    id: navBottomColumn
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 10
                    anchors.left: parent.left
                    anchors.right: parent.right
                    spacing: 4

                    Rectangle {
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: window.sidebarCollapsed ? 28 : 170
                        height: 1
                        color: borderSubtle
                        opacity: 0.6
                        Behavior on width { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
                    }

                    Item { width: 1; height: 2 }

                    // Open Music Folder action
                    Item {
                        width: sidebarPanel.width
                        height: 40

                        Rectangle {
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.verticalCenter
                            width: window.sidebarCollapsed ? 44 : 180
                            height: 40
                            radius: 8
                            color: fldMouse.containsMouse ? surfaceCardHover : "transparent"

                            Behavior on color { ColorAnimation { duration: 120 } }

                            LucideIcon {
                                anchors.left: parent.left
                                anchors.leftMargin: window.sidebarCollapsed ? 12 : 14
                                anchors.verticalCenter: parent.verticalCenter
                                width: 20
                                height: 20
                                icon: "folder"
                                color: fldMouse.containsMouse ? textPrimary : silverDim
                            }

                            Label {
                                anchors.left: parent.left
                                anchors.leftMargin: 46
                                anchors.verticalCenter: parent.verticalCenter
                                text: "Open Music Folder"
                                color: fldMouse.containsMouse ? textPrimary : textSecondary
                                font.family: displayFont
                                font.pixelSize: 13
                                visible: !window.sidebarCollapsed && opacity > 0.01
                                opacity: Math.max(0.0, Math.min(1.0, (sidebarPanel.width - 90) / (200 - 90)))
                            }

                            MouseArea {
                                id: fldMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: if (downloaderBridge) downloaderBridge.openDownloadFolder()
                            }
                        }
                    }

                    NavItem {
                        appWindow: window
                        sidebarWidth: sidebarPanel.width
                        sidebarCollapsed: window.sidebarCollapsed
                        destination: "settings"
                        iconName: "settings"
                        label: "Settings"
                    }

                    // Collapse Toggle Item (Exact match to Main.qml)
                    Item {
                        id: bottomToggleItem
                        width: sidebarPanel.width
                        height: 40

                        Rectangle {
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.verticalCenter
                            width: window.sidebarCollapsed ? 44 : 180
                            height: 40
                            radius: 8
                            color: toggleMouse.containsMouse ? surfaceCardHover : "transparent"

                            Behavior on color { ColorAnimation { duration: 120 } }

                            LucideIcon {
                                anchors.left: parent.left
                                anchors.leftMargin: window.sidebarCollapsed ? 12 : 14
                                anchors.verticalCenter: parent.verticalCenter
                                width: 20
                                height: 20
                                icon: "panel-left"
                                color: toggleMouse.containsMouse ? textPrimary : silverDim

                                Behavior on anchors.leftMargin { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
                                Behavior on color { ColorAnimation { duration: 120 } }
                            }

                            Label {
                                anchors.left: parent.left
                                anchors.leftMargin: 46
                                anchors.verticalCenter: parent.verticalCenter
                                text: "Collapse"
                                color: toggleMouse.containsMouse ? textPrimary : textSecondary
                                font.family: displayFont
                                font.pixelSize: 13
                                visible: !window.sidebarCollapsed && opacity > 0.01
                                opacity: Math.max(0.0, Math.min(1.0, (sidebarPanel.width - 90) / (200 - 90)))

                                Behavior on color { ColorAnimation { duration: 120 } }
                            }
                        }

                        MouseArea {
                            id: toggleMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: window.sidebarCollapsed = !window.sidebarCollapsed
                        }
                    }
                }
            }

            Rectangle {
                id: contentPanel
                anchors.top: parent.top
                anchors.left: sidebarPanel.right
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                color: surfaceBase

                StackLayout {
                    anchors.fill: parent
                    currentIndex: {
                        if (window.page === "explore") return 0
                        if (window.page === "queue") return 1
                        if (window.page === "library") return 2
                        if (window.page === "settings") return 3
                        return 0
                    }

                    // =========================================================
                    // PAGE 1: SEARCH & DOWNLOAD (EXPLORE)
                    // =========================================================
                    Item {
                        id: explorePageItem

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 28
                            anchors.rightMargin: 28
                            anchors.topMargin: 12
                            anchors.bottomMargin: 16
                            spacing: 12

                            // -------------------------------------------------
                            // Search Box (Quiet, sleek 40px desktop input)
                            // -------------------------------------------------
                            Rectangle {
                                id: pageSearchBox
                                Layout.fillWidth: true
                                Layout.preferredHeight: 40
                                radius: 8
                                color: pageSearchInput.activeFocus ? surfaceElevated : surfaceInput
                                border.width: 1
                                border.color: pageSearchInput.activeFocus ? borderVariant : borderSubtle

                                Behavior on color { ColorAnimation { duration: 120 } }
                                Behavior on border.color { ColorAnimation { duration: 120 } }

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 14
                                    anchors.rightMargin: 10
                                    spacing: 10

                                    LucideIcon {
                                        Layout.preferredWidth: 16
                                        Layout.preferredHeight: 16
                                        Layout.alignment: Qt.AlignVCenter
                                        icon: "search"
                                        color: pageSearchInput.activeFocus ? textPrimary : textSecondary
                                        Behavior on color { ColorAnimation { duration: 120 } }
                                    }

                                    TextInput {
                                        id: pageSearchInput
                                        Layout.fillWidth: true
                                        Layout.alignment: Qt.AlignVCenter
                                        verticalAlignment: TextInput.AlignVCenter
                                        color: textPrimary
                                        font.family: bodyFont
                                        font.pixelSize: 13
                                        selectByMouse: true
                                        onAccepted: window.triggerSearch()

                                        Text {
                                            anchors.fill: parent
                                            visible: !pageSearchInput.text && !pageSearchInput.activeFocus
                                            text: "Search songs, albums, artists, or paste a link..."
                                            color: textMuted
                                            font.family: bodyFont
                                            font.pixelSize: 13
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                    }

                                    // Quick Paste Button when search is empty
                                    PressDepthIconButton {
                                        visible: pageSearchInput.text.length === 0
                                        Layout.preferredWidth: 28
                                        Layout.preferredHeight: 28
                                        Layout.alignment: Qt.AlignVCenter
                                        boxSize: 28
                                        iconSize: 14
                                        cornerRadius: 6
                                        backgroundColor: "transparent"
                                        borderColor: "transparent"
                                        hoverBackgroundColor: surfaceCardHover
                                        hoverBorderColor: "transparent"
                                        iconName: "clipboard"
                                        tint: textSecondary
                                        hoverTint: textPrimary
                                        tooltipText: "Paste from clipboard (Ctrl+V)"
                                        onClicked: {
                                            if (downloaderBridge) {
                                                const clip = downloaderBridge.getClipboardText().trim()
                                                if (clip) {
                                                    pageSearchInput.text = clip
                                                    window.triggerSearch(clip)
                                                }
                                            }
                                        }
                                    }

                                    // Clear Button when text entered
                                    PressDepthIconButton {
                                        visible: pageSearchInput.text.length > 0 || window.searchResults.length > 0
                                        Layout.preferredWidth: 28
                                        Layout.preferredHeight: 28
                                        Layout.alignment: Qt.AlignVCenter
                                        boxSize: 28
                                        iconSize: 14
                                        cornerRadius: 6
                                        backgroundColor: "transparent"
                                        borderColor: "transparent"
                                        hoverBackgroundColor: surfaceCardHover
                                        hoverBorderColor: "transparent"
                                        iconName: "x"
                                        tint: textSecondary
                                        hoverTint: textPrimary
                                        tooltipText: "Clear"
                                        onClicked: {
                                            pageSearchInput.text = ""
                                            window.searchResults = []
                                            window.resolvedCollection = null
                                            window.searchError = ""
                                            pageSearchInput.forceActiveFocus()
                                        }
                                    }
                                }
                            }

                            // -------------------------------------------------
                            // Source Filter Tabs Row
                            // -------------------------------------------------
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 6

                                Repeater {
                                    model: [
                                        { id: "all", label: "All Sources" },
                                        { id: "spotify", label: "Spotify" },
                                        { id: "apple", label: "Apple Music" },
                                        { id: "youtube", label: "YouTube" },
                                        { id: "deezer", label: "Deezer" }
                                    ]

                                    delegate: Rectangle {
                                        required property var modelData
                                        readonly property bool isSelected: window.activePlatform === modelData.id
                                        Layout.preferredWidth: tabLabel.implicitWidth + 20
                                        Layout.preferredHeight: 28
                                        Layout.alignment: Qt.AlignVCenter
                                        radius: 6
                                        color: isSelected ? surfaceElevated : (tabMouse.containsMouse ? surfaceCardHover : "transparent")
                                        border.width: isSelected ? 1 : 0
                                        border.color: isSelected ? borderVariant : "transparent"

                                        Behavior on color { ColorAnimation { duration: 100 } }

                                        Label {
                                            id: tabLabel
                                            anchors.centerIn: parent
                                            text: modelData.label
                                            color: isSelected ? textPrimary : (tabMouse.containsMouse ? textPrimary : textSecondary)
                                            font.family: bodyFont
                                            font.pixelSize: 12
                                            font.weight: isSelected ? Font.DemiBold : Font.Normal
                                        }

                                        MouseArea {
                                            id: tabMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                window.activePlatform = modelData.id
                                                if (pageSearchInput.text.trim()) window.triggerSearch()
                                            }
                                        }
                                    }
                                }

                                Item { Layout.fillWidth: true }

                                // Audio Format Indicator (clean, quiet, no decorative status dots)
                                Rectangle {
                                    Layout.preferredHeight: 26
                                    Layout.preferredWidth: fmtBadgeLabel.implicitWidth + 16
                                    Layout.alignment: Qt.AlignVCenter
                                    radius: 6
                                    color: surfaceTag
                                    border.width: 1
                                    border.color: borderSubtle

                                    Label {
                                        id: fmtBadgeLabel
                                        anchors.centerIn: parent
                                        text: (downloaderBridge ? downloaderBridge.audioQuality + " kbps " + downloaderBridge.audioFormat.toUpperCase() : "320 kbps MP3")
                                        color: textSecondary
                                        font.family: bodyFont
                                        font.pixelSize: 11
                                        font.weight: Font.Normal
                                    }
                                }

                                // Batch Download All Button (Only shown when no collection banner is showing)
                                SettingButton {
                                    visible: window.searchResults.length > 1 && (!window.resolvedCollection || !window.resolvedCollection.title)
                                    Layout.alignment: Qt.AlignVCenter
                                    text: "Download All (" + window.searchResults.length + ")"
                                    iconName: "arrow-down"
                                    primary: true
                                    onClicked: {
                                        if (downloaderBridge && window.searchResults.length > 0) {
                                            downloaderBridge.downloadAll(window.searchResults)
                                            window.page = "queue"
                                        }
                                    }
                                }
                            }

                            // -------------------------------------------------
                            // Main Content Area
                            // -------------------------------------------------
                            Item {
                                Layout.fillWidth: true
                                Layout.fillHeight: true

                                // EMPTY STATE: Quiet, human, dignified
                                ColumnLayout {
                                    visible: !window.isSearching && window.searchResults.length === 0 && !window.searchError
                                    anchors.centerIn: parent
                                    spacing: 12
                                    width: Math.min(parent.width - 64, 420)

                                    LucideIcon {
                                        Layout.alignment: Qt.AlignHCenter
                                        Layout.preferredWidth: 38
                                        Layout.preferredHeight: 38
                                        icon: "music"
                                        color: textSecondary
                                    }

                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "Search or Paste a Link"
                                        font.family: displayFont
                                        font.pixelSize: 16
                                        font.weight: Font.DemiBold
                                        color: textPrimary
                                    }

                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        Layout.fillWidth: true
                                        text: "Find tracks, albums, or playlists across Spotify, Apple Music, YouTube, and Deezer."
                                        font.family: bodyFont
                                        font.pixelSize: 13
                                        color: textSecondary
                                        horizontalAlignment: Text.AlignHCenter
                                        wrapMode: Text.WordWrap
                                    }
                                }

                                // LOADING STATE
                                ColumnLayout {
                                    visible: window.isSearching
                                    anchors.centerIn: parent
                                    spacing: 14

                                    BusyIndicator {
                                        Layout.alignment: Qt.AlignHCenter
                                        running: window.isSearching
                                    }

                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "Resolving metadata & scraping audio streams..."
                                        font.family: bodyFont
                                        font.pixelSize: 13
                                        font.weight: Font.DemiBold
                                        color: textPrimary
                                    }

                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "Querying Spotify, Apple Music, Deezer, and YouTube providers"
                                        font.family: bodyFont
                                        font.pixelSize: 12
                                        color: textSecondary
                                    }
                                }

                                // ERROR STATE
                                ColumnLayout {
                                    visible: !window.isSearching && window.searchError.length > 0
                                    anchors.centerIn: parent
                                    spacing: 12
                                    width: Math.min(parent.width - 40, 480)

                                    LucideIcon {
                                        Layout.alignment: Qt.AlignHCenter
                                        Layout.preferredWidth: 32
                                        Layout.preferredHeight: 32
                                        icon: "info"
                                        color: danger
                                    }

                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "Unable to Resolve Link"
                                        font.family: displayFont
                                        font.pixelSize: 16
                                        font.weight: Font.Bold
                                        color: textPrimary
                                    }

                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        Layout.fillWidth: true
                                        text: window.searchError
                                        font.family: bodyFont
                                        font.pixelSize: 12
                                        color: textSecondary
                                        horizontalAlignment: Text.AlignHCenter
                                        wrapMode: Text.WordWrap
                                    }
                                }

                                // RESULTS WORKSPACE
                                ColumnLayout {
                                    visible: !window.isSearching && window.searchResults.length > 0
                                    anchors.fill: parent
                                    spacing: 10

                                    // Resolved Collection Header (Album / Playlist Banner)
                                    Rectangle {
                                        visible: !!(window.resolvedCollection && window.resolvedCollection.title)
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 84
                                        radius: 10
                                        color: surfaceCard
                                        border.width: 1
                                        border.color: borderSubtle

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: 14
                                            spacing: 16

                                            Rectangle {
                                                Layout.preferredWidth: 56
                                                Layout.preferredHeight: 56
                                                Layout.alignment: Qt.AlignVCenter
                                                radius: 8
                                                clip: true
                                                color: surfaceElevated
                                                border.width: 1
                                                border.color: borderSubtle

                                                LucideIcon {
                                                    anchors.centerIn: parent
                                                    width: 22
                                                    height: 22
                                                    icon: "disc"
                                                    color: textMuted
                                                    visible: !collImg.visible || collImg.status !== Image.Ready
                                                }

                                                Image {
                                                    id: collImg
                                                    anchors.fill: parent
                                                    source: (window.resolvedCollection && window.resolvedCollection.cover_url) ? window.resolvedCollection.cover_url : ""
                                                    fillMode: Image.PreserveAspectCrop
                                                    visible: status === Image.Ready && source.toString().length > 0
                                                }
                                            }

                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                Layout.alignment: Qt.AlignVCenter
                                                spacing: 3

                                                Label {
                                                    text: window.resolvedCollection ? window.resolvedCollection.title : ""
                                                    font.family: displayFont
                                                    font.pixelSize: 17
                                                    font.weight: Font.Bold
                                                    color: textPrimary
                                                    elide: Text.ElideRight
                                                }

                                                Label {
                                                    text: {
                                                        if (!window.resolvedCollection) return ""
                                                        var parts = []
                                                        if (window.resolvedCollection.artist) parts.push(window.resolvedCollection.artist)
                                                        if (window.resolvedCollection.count) parts.push(window.resolvedCollection.count + " tracks")
                                                        if (window.resolvedCollection.service) {
                                                            parts.push(window.formatServiceName(window.resolvedCollection.service))
                                                        }
                                                        return parts.join(" • ")
                                                    }
                                                    font.family: bodyFont
                                                    font.pixelSize: 12
                                                    color: textSecondary
                                                    elide: Text.ElideRight
                                                }
                                            }

                                            SettingButton {
                                                Layout.alignment: Qt.AlignVCenter
                                                text: "Download All Tracks"
                                                iconName: "arrow-down"
                                                primary: true
                                                onClicked: {
                                                    if (downloaderBridge && window.searchResults.length > 0) {
                                                        downloaderBridge.downloadAll(window.searchResults)
                                                        window.page = "queue"
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    // Table Header
                                    Rectangle {
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 28
                                        color: "transparent"

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.leftMargin: 16
                                            anchors.rightMargin: 16
                                            spacing: 12

                                            Label {
                                                Layout.preferredWidth: 28
                                                Layout.alignment: Qt.AlignVCenter
                                                text: "#"
                                                font.family: bodyFont
                                                font.pixelSize: 11
                                                font.weight: Font.DemiBold
                                                color: silverDim
                                                horizontalAlignment: Text.AlignRight
                                            }

                                            Item {
                                                Layout.preferredWidth: 38
                                                Layout.alignment: Qt.AlignVCenter
                                            }

                                            Label {
                                                Layout.fillWidth: true
                                                Layout.alignment: Qt.AlignVCenter
                                                text: "TITLE"
                                                font.family: bodyFont
                                                font.pixelSize: 11
                                                font.weight: Font.DemiBold
                                                color: silverDim
                                            }

                                            Label {
                                                Layout.preferredWidth: 180
                                                Layout.alignment: Qt.AlignVCenter
                                                text: "ALBUM"
                                                font.family: bodyFont
                                                font.pixelSize: 11
                                                font.weight: Font.DemiBold
                                                color: silverDim
                                            }

                                            Label {
                                                Layout.preferredWidth: 80
                                                Layout.alignment: Qt.AlignVCenter
                                                text: "SOURCE"
                                                font.family: bodyFont
                                                font.pixelSize: 11
                                                font.weight: Font.DemiBold
                                                color: silverDim
                                                horizontalAlignment: Text.AlignHCenter
                                            }

                                            Label {
                                                Layout.preferredWidth: 54
                                                Layout.alignment: Qt.AlignVCenter
                                                text: "DURATION"
                                                font.family: bodyFont
                                                font.pixelSize: 11
                                                font.weight: Font.DemiBold
                                                color: silverDim
                                                horizontalAlignment: Text.AlignRight
                                            }

                                            Label {
                                                Layout.preferredWidth: 68
                                                Layout.alignment: Qt.AlignVCenter
                                                text: "ACTIONS"
                                                font.family: bodyFont
                                                font.pixelSize: 11
                                                font.weight: Font.DemiBold
                                                color: silverDim
                                                horizontalAlignment: Text.AlignHCenter
                                            }
                                        }

                                        // Baseline hairline
                                        Rectangle {
                                            anchors.bottom: parent.bottom
                                            anchors.left: parent.left
                                            anchors.leftMargin: 16
                                            anchors.right: parent.right
                                            anchors.rightMargin: 16
                                            height: 1
                                            color: borderSubtle
                                            opacity: 0.6
                                        }
                                    }

                                    // Results List
                                    ListView {
                                        id: resultsList
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        clip: true
                                        spacing: 4
                                        model: window.searchResults
                                        boundsBehavior: Flickable.StopAtBounds

                                        delegate: Rectangle {
                                            required property var modelData
                                            required property int index
                                            width: resultsList.width
                                            height: 52
                                            radius: 8
                                            color: rowMouse.containsMouse ? surfaceElevated : (index % 2 === 1 ? Qt.rgba(255, 255, 255, 0.015) : "transparent")
                                            border.width: rowMouse.containsMouse ? 1 : 0
                                            border.color: borderSubtle

                                            Behavior on color { ColorAnimation { duration: 100 } }

                                            RowLayout {
                                                anchors.fill: parent
                                                anchors.leftMargin: 16
                                                anchors.rightMargin: 16
                                                spacing: 12

                                                // Index number
                                                Label {
                                                    Layout.preferredWidth: 28
                                                    text: String(index + 1)
                                                    font.family: bodyFont
                                                    font.pixelSize: 12
                                                    color: silverDim
                                                    horizontalAlignment: Text.AlignRight
                                                    Layout.alignment: Qt.AlignVCenter
                                                }

                                                // Artwork thumbnail with fallback icon
                                                Rectangle {
                                                    Layout.preferredWidth: 38
                                                    Layout.preferredHeight: 38
                                                    radius: 6
                                                    clip: true
                                                    color: surfaceElevated
                                                    border.width: 1
                                                    border.color: borderSubtle
                                                    Layout.alignment: Qt.AlignVCenter

                                                    LucideIcon {
                                                        anchors.centerIn: parent
                                                        width: 16
                                                        height: 16
                                                        icon: "music"
                                                        color: textMuted
                                                        visible: !rowArtImg.visible || rowArtImg.status !== Image.Ready
                                                    }

                                                    Image {
                                                        id: rowArtImg
                                                        anchors.fill: parent
                                                        source: modelData.cover_url || ""
                                                        fillMode: Image.PreserveAspectCrop
                                                        visible: status === Image.Ready && source.toString().length > 0
                                                    }
                                                }

                                                // Title & Artist
                                                ColumnLayout {
                                                    Layout.fillWidth: true
                                                    Layout.alignment: Qt.AlignVCenter
                                                    spacing: 2

                                                    Label {
                                                        Layout.fillWidth: true
                                                        text: modelData.title || "Unknown Track"
                                                        font.family: bodyFont
                                                        font.pixelSize: 13
                                                        font.weight: Font.DemiBold
                                                        color: textPrimary
                                                        elide: Text.ElideRight
                                                    }

                                                    Label {
                                                        Layout.fillWidth: true
                                                        text: modelData.artist || "Unknown Artist"
                                                        font.family: bodyFont
                                                        font.pixelSize: 12
                                                        color: textSecondary
                                                        elide: Text.ElideRight
                                                    }
                                                }

                                                // Album
                                                Label {
                                                    Layout.preferredWidth: 180
                                                    Layout.alignment: Qt.AlignVCenter
                                                    text: modelData.album || ""
                                                    font.family: bodyFont
                                                    font.pixelSize: 12
                                                    color: textSecondary
                                                    elide: Text.ElideRight
                                                }

                                                // Service Tag Pill (subtle, clean, no border)
                                                Item {
                                                    Layout.preferredWidth: 80
                                                    Layout.preferredHeight: 22
                                                    Layout.alignment: Qt.AlignVCenter

                                                    Rectangle {
                                                        anchors.centerIn: parent
                                                        height: 20
                                                        width: sTagLabel.implicitWidth + 12
                                                        radius: 4
                                                        color: surfaceTag

                                                        Label {
                                                            id: sTagLabel
                                                            anchors.centerIn: parent
                                                            text: window.formatServiceName(modelData.service)
                                                            font.family: bodyFont
                                                            font.pixelSize: 11
                                                            font.weight: Font.Normal
                                                            color: textSecondary
                                                        }
                                                    }
                                                }

                                                // Duration
                                                Label {
                                                    Layout.preferredWidth: 54
                                                    Layout.alignment: Qt.AlignVCenter
                                                    text: {
                                                        const d = modelData.duration || 0
                                                        if (!d) return "--:--"
                                                        const mins = Math.floor(d / 60)
                                                        const secs = d % 60
                                                        return mins + ":" + (secs < 10 ? "0" : "") + secs
                                                    }
                                                    font.family: bodyFont
                                                    font.pixelSize: 12
                                                    color: silverDim
                                                    horizontalAlignment: Text.AlignRight
                                                }

                                                // Actions Row (Flat, borderless quiet icons)
                                                Item {
                                                    Layout.preferredWidth: 68
                                                    Layout.preferredHeight: 32
                                                    Layout.alignment: Qt.AlignVCenter

                                                    RowLayout {
                                                        anchors.centerIn: parent
                                                        spacing: 4

                                                        PressDepthIconButton {
                                                            Layout.preferredWidth: 28
                                                            Layout.preferredHeight: 28
                                                            Layout.alignment: Qt.AlignVCenter
                                                            boxSize: 28
                                                            iconSize: 13
                                                            cornerRadius: 6
                                                            backgroundColor: "transparent"
                                                            borderColor: "transparent"
                                                            hoverBackgroundColor: surfaceElevated
                                                            hoverBorderColor: "transparent"
                                                            iconName: (downloaderBridge && downloaderBridge.previewPlaying && downloaderBridge.currentPreviewPath === (modelData.preview_url || "")) ? "pause" : "play"
                                                            tint: (modelData.preview_url && modelData.preview_url.length > 0) ? silverDim : textMuted
                                                            hoverTint: textPrimary
                                                            enabled: !!(modelData.preview_url && modelData.preview_url.length > 0)
                                                            opacity: enabled ? 1.0 : 0.35
                                                            tooltipText: enabled ? "Preview audio snippet" : "No preview available"
                                                            onClicked: {
                                                                if (downloaderBridge && modelData.preview_url) {
                                                                    downloaderBridge.togglePreview(modelData.preview_url, modelData)
                                                                }
                                                            }
                                                        }

                                                        PressDepthIconButton {
                                                            Layout.preferredWidth: 28
                                                            Layout.preferredHeight: 28
                                                            Layout.alignment: Qt.AlignVCenter
                                                            boxSize: 28
                                                            iconSize: 13
                                                            cornerRadius: 6
                                                            backgroundColor: "transparent"
                                                            borderColor: "transparent"
                                                            hoverBackgroundColor: brandAccent
                                                            hoverBorderColor: "transparent"
                                                            iconName: "arrow-down"
                                                            tint: silverDim
                                                            hoverTint: "#FFFFFF"
                                                            tooltipText: "Download track"
                                                            onClicked: {
                                                                if (downloaderBridge) {
                                                                    downloaderBridge.downloadTrack(modelData)
                                                                    window.page = "queue"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }

                                            MouseArea {
                                                id: rowMouse
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                acceptedButtons: Qt.NoButton
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Item {
                        id: queuePageItem

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 28
                            anchors.rightMargin: 28
                            anchors.topMargin: 12
                            anchors.bottomMargin: 16
                            spacing: 14

                            // Header Row
                            RowLayout {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 38
                                spacing: 10

                                Label {
                                    text: "Downloads"
                                    font.family: displayFont
                                    font.pixelSize: 18
                                    font.weight: Font.DemiBold
                                    color: textPrimary
                                }

                                // Active count badge pill
                                Rectangle {
                                    visible: window.activeJobs.length > 0
                                    implicitWidth: queueCountLabel.implicitWidth + 14
                                    implicitHeight: 20
                                    radius: 10
                                    color: surfaceElevated
                                    border.width: 1
                                    border.color: borderSubtle

                                    Text {
                                        id: queueCountLabel
                                        anchors.centerIn: parent
                                        text: window.activeJobs.length
                                        font.family: monoFont
                                        font.pixelSize: 11
                                        font.weight: Font.Medium
                                        color: silverDim
                                    }
                                }

                                Item { Layout.fillWidth: true }

                                // Open Download Folder
                                SettingButton {
                                    text: "Open Folder"
                                    iconName: "folder"
                                    onClicked: if (downloaderBridge) downloaderBridge.openDownloadFolder()
                                }

                                // Cancel All (visible when 2 or more active jobs)
                                SettingButton {
                                    visible: {
                                        var activeCount = 0
                                        for (var i = 0; i < window.activeJobs.length; i++) {
                                            var s = window.activeJobs[i].status
                                            if (s !== "Completed" && s !== "Failed" && s !== "Cancelled") {
                                                activeCount++
                                            }
                                        }
                                        return activeCount > 1
                                    }
                                    text: "Cancel All"
                                    iconName: "x"
                                    destructive: true
                                    onClicked: {
                                        if (downloaderBridge) {
                                            downloaderBridge.cancelAll()
                                            window.activeJobs = downloaderBridge.getActiveJobs()
                                        }
                                    }
                                }

                                // Clear Finished (visible when any completed, failed, or cancelled jobs exist)
                                SettingButton {
                                    visible: {
                                        for (var i = 0; i < window.activeJobs.length; i++) {
                                            var s = window.activeJobs[i].status
                                            if (s === "Completed" || s === "Failed" || s === "Cancelled") {
                                                return true
                                            }
                                        }
                                        return false
                                    }
                                    text: "Clear Finished"
                                    iconName: "x"
                                    onClicked: {
                                        if (downloaderBridge) {
                                            downloaderBridge.clearCompletedJobs()
                                            window.activeJobs = downloaderBridge.getActiveJobs()
                                        }
                                    }
                                }
                            }

                            // Empty Queue State
                            Rectangle {
                                visible: window.activeJobs.length === 0
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: "transparent"

                                ColumnLayout {
                                    anchors.centerIn: parent
                                    spacing: 12

                                    LucideIcon {
                                        Layout.alignment: Qt.AlignHCenter
                                        Layout.preferredWidth: 38
                                        Layout.preferredHeight: 38
                                        icon: "download"
                                        color: textSecondary
                                    }

                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "No downloads in queue"
                                        font.family: displayFont
                                        font.pixelSize: 16
                                        font.weight: Font.DemiBold
                                        color: textPrimary
                                    }

                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "Search or paste any track or album link in Explore to grab music"
                                        font.family: bodyFont
                                        font.pixelSize: 12
                                        color: silverDim
                                    }

                                    Item { Layout.preferredHeight: 4 }

                                    SettingButton {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "Go to Explore"
                                        iconName: "search"
                                        primary: true
                                        onClicked: window.page = "explore"
                                    }
                                }
                            }

                            // Active Queue List
                            ListView {
                                id: queueList
                                visible: window.activeJobs.length > 0
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                spacing: 8
                                model: window.activeJobs

                                delegate: Rectangle {
                                    id: queueItemRect
                                    required property var modelData
                                    width: queueList.width
                                    height: 64
                                    radius: 8
                                    color: itemMouseArea.containsMouse ? surfaceCardHover : surfaceCard
                                    border.width: 1
                                    border.color: itemMouseArea.containsMouse ? borderVariant : borderSubtle

                                    Behavior on color { ColorAnimation { duration: 120 } }
                                    Behavior on border.color { ColorAnimation { duration: 120 } }

                                    MouseArea {
                                        id: itemMouseArea
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        acceptedButtons: Qt.NoButton
                                    }

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 12
                                        anchors.rightMargin: 12
                                        anchors.topMargin: 10
                                        anchors.bottomMargin: 10
                                        spacing: 12

                                        // Cover Art Thumbnail with Fallback
                                        Rectangle {
                                            Layout.preferredWidth: 44
                                            Layout.preferredHeight: 44
                                            radius: 6
                                            clip: true
                                            color: surfaceElevated
                                            border.width: 1
                                            border.color: borderSubtle

                                            LucideIcon {
                                                anchors.centerIn: parent
                                                width: 18
                                                height: 18
                                                icon: "music"
                                                color: silverDim
                                            }

                                            Image {
                                                anchors.fill: parent
                                                source: modelData.cover_url || ""
                                                fillMode: Image.PreserveAspectCrop
                                                asynchronous: true
                                                visible: status === Image.Ready
                                            }
                                        }

                                        // Central Info Column
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 4

                                            // Row 1: Title + Speed/ETA / Status indicator
                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 8

                                                Label {
                                                    Layout.fillWidth: true
                                                    text: modelData.title || "Track"
                                                    font.family: displayFont
                                                    font.pixelSize: 13
                                                    font.weight: Font.DemiBold
                                                    color: textPrimary
                                                    elide: Text.ElideRight
                                                }

                                                // Speed & ETA (only when actively downloading)
                                                Label {
                                                    visible: {
                                                        var s = modelData.status
                                                        return s !== "Completed" && s !== "Failed" && s !== "Cancelled" && !!modelData.speed
                                                    }
                                                    text: modelData.speed + (modelData.eta ? " • ETA " + modelData.eta : "")
                                                    font.family: monoFont
                                                    font.pixelSize: 10
                                                    color: silverDim
                                                }
                                            }

                                            // Row 2: Slender Progress Bar
                                            Rectangle {
                                                Layout.fillWidth: true
                                                Layout.preferredHeight: 3
                                                radius: 1.5
                                                color: surfaceElevated

                                                Rectangle {
                                                    id: progressFill
                                                    width: parent.width * Math.max(0.0, Math.min(1.0, (modelData.percent || 0) / 100))
                                                    height: parent.height
                                                    radius: 1.5
                                                    color: {
                                                        var s = modelData.status
                                                        if (s === "Completed") return success
                                                        if (s === "Failed" || s === "Cancelled") return danger
                                                        return recordRed
                                                    }
                                                    Behavior on width { NumberAnimation { duration: 150 } }
                                                }
                                            }

                                            // Row 3: Artist & Album + Status Badge
                                            RowLayout {
                                                Layout.fillWidth: true
                                                spacing: 8

                                                Label {
                                                    Layout.fillWidth: true
                                                    text: (modelData.artist || "Unknown Artist") + (modelData.album ? " \u00b7 " + modelData.album : "")
                                                    font.family: bodyFont
                                                    font.pixelSize: 11
                                                    color: textSecondary
                                                    elide: Text.ElideRight
                                                }

                                                // Status badge pill
                                                Rectangle {
                                                    implicitWidth: statusText.implicitWidth + 12
                                                    implicitHeight: 18
                                                    radius: 9
                                                    color: {
                                                        var s = modelData.status
                                                        if (s === "Completed") return Qt.alpha(success, 0.15)
                                                        if (s === "Failed") return Qt.alpha(danger, 0.15)
                                                        if (s === "Cancelled") return surfaceElevated
                                                        if (s === "Queued") return surfaceElevated
                                                        return Qt.alpha(recordRed, 0.15)
                                                    }
                                                    border.width: 1
                                                    border.color: {
                                                        var s = modelData.status
                                                        if (s === "Completed") return Qt.alpha(success, 0.3)
                                                        if (s === "Failed") return Qt.alpha(danger, 0.3)
                                                        if (s === "Cancelled") return borderSubtle
                                                        if (s === "Queued") return borderSubtle
                                                        return Qt.alpha(recordRed, 0.3)
                                                    }

                                                    Text {
                                                        id: statusText
                                                        anchors.centerIn: parent
                                                        text: {
                                                            var s = modelData.status
                                                            if (s === "Completed") return "Complete"
                                                            if (s === "Failed") return "Failed"
                                                            if (s === "Cancelled") return "Cancelled"
                                                            if (s === "Queued") return "Queued"
                                                            if (s === "Converting audio...") return "Converting"
                                                            return Math.round(modelData.percent || 0) + "%"
                                                        }
                                                        font.family: monoFont
                                                        font.pixelSize: 10
                                                        font.weight: Font.Medium
                                                        color: {
                                                            var s = modelData.status
                                                            if (s === "Completed") return success
                                                            if (s === "Failed") return danger
                                                            if (s === "Cancelled" || s === "Queued") return silverDim
                                                            return recordRed
                                                        }
                                                    }
                                                }
                                            }
                                        }

                                        // Actions column with fixed width so progress bars and status pills align uniformly across cards
                                        Item {
                                            Layout.preferredWidth: 102
                                            Layout.fillHeight: true

                                            RowLayout {
                                                anchors.right: parent.right
                                                anchors.verticalCenter: parent.verticalCenter
                                                spacing: 6

                                                // Completed actions: Play preview & Show in folder
                                                PressDepthIconButton {
                                                    visible: modelData.status === "Completed" && !!modelData.file_path
                                                    boxSize: 30
                                                    iconSize: 13
                                                    iconName: (downloaderBridge && downloaderBridge.previewPlaying && downloaderBridge.currentPreviewPath === modelData.file_path) ? "pause" : "play"
                                                    tooltipText: (downloaderBridge && downloaderBridge.previewPlaying && downloaderBridge.currentPreviewPath === modelData.file_path) ? "Pause audio" : "Play audio"
                                                    onClicked: {
                                                        if (downloaderBridge && modelData.file_path) {
                                                            downloaderBridge.togglePreview(modelData.file_path, {
                                                                "title": modelData.title,
                                                                "artist": modelData.artist,
                                                                "path": modelData.file_path,
                                                                "cover_path": ""
                                                            })
                                                        }
                                                    }
                                                }

                                                PressDepthIconButton {
                                                    visible: modelData.status === "Completed" && !!modelData.file_path
                                                    boxSize: 30
                                                    iconSize: 13
                                                    iconName: "folder"
                                                    tooltipText: "Show in folder"
                                                    onClicked: {
                                                        if (downloaderBridge && modelData.file_path) {
                                                            downloaderBridge.revealFileInExplorer(modelData.file_path)
                                                        }
                                                    }
                                                }

                                                // Cancel button (active jobs) or Dismiss button (completed/failed/cancelled)
                                                PressDepthIconButton {
                                                    boxSize: 30
                                                    iconSize: 12
                                                    iconName: "x"
                                                    tooltipText: {
                                                        var s = modelData.status
                                                        if (s === "Completed" || s === "Failed" || s === "Cancelled") return "Remove from list"
                                                        return "Cancel download"
                                                    }
                                                    onClicked: {
                                                        if (downloaderBridge && modelData.id) {
                                                            downloaderBridge.dismissJob(modelData.id)
                                                            window.activeJobs = downloaderBridge.getActiveJobs()
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // =========================================================
                    // PAGE 3: LIBRARY
                    // =========================================================
                    Item {
                        id: libraryPageItem

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 28
                            anchors.rightMargin: 28
                            anchors.topMargin: 12
                            anchors.bottomMargin: 16
                            spacing: 14

                            // Header Row
                            RowLayout {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 38
                                spacing: 10

                                Label {
                                    text: "Library"
                                    font.family: displayFont
                                    font.pixelSize: 18
                                    font.weight: Font.DemiBold
                                    color: textPrimary
                                }

                                // Song count badge pill
                                Rectangle {
                                    visible: window.downloadedFiles.length > 0
                                    implicitWidth: libCountLabel.implicitWidth + 14
                                    implicitHeight: 20
                                    radius: 10
                                    color: surfaceElevated
                                    border.width: 1
                                    border.color: borderSubtle

                                    Text {
                                        id: libCountLabel
                                        anchors.centerIn: parent
                                        text: window.downloadedFiles.length
                                        font.family: monoFont
                                        font.pixelSize: 11
                                        font.weight: Font.Medium
                                        color: silverDim
                                    }
                                }

                                Item { Layout.fillWidth: true }

                                // View Mode Toggle (Grid / List)
                                Rectangle {
                                    Layout.preferredHeight: 30
                                    Layout.preferredWidth: 68
                                    radius: 6
                                    color: surfaceCard
                                    border.width: 1
                                    border.color: borderSubtle

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 2
                                        spacing: 2

                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                            radius: 4
                                            color: window.libraryViewMode === "grid" ? surfaceElevated : "transparent"
                                            border.width: window.libraryViewMode === "grid" ? 1 : 0
                                            border.color: borderVariant

                                            LucideIcon {
                                                anchors.centerIn: parent
                                                width: 14
                                                height: 14
                                                icon: "grid-2x2"
                                                color: window.libraryViewMode === "grid" ? textPrimary : textSecondary
                                            }
                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: window.libraryViewMode = "grid"
                                            }
                                        }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                            radius: 4
                                            color: window.libraryViewMode === "list" ? surfaceElevated : "transparent"
                                            border.width: window.libraryViewMode === "list" ? 1 : 0
                                            border.color: borderVariant

                                            LucideIcon {
                                                anchors.centerIn: parent
                                                width: 14
                                                height: 14
                                                icon: "list"
                                                color: window.libraryViewMode === "list" ? textPrimary : textSecondary
                                            }
                                            MouseArea {
                                                anchors.fill: parent
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: window.libraryViewMode = "list"
                                            }
                                        }
                                    }
                                }

                                SettingButton {
                                    text: "Open Folder"
                                    iconName: "folder"
                                    onClicked: if (downloaderBridge) downloaderBridge.openDownloadFolder()
                                }
                            }

                            // Empty Library State
                            Rectangle {
                                visible: window.downloadedFiles.length === 0
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: "transparent"

                                ColumnLayout {
                                    anchors.centerIn: parent
                                    spacing: 12

                                    LucideIcon {
                                        Layout.alignment: Qt.AlignHCenter
                                        Layout.preferredWidth: 38
                                        Layout.preferredHeight: 38
                                        icon: "disc"
                                        color: textSecondary
                                    }

                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "No downloaded songs in library"
                                        font.family: displayFont
                                        font.pixelSize: 16
                                        font.weight: Font.DemiBold
                                        color: textPrimary
                                    }

                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "Grab any track or album in Explore to start your offline library"
                                        font.family: bodyFont
                                        font.pixelSize: 12
                                        color: silverDim
                                    }

                                    Item { Layout.preferredHeight: 4 }

                                    SettingButton {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "Go to Explore"
                                        iconName: "search"
                                        primary: true
                                        onClicked: window.page = "explore"
                                    }
                                }
                            }

                            // Grid View
                            GridView {
                                id: libGrid
                                visible: window.downloadedFiles.length > 0 && window.libraryViewMode === "grid"
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                cellWidth: 172
                                cellHeight: 236
                                model: window.downloadedFiles

                                delegate: Rectangle {
                                    id: gridCard
                                    required property var modelData
                                    width: 160
                                    height: 232
                                    radius: 8
                                    color: cardM.containsMouse ? surfaceCardHover : surfaceCard
                                    border.width: 1
                                    border.color: (downloaderBridge && downloaderBridge.currentPreviewPath === modelData.path) ? recordRed : (cardM.containsMouse ? borderVariant : borderSubtle)

                                    Behavior on color { ColorAnimation { duration: 120 } }
                                    Behavior on border.color { ColorAnimation { duration: 120 } }

                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 10
                                        spacing: 8

                                        // Artwork Container
                                        Rectangle {
                                            Layout.preferredWidth: 140
                                            Layout.preferredHeight: 140
                                            Layout.alignment: Qt.AlignHCenter
                                            radius: 6
                                            clip: true
                                            color: surfaceElevated
                                            border.width: 1
                                            border.color: borderSubtle

                                            LucideIcon {
                                                anchors.centerIn: parent
                                                width: 32
                                                height: 32
                                                icon: "music"
                                                color: silverDim
                                                visible: !gridImg.visible || gridImg.status !== Image.Ready
                                            }

                                            Image {
                                                id: gridImg
                                                anchors.fill: parent
                                                source: modelData.cover_url || ""
                                                fillMode: Image.PreserveAspectCrop
                                                asynchronous: true
                                                visible: status === Image.Ready && source.toString().length > 0
                                            }

                                            // Play/Pause Overlay Button on hover or playing
                                            Rectangle {
                                                visible: cardM.containsMouse || (downloaderBridge && downloaderBridge.currentPreviewPath === modelData.path)
                                                anchors.centerIn: parent
                                                width: 38
                                                height: 38
                                                radius: 19
                                                color: (downloaderBridge && downloaderBridge.currentPreviewPath === modelData.path && downloaderBridge.previewPlaying) ? recordRed : Qt.rgba(0, 0, 0, 0.72)
                                                border.width: 1
                                                border.color: Qt.rgba(255, 255, 255, 0.15)

                                                LucideIcon {
                                                    anchors.centerIn: parent
                                                    width: 16
                                                    height: 16
                                                    icon: (downloaderBridge && downloaderBridge.previewPlaying && downloaderBridge.currentPreviewPath === modelData.path) ? "pause" : "play"
                                                    color: "#FFFFFF"
                                                }
                                            }
                                        }

                                        // Details
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 2

                                            Label {
                                                Layout.fillWidth: true
                                                text: modelData.title || modelData.filename
                                                font.family: displayFont
                                                font.pixelSize: 13
                                                font.weight: Font.DemiBold
                                                color: (downloaderBridge && downloaderBridge.currentPreviewPath === modelData.path) ? recordRed : textPrimary
                                                elide: Text.ElideRight
                                            }

                                            Label {
                                                Layout.fillWidth: true
                                                text: modelData.artist || "Unknown Artist"
                                                font.family: bodyFont
                                                font.pixelSize: 11
                                                color: textSecondary
                                                elide: Text.ElideRight
                                            }
                                        }

                                        Item { Layout.fillHeight: true }

                                        // Card Footer (Size & Reveal Folder action)
                                        RowLayout {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 22

                                            Label {
                                                text: modelData.size || ""
                                                font.family: monoFont
                                                font.pixelSize: 10
                                                color: silverDim
                                            }

                                            Item { Layout.fillWidth: true }

                                            PressDepthIconButton {
                                                boxSize: 22
                                                iconSize: 12
                                                iconName: "folder"
                                                tooltipText: "Show in folder"
                                                onClicked: if (downloaderBridge) downloaderBridge.revealFileInExplorer(modelData.path)
                                            }
                                        }
                                    }

                                    MouseArea {
                                        id: cardM
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            if (downloaderBridge) {
                                                downloaderBridge.togglePreview(modelData.path, {
                                                    "title": modelData.title,
                                                    "artist": modelData.artist,
                                                    "path": modelData.path,
                                                    "cover_path": modelData.cover_path || ""
                                                })
                                            }
                                        }
                                    }
                                }
                            }

                            // List View
                            ListView {
                                id: libList
                                visible: window.downloadedFiles.length > 0 && window.libraryViewMode === "list"
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                spacing: 6
                                model: window.downloadedFiles

                                delegate: Rectangle {
                                    id: listCard
                                    required property var modelData
                                    width: libList.width
                                    height: 56
                                    radius: 8
                                    color: lRowM.containsMouse ? surfaceCardHover : surfaceCard
                                    border.width: 1
                                    border.color: (downloaderBridge && downloaderBridge.currentPreviewPath === modelData.path) ? recordRed : (lRowM.containsMouse ? borderVariant : borderSubtle)

                                    Behavior on color { ColorAnimation { duration: 120 } }
                                    Behavior on border.color { ColorAnimation { duration: 120 } }

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 12
                                        anchors.rightMargin: 12
                                        spacing: 12

                                        // Play / Pause Icon Button
                                        PressDepthIconButton {
                                            boxSize: 32
                                            iconSize: 14
                                            iconName: (downloaderBridge && downloaderBridge.previewPlaying && downloaderBridge.currentPreviewPath === modelData.path) ? "pause" : "play"
                                            tint: (downloaderBridge && downloaderBridge.currentPreviewPath === modelData.path) ? recordRed : silverDim
                                            tooltipText: "Play / Pause"
                                            onClicked: {
                                                if (downloaderBridge) {
                                                    downloaderBridge.togglePreview(modelData.path, {
                                                        "title": modelData.title,
                                                        "artist": modelData.artist,
                                                        "path": modelData.path,
                                                        "cover_path": modelData.cover_path || ""
                                                    })
                                                }
                                            }
                                        }

                                        // Cover Art Thumbnail
                                        Rectangle {
                                            Layout.preferredWidth: 38
                                            Layout.preferredHeight: 38
                                            radius: 6
                                            clip: true
                                            color: surfaceElevated
                                            border.width: 1
                                            border.color: borderSubtle

                                            LucideIcon {
                                                anchors.centerIn: parent
                                                width: 16
                                                height: 16
                                                icon: "music"
                                                color: silverDim
                                                visible: !listImg.visible || listImg.status !== Image.Ready
                                            }

                                            Image {
                                                id: listImg
                                                anchors.fill: parent
                                                source: modelData.cover_url || ""
                                                fillMode: Image.PreserveAspectCrop
                                                asynchronous: true
                                                visible: status === Image.Ready && source.toString().length > 0
                                            }
                                        }

                                        // Track Info Column
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 2

                                            Label {
                                                Layout.fillWidth: true
                                                text: modelData.title || modelData.filename
                                                font.family: displayFont
                                                font.pixelSize: 13
                                                font.weight: Font.DemiBold
                                                color: (downloaderBridge && downloaderBridge.currentPreviewPath === modelData.path) ? recordRed : textPrimary
                                                elide: Text.ElideRight
                                            }

                                            Label {
                                                Layout.fillWidth: true
                                                text: (modelData.artist || "Unknown Artist") + (modelData.album ? " \u00b7 " + modelData.album : "")
                                                font.family: bodyFont
                                                font.pixelSize: 11
                                                color: textSecondary
                                                elide: Text.ElideRight
                                            }
                                        }

                                        // File Size
                                        Label {
                                            Layout.preferredWidth: 64
                                            text: modelData.size || ""
                                            font.family: monoFont
                                            font.pixelSize: 11
                                            color: silverDim
                                            horizontalAlignment: Text.AlignRight
                                        }

                                        // Containerless Action Buttons
                                        PressDepthIconButton {
                                            boxSize: 30
                                            iconSize: 13
                                            iconName: "folder"
                                            tooltipText: "Show in folder"
                                            onClicked: if (downloaderBridge) downloaderBridge.revealFileInExplorer(modelData.path)
                                        }

                                        PressDepthIconButton {
                                            boxSize: 30
                                            iconSize: 13
                                            iconName: "x"
                                            tooltipText: "Delete file"
                                            hoverTint: danger
                                            onClicked: if (downloaderBridge) downloaderBridge.deleteFile(modelData.path)
                                        }
                                    }

                                    MouseArea {
                                        id: lRowM
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        acceptedButtons: Qt.NoButton
                                    }
                                }
                            }
                        }
                    }

                    // =========================================================
                    // PAGE 4: SETTINGS
                    // =========================================================
                    Item {
                        id: settingsPage
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 28
                            anchors.rightMargin: 28
                            anchors.topMargin: 12
                            anchors.bottomMargin: 16
                            spacing: 14

                            // Standard Page Header Row
                            RowLayout {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 40
                                spacing: 12

                                Label {
                                    text: "Settings"
                                    font.family: displayFont
                                    font.pixelSize: 20
                                    font.weight: Font.DemiBold
                                    color: textPrimary
                                }

                                Item { Layout.fillWidth: true }
                            }

                            // Scrollable Settings Content
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                contentWidth: width

                                ColumnLayout {
                                    width: parent.width
                                    spacing: 16

                                    // --- SECTION 1: AUDIO QUALITY & FORMAT ---
                                    Label {
                                        text: "AUDIO QUALITY & FORMAT"
                                        font.family: monoFont
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                        color: silverDim
                                    }

                                    SettingCard {
                                        SettingRow {
                                            title: "Output Format"
                                            subtitle: "Select preferred audio encoding container"
                                            iconName: "music"

                                            Row {
                                                spacing: 6
                                                Repeater {
                                                    model: ["mp3", "flac", "m4a", "opus"]
                                                    FilterChip {
                                                        required property var modelData
                                                        text: modelData.toUpperCase()
                                                        selected: (downloaderBridge ? downloaderBridge.audioFormat : "mp3") === modelData
                                                        onClicked: if (downloaderBridge) downloaderBridge.setAudioFormat(modelData)
                                                    }
                                                }
                                            }
                                        }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 1
                                            color: borderSubtle
                                            opacity: 0.6
                                        }

                                        SettingRow {
                                            title: "Bitrate Quality"
                                            subtitle: (downloaderBridge && downloaderBridge.audioFormat === "flac")
                                                ? "Lossless bit-perfect preservation (Bitrate selection not applicable to FLAC)"
                                                : "Constant target bitrate for lossy compression"
                                            iconName: "audio-lines"

                                            Row {
                                                spacing: 6
                                                visible: !(downloaderBridge && downloaderBridge.audioFormat === "flac")
                                                Repeater {
                                                    model: [
                                                        { id: "320", label: "320 kbps (High)" },
                                                        { id: "256", label: "256 kbps (Standard)" },
                                                        { id: "192", label: "192 kbps (Compact)" }
                                                    ]
                                                    FilterChip {
                                                        required property var modelData
                                                        text: modelData.label
                                                        selected: (downloaderBridge ? downloaderBridge.audioQuality : "320") === modelData.id
                                                        onClicked: if (downloaderBridge) downloaderBridge.setAudioQuality(modelData.id)
                                                    }
                                                }
                                            }

                                            Label {
                                                visible: downloaderBridge && downloaderBridge.audioFormat === "flac"
                                                text: "Bit-Perfect Lossless"
                                                font.family: monoFont
                                                font.pixelSize: 11
                                                color: recordRedHover
                                            }
                                        }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 1
                                            color: borderSubtle
                                            opacity: 0.6
                                        }

                                        SettingRow {
                                            title: "Max Concurrent Downloads"
                                            subtitle: "Number of tracks downloaded simultaneously in queue"
                                            iconName: "download"

                                            Row {
                                                spacing: 6
                                                Repeater {
                                                    model: [
                                                        { count: 1, label: "1 Track" },
                                                        { count: 2, label: "2 Tracks (Default)" },
                                                        { count: 3, label: "3 Tracks" },
                                                        { count: 4, label: "4 Tracks" }
                                                    ]
                                                    FilterChip {
                                                        required property var modelData
                                                        text: modelData.label
                                                        selected: (downloaderBridge ? downloaderBridge.maxConcurrentDownloads : 2) === modelData.count
                                                        onClicked: if (downloaderBridge) downloaderBridge.setMaxConcurrentDownloads(modelData.count)
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    // --- SECTION 2: METADATA & LYRICS ---
                                    Label {
                                        text: "METADATA & LYRICS"
                                        font.family: monoFont
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                        color: silverDim
                                        Layout.topMargin: 4
                                    }

                                    SettingCard {
                                        SettingRow {
                                            title: "LRCLIB Synced Lyrics"
                                            subtitle: "Fetch and embed time-synchronized lyrics (.lrc) directly into audio tags"
                                            iconName: "quote"

                                            SettingSwitch {
                                                checked: downloaderBridge ? downloaderBridge.embedLyrics : true
                                                onToggled: if (downloaderBridge) downloaderBridge.setEmbedLyrics(checked)
                                            }
                                        }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 1
                                            color: borderSubtle
                                            opacity: 0.6
                                        }

                                        SettingRow {
                                            title: "Save Separate .lrc File"
                                            subtitle: "Export timestamped lyrics as companion .lrc text file in folder"
                                            iconName: "pencil"

                                            SettingSwitch {
                                                checked: downloaderBridge ? downloaderBridge.saveLrcFile : false
                                                onToggled: if (downloaderBridge) downloaderBridge.setSaveLrcFile(checked)
                                            }
                                        }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 1
                                            color: borderSubtle
                                            opacity: 0.6
                                        }

                                        SettingRow {
                                            title: "Embed High-Res Artwork"
                                            subtitle: "Inject album cover into ID3v2, MP4, and Vorbis metadata containers"
                                            iconName: "disc"

                                            SettingSwitch {
                                                checked: downloaderBridge ? downloaderBridge.embedArtwork : true
                                                onToggled: if (downloaderBridge) downloaderBridge.setEmbedArtwork(checked)
                                            }
                                        }
                                    }

                                    // --- SECTION 3: STORAGE & DIRECTORY ---
                                    Label {
                                        text: "STORAGE & DIRECTORY"
                                        font.family: monoFont
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                        color: silverDim
                                        Layout.topMargin: 4
                                    }

                                    SettingCard {
                                        SettingRow {
                                            title: "Download Location"
                                            subtitle: downloaderBridge ? downloaderBridge.downloadDirectory : "Music/GrabSongs"
                                            iconName: "folder"

                                            Row {
                                                spacing: 8

                                                SettingButton {
                                                    text: "Change Folder..."
                                                    iconName: "folder"
                                                    onClicked: if (downloaderBridge) downloaderBridge.chooseDownloadDirectory()
                                                }

                                                SettingButton {
                                                    text: "Open Folder"
                                                    iconName: "folder"
                                                    onClicked: if (downloaderBridge) downloaderBridge.openDownloadFolder()
                                                }
                                            }
                                        }
                                    }

                                    // --- SECTION 4: APPEARANCE ACCENT ---
                                    Label {
                                        text: "APPEARANCE ACCENT"
                                        font.family: monoFont
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                        color: silverDim
                                        Layout.topMargin: 4
                                    }

                                    SettingCard {
                                        SettingRow {
                                            title: "Color Accent"
                                            subtitle: "Natural warmth palette inspired by soot black, terracotta, pine, and ochre"
                                            iconName: "sliders-horizontal"

                                            Row {
                                                spacing: 6
                                                Repeater {
                                                    model: [
                                                        { id: "terracotta", name: "Terracotta", color: "#D95D39" },
                                                        { id: "tangerine",  name: "Tangerine",  color: "#F05423" },
                                                        { id: "pine",       name: "Pine",       color: "#3D7A5A" },
                                                        { id: "ochre",      name: "Ochre",      color: "#C88A2E" },
                                                        { id: "linen",      name: "Linen",      color: "#E4DFD7" }
                                                    ]
                                                    FilterChip {
                                                        required property var modelData
                                                        text: modelData.name
                                                        swatchColor: modelData.color
                                                        selected: window.accentName === modelData.id
                                                        onClicked: {
                                                            window.accentName = modelData.id
                                                            if (downloaderBridge) downloaderBridge.setAccentName(modelData.id)
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    // --- SECTION 5: SYSTEM & ENGINE ---
                                    Label {
                                        text: "SYSTEM & ENGINE"
                                        font.family: monoFont
                                        font.pixelSize: 11
                                        font.weight: Font.DemiBold
                                        color: silverDim
                                        Layout.topMargin: 4
                                    }

                                    SettingCard {
                                        SettingRow {
                                            title: "FFmpeg Audio Pipeline"
                                            subtitle: (downloaderBridge && downloaderBridge.ffmpegPath.length > 0)
                                                ? "Ready: " + downloaderBridge.ffmpegPath
                                                : "Bundled imageio-ffmpeg pipeline active"
                                            iconName: "zap"

                                            Label {
                                                text: "OPERATIONAL"
                                                font.family: monoFont
                                                font.pixelSize: 10
                                                font.weight: Font.Bold
                                                color: success
                                            }
                                        }

                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 1
                                            color: borderSubtle
                                            opacity: 0.6
                                        }

                                        SettingRow {
                                            title: "GrabSongs"
                                            subtitle: "High-fidelity lossless and 320kbps music downloader • GPL-3.0 License"
                                            iconName: "info"

                                            Label {
                                                text: "v2.4.0"
                                                font.family: monoFont
                                                font.pixelSize: 11
                                                color: silverDim
                                            }
                                        }
                                    }

                                    Item { Layout.preferredHeight: 12 }
                                }
                            }
                        }
                    }
                }
            }
        }

        Rectangle {
            id: miniPlayerDock
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            visible: !!(downloaderBridge && (downloaderBridge.previewPlaying || (downloaderBridge.currentPreviewPath && downloaderBridge.currentPreviewPath.length > 0)))
            height: visible ? 72 : 0
            clip: true
            color: surfaceDock

            Behavior on height { NumberAnimation { duration: 160; easing.type: Easing.OutCubic } }

            // Top border
            Rectangle {
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: 1
                color: borderSubtle
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 24
                anchors.rightMargin: 20
                spacing: 20

                // Track Info Section (320px)
                RowLayout {
                    Layout.preferredWidth: 320
                    Layout.maximumWidth: 360
                    spacing: 12

                    Rectangle {
                        Layout.preferredWidth: 52
                        Layout.preferredHeight: 52
                        radius: 8
                        clip: true
                        color: surfaceCard
                        border.width: 1
                        border.color: borderVariant

                        LucideIcon {
                            anchors.centerIn: parent
                            width: 24
                            height: 24
                            icon: "music"
                            color: (downloaderBridge && downloaderBridge.previewPlaying) ? recordRed : silverDim
                            visible: !dockArtImg.visible || dockArtImg.status !== Image.Ready
                        }

                        Image {
                            id: dockArtImg
                            anchors.fill: parent
                            source: (downloaderBridge && downloaderBridge.currentPreviewTrack && downloaderBridge.currentPreviewTrack.cover_path) ? downloaderBridge.currentPreviewTrack.cover_path : ""
                            fillMode: Image.PreserveAspectCrop
                            visible: status === Image.Ready && source.toString().length > 0
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Label {
                            Layout.fillWidth: true
                            text: (downloaderBridge && downloaderBridge.currentPreviewTrack && downloaderBridge.currentPreviewTrack.title) ? downloaderBridge.currentPreviewTrack.title : "GrabSongs Audio Engine"
                            font.family: displayFont
                            font.pixelSize: 13
                            font.weight: Font.DemiBold
                            color: textPrimary
                            elide: Text.ElideRight
                        }

                        Label {
                            Layout.fillWidth: true
                            text: (downloaderBridge && downloaderBridge.currentPreviewTrack && downloaderBridge.currentPreviewTrack.artist) ? downloaderBridge.currentPreviewTrack.artist : "Ready to grab from Spotify, Apple Music, YouTube & Deezer"
                            font.family: bodyFont
                            font.pixelSize: 11
                            color: textSecondary
                            elide: Text.ElideRight
                        }
                    }
                }

                // Center Transport Controls & Scrubber (fillWidth)
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4

                    // Transport Play Button (TransportButton from main app)
                    RowLayout {
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 16

                        TransportButton {
                            buttonSize: 38
                            accented: true
                            iconName: (downloaderBridge && downloaderBridge.previewPlaying) ? "pause" : "play"
                            tooltipText: "Play / Pause Preview"
                            onClicked: if (downloaderBridge) downloaderBridge.togglePlayPause()
                        }
                    }

                    // Scrubber Bar
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.preferredWidth: 420
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 10

                        Label {
                            text: window.formatTime(downloaderBridge ? downloaderBridge.previewPosition : 0)
                            font.family: monoFont
                            font.pixelSize: 10
                            color: silverDim
                        }

                        Rectangle {
                            id: dockScrubber
                            Layout.fillWidth: true
                            Layout.preferredHeight: 4
                            radius: 2
                            color: surfaceElevated

                            Rectangle {
                                width: {
                                    if (!downloaderBridge || downloaderBridge.previewDuration <= 0) return 0
                                    return parent.width * Math.max(0, Math.min(1.0, downloaderBridge.previewPosition / downloaderBridge.previewDuration))
                                }
                                height: parent.height
                                radius: 2
                                color: recordRed
                            }

                            MouseArea {
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                onClicked: mouse => {
                                    if (downloaderBridge && downloaderBridge.previewDuration > 0) {
                                        const frac = mouse.x / width
                                        downloaderBridge.seekPreview(Math.floor(frac * downloaderBridge.previewDuration))
                                    }
                                }
                            }
                        }

                        Label {
                            text: window.formatTime(downloaderBridge ? downloaderBridge.previewDuration : 0)
                            font.family: monoFont
                            font.pixelSize: 10
                            color: silverDim
                        }
                    }
                }

                // Right Volume & Destination (VolumeControl from main app)
                RowLayout {
                    Layout.preferredWidth: 220
                    Layout.alignment: Qt.AlignRight
                    spacing: 14

                    VolumeControl {
                        volume: downloaderBridge ? downloaderBridge.previewVolume : 1.0
                        onVolumeAdjusted: v => {
                            if (downloaderBridge) downloaderBridge.setPreviewVolume(v)
                        }
                    }

                    PressDepthIconButton {
                        boxSize: 32
                        iconSize: 16
                        iconName: "folder"
                        tooltipText: "Open Music Folder"
                        onClicked: if (downloaderBridge) downloaderBridge.openDownloadFolder()
                    }

                    PressDepthIconButton {
                        boxSize: 32
                        iconSize: 14
                        iconName: "x"
                        tooltipText: "Dismiss Preview"
                        onClicked: if (downloaderBridge) downloaderBridge.stopPreview()
                    }
                }
            }
        }
    }

    Item {
        visible: window.visibility !== Window.Maximized
        anchors.fill: parent
        z: 300

        MouseArea {
            anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; height: 4
            cursorShape: Qt.SizeVerCursor
            onPressed: window.startSystemResize(Qt.TopEdge)
        }
        MouseArea {
            anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom; height: 4
            cursorShape: Qt.SizeVerCursor
            onPressed: window.startSystemResize(Qt.BottomEdge)
        }
        MouseArea {
            anchors.left: parent.left; anchors.top: parent.top; anchors.bottom: parent.bottom; width: 4
            cursorShape: Qt.SizeHorCursor
            onPressed: window.startSystemResize(Qt.LeftEdge)
        }
        MouseArea {
            anchors.right: parent.right; anchors.top: parent.top; anchors.bottom: parent.bottom; width: 4
            cursorShape: Qt.SizeHorCursor
            onPressed: window.startSystemResize(Qt.RightEdge)
        }
        MouseArea {
            anchors.left: parent.left; anchors.top: parent.top; width: 8; height: 8
            cursorShape: Qt.SizeFDiagCursor
            onPressed: window.startSystemResize(Qt.TopEdge | Qt.LeftEdge)
        }
        MouseArea {
            anchors.right: parent.right; anchors.top: parent.top; width: 8; height: 8
            cursorShape: Qt.SizeBDiagCursor
            onPressed: window.startSystemResize(Qt.TopEdge | Qt.RightEdge)
        }
        MouseArea {
            anchors.left: parent.left; anchors.bottom: parent.bottom; width: 8; height: 8
            cursorShape: Qt.SizeBDiagCursor
            onPressed: window.startSystemResize(Qt.BottomEdge | Qt.LeftEdge)
        }
        MouseArea {
            anchors.right: parent.right; anchors.bottom: parent.bottom; width: 8; height: 8
            cursorShape: Qt.SizeFDiagCursor
            onPressed: window.startSystemResize(Qt.BottomEdge | Qt.RightEdge)
        }
    }
}
