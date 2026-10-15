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

    readonly property color recordRed: "#C23B30"
    readonly property color recordRedHover: "#D64337"
    readonly property color accentText: "#D8584E"

    readonly property color surfaceDeep: "#0B0A09"
    readonly property color surfaceBase: "#0E0D0C"
    readonly property color surfaceSidebar: "#131211"
    readonly property color surfaceDock: "#151412"
    readonly property color surfaceCard: "#181715"
    readonly property color surfaceInput: "#1A1917"
    readonly property color surfaceCardHover: "#22201D"
    readonly property color surfaceElevated: "#282623"
    readonly property color surfaceTag: surfaceCardHover
    readonly property color surfaceSelected: "#2E1C1A"

    readonly property color silver: "#C4C4C0"
    readonly property color silverDim: "#918E88"
    readonly property color textPrimary: "#F5F0EC"
    readonly property color textSecondary: "#A8A49E"
    readonly property color textMuted: "#6B6762"
    readonly property color danger: "#FF6B6B"
    readonly property color success: "#34D399"

    readonly property color borderSubtle: Qt.alpha(textPrimary, 0.05)
    readonly property color borderVariant: Qt.alpha(textPrimary, 0.09)
    readonly property color borderCard: borderVariant

    // Typography
    readonly property string displayFont: (typeof displayFontFamily !== "undefined" && displayFontFamily) ? displayFontFamily : "Space Grotesk"
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
    property string searchError: ""
    property string libraryViewMode: "grid" // "grid" or "list"

    // Timer to poll download queue and library
    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
            if (downloaderBridge) {
                window.activeJobs = downloaderBridge.getActiveJobs()
                if (window.page === "library") {
                    window.downloadedFiles = downloaderBridge.getDownloadedFiles()
                }
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
        function onSearchFinished(tracks) {
            window.isSearching = false
            window.searchResults = tracks
            if (tracks.length > 1 && tracks[0] && (tracks[0].album || tracks[0].service)) {
                window.resolvedCollection = {
                    title: tracks[0].album || (tracks[0].artist + " Collection"),
                    artist: tracks[0].artist || "",
                    cover_url: tracks[0].cover_url || "",
                    count: tracks.length,
                    service: tracks[0].service || "all"
                }
            }
        }
        function onSearchFailed(err) {
            window.isSearching = false
            window.searchError = err
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
    }

    Component.onCompleted: {
        if (downloaderBridge) {
            window.activeJobs = downloaderBridge.getActiveJobs()
            window.downloadedFiles = downloaderBridge.getDownloadedFiles()
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

    Rectangle {
        id: customTitleBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 60
        color: surfaceBase
        z: 100

        MouseArea {
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton
            onPressed: window.startSystemMove()
            onDoubleClicked: toggleMaximize()
        }

        // Title and Subtitle / Counter
        RowLayout {
            anchors.left: parent.left
            anchors.leftMargin: 20
            anchors.verticalCenter: parent.verticalCenter
            spacing: 12

            // CassetteCat branding icon
            Rectangle {
                width: 34
                height: 34
                radius: 8
                color: surfaceCard
                border.width: 1
                border.color: borderVariant

                Image {
                    anchors.centerIn: parent
                    width: 22
                    height: 22
                    source: (typeof appIconUrl !== "undefined" && appIconUrl) ? appIconUrl : ""
                    fillMode: Image.PreserveAspectFit
                }
            }

            Label {
                text: {
                    if (window.page === "explore") return "Explore"
                    if (window.page === "queue") return "Download Queue"
                    if (window.page === "library") return "GrabSongs Library"
                    if (window.page === "settings") return "Settings"
                    return "GrabSongs"
                }
                color: textPrimary
                font.family: displayFont
                font.pixelSize: 22
                font.weight: Font.Bold
                font.letterSpacing: -0.3
            }

            Label {
                text: {
                    if (window.page === "explore") {
                        return (downloaderBridge ? downloaderBridge.audioQuality + " kbps " + downloaderBridge.audioFormat.toUpperCase() : "320 kbps MP3")
                    }
                    if (window.page === "queue") return window.activeJobs.length + " active"
                    if (window.page === "library") return window.downloadedFiles.length + " songs"
                    return "Download Service"
                }
                color: silverDim
                font.family: monoFont
                font.pixelSize: 11
                Layout.leftMargin: 4
            }
        }

        // Window Controls (minBtn, maxBtn, closeBtn matching Main.qml)
        Row {
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            // Minimize
            Rectangle {
                id: minBtn
                width: 48
                height: 60
                color: minBtnMouse.containsMouse ? surfaceElevated : "transparent"

                Rectangle {
                    anchors.centerIn: parent
                    width: 10
                    height: 1.2
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
                width: 48
                height: 60
                color: maxBtnMouse.containsMouse ? surfaceElevated : "transparent"

                Rectangle {
                    anchors.centerIn: parent
                    width: 10
                    height: 10
                    color: "transparent"
                    border.width: 1.2
                    border.color: maxBtnMouse.containsMouse ? textPrimary : silverDim
                    radius: 1
                }

                MouseArea {
                    id: maxBtnMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.ArrowCursor
                    onClicked: toggleMaximize()
                }
            }

            // Close (turns recordRed on hover!)
            Rectangle {
                id: closeBtn
                width: 48
                height: 60
                color: closeBtnMouse.containsMouse ? recordRed : "transparent"

                Label {
                    anchors.centerIn: parent
                    text: "✕"
                    color: closeBtnMouse.containsMouse ? "#FFFFFF" : silverDim
                    font.family: displayFont
                    font.pixelSize: 12
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
                        iconName: "house"
                        label: "Explore & Grab"
                    }

                    NavItem {
                        appWindow: window
                        sidebarWidth: sidebarPanel.width
                        sidebarCollapsed: window.sidebarCollapsed
                        destination: "queue"
                        iconName: "clock"
                        label: "Download Queue"
                    }

                    NavItem {
                        appWindow: window
                        sidebarWidth: sidebarPanel.width
                        sidebarCollapsed: window.sidebarCollapsed
                        destination: "library"
                        iconName: "music"
                        label: "GrabSongs Library"
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

                    // Open GrabSongs Folder action
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
                                text: "GrabSongs Folder"
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
                            anchors.left: parent.left
                            anchors.leftMargin: 10
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

                    Item {
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.topMargin: 16
                            spacing: 14

                            Rectangle {
                                id: pageSearchBox
                                Layout.fillWidth: true
                                Layout.leftMargin: 28
                                Layout.rightMargin: 28
                                Layout.preferredHeight: 46
                                radius: 12
                                color: pageSearchInput.activeFocus ? surfaceElevated : surfaceCard
                                border.width: pageSearchInput.activeFocus ? 1.5 : 1
                                border.color: pageSearchInput.activeFocus ? recordRedHover : borderVariant

                                Behavior on color { ColorAnimation { duration: 120 } }
                                Behavior on border.color { ColorAnimation { duration: 120 } }

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 16
                                    anchors.rightMargin: 10
                                    spacing: 10

                                    LucideIcon {
                                        Layout.preferredWidth: 18
                                        Layout.preferredHeight: 18
                                        icon: "search"
                                        color: pageSearchInput.activeFocus ? recordRedHover : silverDim
                                        Behavior on color { ColorAnimation { duration: 120 } }
                                    }

                                    TextInput {
                                        id: pageSearchInput
                                        Layout.fillWidth: true
                                        color: textPrimary
                                        font.family: displayFont
                                        font.pixelSize: 14
                                        font.weight: Font.Medium
                                        selectByMouse: true
                                        onAccepted: window.triggerSearch()

                                        Text {
                                            anchors.fill: parent
                                            visible: !pageSearchInput.text && !pageSearchInput.activeFocus
                                            text: "Search songs, artists, albums, or paste links (Spotify, Apple Music, YouTube, Deezer)..."
                                            color: silverDim
                                            font.family: displayFont
                                            font.pixelSize: 14
                                            verticalAlignment: Text.AlignVCenter
                                        }
                                    }

                                    // Keyboard shortcut / Enter hint when idle
                                    Rectangle {
                                        visible: pageSearchInput.text.length === 0
                                        Layout.preferredHeight: 22
                                        Layout.preferredWidth: shortcutLabel.implicitWidth + 12
                                        radius: 5
                                        color: surfaceTag
                                        border.width: 1
                                        border.color: borderSubtle

                                        Label {
                                            id: shortcutLabel
                                            anchors.centerIn: parent
                                            text: "Enter"
                                            color: silverDim
                                            font.family: monoFont
                                            font.pixelSize: 10
                                            font.weight: Font.DemiBold
                                        }
                                    }

                                    // Clear button when active text exists
                                    Rectangle {
                                        visible: pageSearchInput.text.length > 0
                                        Layout.preferredWidth: 24
                                        Layout.preferredHeight: 24
                                        radius: 12
                                        color: clearMouse.containsMouse ? surfaceElevated : "transparent"

                                        LucideIcon {
                                            anchors.centerIn: parent
                                            width: 14
                                            height: 14
                                            icon: "x"
                                            color: clearMouse.containsMouse ? textPrimary : silverDim
                                        }

                                        MouseArea {
                                            id: clearMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                pageSearchInput.text = ""
                                                pageSearchInput.forceActiveFocus()
                                            }
                                        }
                                    }

                                    // Paste from clipboard button
                                    PressDepthIconButton {
                                        visible: pageSearchInput.text.length === 0
                                        boxSize: 32
                                        iconSize: 15
                                        iconName: "clipboard"
                                        tooltipText: "Paste link or query from clipboard"
                                        onClicked: {
                                            if (downloaderBridge) {
                                                const cb = downloaderBridge.getClipboardText().trim()
                                                if (cb) {
                                                    pageSearchInput.text = cb
                                                    window.triggerSearch(cb)
                                                }
                                            }
                                        }
                                    }

                                    // Action / Execute button (PressDepthIconButton)
                                    PressDepthIconButton {
                                        visible: pageSearchInput.text.length > 0
                                        boxSize: 32
                                        iconSize: 15
                                        iconName: window.isSearching ? "loader" : "arrow-right"
                                        highlighted: true
                                        tooltipText: "Search or Grab"
                                        onClicked: window.triggerSearch()
                                    }
                                }
                            }

                            // Platform Filter Chips (using authentic FilterChip.qml)
                            RowLayout {
                                Layout.fillWidth: true
                                Layout.leftMargin: 28
                                Layout.rightMargin: 28
                                spacing: 8

                                FilterChip {
                                    text: "All Platforms"
                                    iconName: "disc"
                                    selected: window.activePlatform === "all"
                                    onClicked: {
                                        window.activePlatform = "all"
                                        if (pageSearchInput.text.trim()) window.triggerSearch()
                                    }
                                }

                                FilterChip {
                                    text: "Spotify"
                                    iconName: "music"
                                    selected: window.activePlatform === "spotify"
                                    onClicked: {
                                        window.activePlatform = "spotify"
                                        if (pageSearchInput.text.trim()) window.triggerSearch()
                                    }
                                }

                                FilterChip {
                                    text: "Apple Music"
                                    iconName: "headphones"
                                    selected: window.activePlatform === "apple"
                                    onClicked: {
                                        window.activePlatform = "apple"
                                        if (pageSearchInput.text.trim()) window.triggerSearch()
                                    }
                                }

                                FilterChip {
                                    text: "YouTube"
                                    iconName: "play"
                                    selected: window.activePlatform === "youtube"
                                    onClicked: {
                                        window.activePlatform = "youtube"
                                        if (pageSearchInput.text.trim()) window.triggerSearch()
                                    }
                                }

                                FilterChip {
                                    text: "Deezer"
                                    iconName: "audio-lines"
                                    selected: window.activePlatform === "deezer"
                                    onClicked: {
                                        window.activePlatform = "deezer"
                                        if (pageSearchInput.text.trim()) window.triggerSearch()
                                    }
                                }

                                Item { Layout.fillWidth: true }

                                // Batch Download All Button (SettingButton from main app)
                                SettingButton {
                                    visible: window.searchResults.length > 1
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

                            // Main Results / Empty State / Loading Workspace
                            Item {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                Layout.leftMargin: 28
                                Layout.rightMargin: 28

                                // ---------------------------------------------
                                // EMPTY STATE: Centered Card matching reference
                                // ---------------------------------------------
                                Rectangle {
                                    visible: !window.isSearching && window.searchResults.length === 0 && !window.searchError
                                    anchors.centerIn: parent
                                    width: Math.min(parent.width - 40, 580)
                                    height: 250
                                    radius: 14
                                    color: surfaceCard
                                    border.width: 1
                                    border.color: borderSubtle

                                    ColumnLayout {
                                        anchors.centerIn: parent
                                        spacing: 12
                                        width: parent.width - 48

                                        Item {
                                            Layout.alignment: Qt.AlignHCenter
                                            width: 44
                                            height: 44

                                            Rectangle {
                                                anchors.centerIn: parent
                                                width: 42
                                                height: 42
                                                radius: 21
                                                color: "transparent"
                                                border.width: 2.5
                                                border.color: recordRed
                                            }
                                            Rectangle {
                                                anchors.centerIn: parent
                                                width: 24
                                                height: 24
                                                radius: 12
                                                color: "transparent"
                                                border.width: 1.5
                                                border.color: Qt.rgba(recordRed.r, recordRed.g, recordRed.b, 0.7)
                                            }
                                            Rectangle {
                                                anchors.centerIn: parent
                                                width: 8
                                                height: 8
                                                radius: 4
                                                color: recordRed
                                            }
                                        }

                                        Label {
                                            Layout.alignment: Qt.AlignHCenter
                                            text: "CassetteCat Universal Music Hub"
                                            font.family: displayFont
                                            font.pixelSize: 16
                                            font.weight: Font.Bold
                                            color: textPrimary
                                        }

                                        Label {
                                            Layout.alignment: Qt.AlignHCenter
                                            text: "Paste URLs from Spotify, Apple Music, Deezer, YouTube, or type track titles."
                                            font.family: bodyFont
                                            font.pixelSize: 13
                                            color: textSecondary
                                            horizontalAlignment: Text.AlignHCenter
                                        }

                                        Label {
                                            Layout.alignment: Qt.AlignHCenter
                                            text: "Full album discographies, high-res artwork, and synchronized lyrics are processed seamlessly."
                                            font.family: bodyFont
                                            font.pixelSize: 12
                                            color: textMuted
                                            horizontalAlignment: Text.AlignHCenter
                                        }
                                    }
                                }

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
                                        text: "Resolving metadata & extracting high-quality audio streams..."
                                        font.family: bodyFont
                                        font.pixelSize: 13
                                        color: textSecondary
                                    }
                                }

                                ColumnLayout {
                                    visible: !window.isSearching && window.searchResults.length > 0
                                    anchors.fill: parent
                                    spacing: 10

                                    Rectangle {
                                        visible: window.resolvedCollection !== null
                                        Layout.fillWidth: true
                                        Layout.preferredHeight: 88
                                        radius: 12
                                        color: surfaceCard
                                        border.width: 1
                                        border.color: borderSubtle

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: 12
                                            spacing: 16

                                            Rectangle {
                                                Layout.preferredWidth: 64
                                                Layout.preferredHeight: 64
                                                radius: 8
                                                clip: true
                                                color: surfaceElevated

                                                Image {
                                                    anchors.fill: parent
                                                    source: (window.resolvedCollection && window.resolvedCollection.cover_url) ? window.resolvedCollection.cover_url : ""
                                                    fillMode: Image.PreserveAspectCrop
                                                }
                                            }

                                            ColumnLayout {
                                                Layout.fillWidth: true
                                                spacing: 4

                                                Label {
                                                    text: (window.resolvedCollection && window.resolvedCollection.service ? window.resolvedCollection.service.toUpperCase() : "COLLECTION")
                                                    font.family: monoFont
                                                    font.pixelSize: 10
                                                    font.weight: Font.Bold
                                                    color: accentText
                                                }

                                                Label {
                                                    text: window.resolvedCollection ? window.resolvedCollection.title : ""
                                                    font.family: displayFont
                                                    font.pixelSize: 16
                                                    font.weight: Font.Bold
                                                    color: textPrimary
                                                    elide: Text.ElideRight
                                                }

                                                Label {
                                                    text: (window.resolvedCollection ? window.resolvedCollection.artist + " • " + window.resolvedCollection.count + " tracks" : "")
                                                    font.family: bodyFont
                                                    font.pixelSize: 12
                                                    color: textSecondary
                                                }
                                            }

                                            SettingButton {
                                                text: "Download Collection"
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

                                    // Results List
                                    ListView {
                                        id: resultsList
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        clip: true
                                        spacing: 4
                                        model: window.searchResults

                                        delegate: Rectangle {
                                            required property var modelData
                                            required property int index
                                            width: resultsList.width
                                            height: 54
                                            radius: 10
                                            color: rowMouse.containsMouse ? surfaceElevated : "transparent"

                                            RowLayout {
                                                anchors.fill: parent
                                                anchors.leftMargin: 14
                                                anchors.rightMargin: 14
                                                spacing: 12

                                                Label {
                                                    Layout.preferredWidth: 24
                                                    text: String(index + 1)
                                                    font.family: monoFont
                                                    font.pixelSize: 11
                                                    color: silverDim
                                                    horizontalAlignment: Text.AlignRight
                                                }

                                                Rectangle {
                                                    Layout.preferredWidth: 38
                                                    Layout.preferredHeight: 38
                                                    radius: 8
                                                    clip: true
                                                    color: surfaceElevated

                                                    Image {
                                                        anchors.fill: parent
                                                        source: modelData.cover_url || ""
                                                        fillMode: Image.PreserveAspectCrop
                                                    }
                                                }

                                                ColumnLayout {
                                                    Layout.fillWidth: true
                                                    spacing: 2

                                                    Label {
                                                        Layout.fillWidth: true
                                                        text: modelData.title || "Unknown Track"
                                                        font.family: displayFont
                                                        font.pixelSize: 13
                                                        font.weight: Font.DemiBold
                                                        color: textPrimary
                                                        elide: Text.ElideRight
                                                    }

                                                    Label {
                                                        Layout.fillWidth: true
                                                        text: (modelData.artist || "Unknown Artist") + (modelData.album ? " • " + modelData.album : "")
                                                        font.family: bodyFont
                                                        font.pixelSize: 11
                                                        color: textSecondary
                                                        elide: Text.ElideRight
                                                    }
                                                }

                                                // Service Tag Pill
                                                Rectangle {
                                                    Layout.preferredHeight: 20
                                                    Layout.preferredWidth: sTagLabel.implicitWidth + 12
                                                    radius: 4
                                                    color: surfaceTag
                                                    border.width: 1
                                                    border.color: borderSubtle

                                                    Label {
                                                        id: sTagLabel
                                                        anchors.centerIn: parent
                                                        text: (modelData.service || "source").toUpperCase()
                                                        font.family: monoFont
                                                        font.pixelSize: 9
                                                        font.weight: Font.Bold
                                                        color: {
                                                            const s = (modelData.service || "").toLowerCase()
                                                            if (s === "spotify") return "#1DB954"
                                                            if (s === "apple") return "#FC3C44"
                                                            if (s === "youtube") return "#FF4444"
                                                            if (s === "deezer") return "#A238FF"
                                                            return silverDim
                                                        }
                                                    }
                                                }

                                                // Duration
                                                Label {
                                                    Layout.preferredWidth: 44
                                                    text: {
                                                        const d = modelData.duration || 0
                                                        if (!d) return "--:--"
                                                        const mins = Math.floor(d / 60)
                                                        const secs = d % 60
                                                        return mins + ":" + (secs < 10 ? "0" : "") + secs
                                                    }
                                                    font.family: monoFont
                                                    font.pixelSize: 11
                                                    color: silverDim
                                                    horizontalAlignment: Text.AlignRight
                                                }

                                                // Download action (PressDepthIconButton from main app)
                                                PressDepthIconButton {
                                                    boxSize: 32
                                                    iconSize: 14
                                                    iconName: "arrow-down"
                                                    tint: textPrimary
                                                    hoverTint: "#FFFFFF"
                                                    hoverBackgroundColor: recordRed
                                                    tooltipText: "Download track"
                                                    onClicked: {
                                                        if (downloaderBridge) {
                                                            downloaderBridge.downloadTrack(modelData)
                                                            window.page = "queue"
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
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 28
                            anchors.rightMargin: 28
                            anchors.topMargin: 16
                            anchors.bottomMargin: 16
                            spacing: 14

                            RowLayout {
                                Layout.fillWidth: true
                                Label {
                                    text: "Active Downloads (" + window.activeJobs.length + ")"
                                    font.family: displayFont
                                    font.pixelSize: 18
                                    font.weight: Font.Bold
                                    color: textPrimary
                                }
                                Item { Layout.fillWidth: true }

                                SettingButton {
                                    visible: window.activeJobs.length > 0
                                    text: "Clear Completed"
                                    iconName: "x"
                                    onClicked: {
                                        if (downloaderBridge) {
                                            downloaderBridge.clearCompletedJobs()
                                            window.activeJobs = downloaderBridge.getActiveJobs()
                                        }
                                    }
                                }
                            }

                            // Empty Queue
                            Rectangle {
                                visible: window.activeJobs.length === 0
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: "transparent"

                                ColumnLayout {
                                    anchors.centerIn: parent
                                    spacing: 10
                                    LucideIcon {
                                        Layout.alignment: Qt.AlignHCenter
                                        width: 36
                                        height: 36
                                        icon: "clock"
                                        color: silverDim
                                    }
                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "No active downloads in queue"
                                        font.family: displayFont
                                        font.pixelSize: 16
                                        font.weight: Font.Bold
                                        color: textPrimary
                                    }
                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "Search or paste any music link in Explore to grab tracks"
                                        font.family: bodyFont
                                        font.pixelSize: 12
                                        color: silverDim
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
                                    required property var modelData
                                    width: queueList.width
                                    height: 68
                                    radius: 10
                                    color: surfaceCard
                                    border.width: 1
                                    border.color: borderSubtle

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 14

                                        Rectangle {
                                            Layout.preferredWidth: 44
                                            Layout.preferredHeight: 44
                                            radius: 6
                                            clip: true
                                            color: surfaceElevated

                                            Image {
                                                anchors.fill: parent
                                                source: modelData.cover_url || ""
                                                fillMode: Image.PreserveAspectCrop
                                            }
                                        }

                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: 4

                                            RowLayout {
                                                Layout.fillWidth: true
                                                Label {
                                                    Layout.fillWidth: true
                                                    text: modelData.title || "Downloading track"
                                                    font.family: displayFont
                                                    font.pixelSize: 13
                                                    font.weight: Font.Bold
                                                    color: textPrimary
                                                    elide: Text.ElideRight
                                                }
                                                Label {
                                                    text: modelData.speed ? (modelData.speed + (modelData.eta ? " • ETA " + modelData.eta : "")) : ""
                                                    font.family: monoFont
                                                    font.pixelSize: 10
                                                    color: silverDim
                                                }
                                            }

                                            // Progress Bar
                                            Rectangle {
                                                Layout.fillWidth: true
                                                Layout.preferredHeight: 4
                                                radius: 2
                                                color: surfaceElevated

                                                Rectangle {
                                                    width: parent.width * Math.max(0.02, Math.min(1.0, (modelData.percent || 0) / 100))
                                                    height: parent.height
                                                    radius: 2
                                                    color: modelData.status === "Failed" ? danger : (modelData.status === "Completed" ? success : recordRed)
                                                }
                                            }

                                            RowLayout {
                                                Layout.fillWidth: true
                                                Label {
                                                    text: modelData.artist || ""
                                                    font.family: bodyFont
                                                    font.pixelSize: 11
                                                    color: textSecondary
                                                }
                                                Item { Layout.fillWidth: true }
                                                Label {
                                                    text: modelData.status || "Queued"
                                                    font.family: monoFont
                                                    font.pixelSize: 10
                                                    color: modelData.status === "Completed" ? success : (modelData.status === "Failed" ? danger : textSecondary)
                                                }
                                            }
                                        }

                                        PressDepthIconButton {
                                            boxSize: 28
                                            iconSize: 12
                                            iconName: "x"
                                            tooltipText: "Cancel download"
                                            onClicked: if (downloaderBridge && modelData.id) downloaderBridge.cancelJob(modelData.id)
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Item {
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 28
                            anchors.rightMargin: 28
                            anchors.topMargin: 16
                            anchors.bottomMargin: 16
                            spacing: 14

                            RowLayout {
                                Layout.fillWidth: true
                                Label {
                                    text: "GrabSongs Library (" + window.downloadedFiles.length + " songs)"
                                    font.family: displayFont
                                    font.pixelSize: 18
                                    font.weight: Font.Bold
                                    color: textPrimary
                                }
                                Item { Layout.fillWidth: true }

                                // View Mode Toggle (Grid / List)
                                Rectangle {
                                    Layout.preferredHeight: 28
                                    Layout.preferredWidth: 64
                                    radius: 6
                                    color: surfaceCard
                                    border.width: 1
                                    border.color: borderSubtle

                                    RowLayout {
                                        anchors.fill: parent
                                        spacing: 0

                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                            radius: 6
                                            color: window.libraryViewMode === "grid" ? surfaceElevated : "transparent"
                                            LucideIcon {
                                                anchors.centerIn: parent
                                                width: 14
                                                height: 14
                                                icon: "grid-2x2"
                                                color: window.libraryViewMode === "grid" ? textPrimary : silverDim
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
                                            radius: 6
                                            color: window.libraryViewMode === "list" ? surfaceElevated : "transparent"
                                            LucideIcon {
                                                anchors.centerIn: parent
                                                width: 14
                                                height: 14
                                                icon: "list"
                                                color: window.libraryViewMode === "list" ? textPrimary : silverDim
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

                            // Empty State
                            Rectangle {
                                visible: window.downloadedFiles.length === 0
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: "transparent"

                                ColumnLayout {
                                    anchors.centerIn: parent
                                    spacing: 10
                                    LucideIcon {
                                        Layout.alignment: Qt.AlignHCenter
                                        width: 36
                                        height: 36
                                        icon: "disc"
                                        color: silverDim
                                    }
                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "GrabSongs library is empty"
                                        font.family: displayFont
                                        font.pixelSize: 16
                                        font.weight: Font.Bold
                                        color: textPrimary
                                    }
                                    Label {
                                        Layout.alignment: Qt.AlignHCenter
                                        text: "Downloaded songs will automatically show up here"
                                        font.family: bodyFont
                                        font.pixelSize: 12
                                        color: silverDim
                                    }
                                }
                            }

                            // Grid View (SongCard style)
                            GridView {
                                id: libGrid
                                visible: window.downloadedFiles.length > 0 && window.libraryViewMode === "grid"
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                cellWidth: 160
                                cellHeight: 220
                                model: window.downloadedFiles

                                delegate: Item {
                                    required property var modelData
                                    width: 150
                                    height: 210

                                    ColumnLayout {
                                        anchors.fill: parent
                                        spacing: 8

                                        Rectangle {
                                            Layout.preferredWidth: 144
                                            Layout.preferredHeight: 144
                                            radius: 10
                                            clip: true
                                            color: surfaceCard
                                            border.width: 1
                                            border.color: cardM.containsMouse ? borderVariant : borderSubtle

                                            LucideIcon {
                                                anchors.centerIn: parent
                                                width: 32
                                                height: 32
                                                icon: "music"
                                                color: silverDim
                                            }

                                            // Hover play button (PressDepthIconButton)
                                            Rectangle {
                                                visible: cardM.containsMouse || (downloaderBridge && downloaderBridge.currentPreviewPath === modelData.path)
                                                anchors.centerIn: parent
                                                width: 40
                                                height: 40
                                                radius: 20
                                                color: recordRed

                                                LucideIcon {
                                                    anchors.centerIn: parent
                                                    width: 16
                                                    height: 16
                                                    icon: (downloaderBridge && downloaderBridge.previewPlaying && downloaderBridge.currentPreviewPath === modelData.path) ? "pause" : "play"
                                                    color: "#FFFFFF"
                                                }
                                            }

                                            MouseArea {
                                                id: cardM
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    if (downloaderBridge) downloaderBridge.togglePreview(modelData.path)
                                                }
                                            }
                                        }

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
                                            text: modelData.artist || "GrabSongs"
                                            font.family: bodyFont
                                            font.pixelSize: 11
                                            color: textSecondary
                                            elide: Text.ElideRight
                                        }
                                    }
                                }
                            }

                            // List View (SongRow style)
                            ListView {
                                id: libList
                                visible: window.downloadedFiles.length > 0 && window.libraryViewMode === "list"
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                clip: true
                                spacing: 4
                                model: window.downloadedFiles

                                delegate: Rectangle {
                                    required property var modelData
                                    width: libList.width
                                    height: 52
                                    radius: 8
                                    color: lRowM.containsMouse ? surfaceElevated : "transparent"

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
                                            highlighted: (downloaderBridge && downloaderBridge.currentPreviewPath === modelData.path)
                                            tooltipText: "Play / Pause"
                                            onClicked: if (downloaderBridge) downloaderBridge.togglePreview(modelData.path)
                                        }

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
                                                text: modelData.artist || "GrabSongs"
                                                font.family: bodyFont
                                                font.pixelSize: 11
                                                color: textSecondary
                                                elide: Text.ElideRight
                                            }
                                        }

                                        Label {
                                            Layout.preferredWidth: 60
                                            text: modelData.size || ""
                                            font.family: monoFont
                                            font.pixelSize: 11
                                            color: silverDim
                                            horizontalAlignment: Text.AlignRight
                                        }

                                        PressDepthIconButton {
                                            boxSize: 30
                                            iconSize: 14
                                            iconName: "folder"
                                            tooltipText: "Reveal in Explorer"
                                            onClicked: if (downloaderBridge) downloaderBridge.revealFileInExplorer(modelData.path)
                                        }

                                        PressDepthIconButton {
                                            boxSize: 30
                                            iconSize: 14
                                            iconName: "x"
                                            tooltipText: "Delete file"
                                            hoverBackgroundColor: Qt.alpha(danger, 0.2)
                                            hoverBorderColor: danger
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

                    Item {
                        ScrollView {
                            anchors.fill: parent
                            anchors.leftMargin: 28
                            anchors.rightMargin: 28
                            anchors.topMargin: 16
                            anchors.bottomMargin: 16
                            contentWidth: width

                            ColumnLayout {
                                width: parent.width
                                spacing: 18

                                Label {
                                    text: "Downloader Preferences"
                                    font.family: displayFont
                                    font.pixelSize: 18
                                    font.weight: Font.Bold
                                    color: textPrimary
                                }

                                // Card 1: Format & Quality (SettingCard)
                                SettingCard {
                                    SettingRow {
                                        title: "Audio Output Format"
                                        subtitle: "Select preferred file container for downloaded tracks"
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

                                    SettingRow {
                                        title: "Audio Bitrate Quality"
                                        subtitle: "Constant high bitrate or lossless preservation"
                                        iconName: "audio-lines"

                                        Row {
                                            spacing: 6
                                            Repeater {
                                                model: [
                                                    { id: "320", label: "320 kbps (High)" },
                                                    { id: "256", label: "256 kbps" },
                                                    { id: "192", label: "192 kbps" }
                                                ]
                                                FilterChip {
                                                    required property var modelData
                                                    text: modelData.label
                                                    selected: (downloaderBridge ? downloaderBridge.audioQuality : "320") === modelData.id
                                                    onClicked: if (downloaderBridge) downloaderBridge.setAudioQuality(modelData.id)
                                                }
                                            }
                                        }
                                    }
                                }

                                // Card 2: Metadata & Lyrics (SettingCard)
                                SettingCard {
                                    SettingRow {
                                        title: "LRCLIB Synced Lyrics"
                                        subtitle: "Fetch and save matching synchronized lyrics (.lrc)"
                                        iconName: "quote"

                                        SettingSwitch {
                                            checked: downloaderBridge ? downloaderBridge.embedLyrics : true
                                            onToggled: if (downloaderBridge) downloaderBridge.setEmbedLyrics(checked)
                                        }
                                    }

                                    SettingRow {
                                        title: "Embed High-Res Artwork"
                                        subtitle: "Inject album cover into ID3v2 / Vorbis metadata"
                                        iconName: "disc"

                                        SettingSwitch {
                                            checked: downloaderBridge ? downloaderBridge.embedArtwork : true
                                            onToggled: if (downloaderBridge) downloaderBridge.setEmbedArtwork(checked)
                                        }
                                    }
                                }

                                // Card 3: Download Directory (SettingCard)
                                SettingCard {
                                    SettingRow {
                                        title: "GrabSongs Download Directory"
                                        subtitle: downloaderBridge ? downloaderBridge.downloadDirectory : "Music/GrabSongs"
                                        iconName: "folder"

                                        SettingButton {
                                            text: "Open Folder"
                                            iconName: "folder"
                                            onClicked: if (downloaderBridge) downloaderBridge.openDownloadFolder()
                                        }
                                    }
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
            height: 88
            color: surfaceDock

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
                        tooltipText: "Open GrabSongs Folder"
                        onClicked: if (downloaderBridge) downloaderBridge.openDownloadFolder()
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
