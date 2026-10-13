import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects
import "ThemeColors.js" as ThemeColors
import "TrackTitles.js" as TrackTitles

ApplicationWindow {
    id: window
    visible: true
    width: 1280
    height: 800
    minimumWidth: 900
    minimumHeight: 600
    title: "Harmonix • CassetteCat Multi-Platform Downloader"
    color: surfaceBase
    flags: Qt.Window | Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint

    // ==========================================
    // DESIGN SYSTEM TOKENS (DESIGN.md)
    // ==========================================
    readonly property color recordRed: "#C23B30"
    readonly property color recordRedHover: "#D64337"
    readonly property color surfaceDeep: "#0B0A09"
    readonly property color surfaceBase: "#0E0D0C"
    readonly property color surfaceSidebar: "#131211"
    readonly property color surfaceDock: "#151412"
    readonly property color surfaceCard: "#181715"
    readonly property color surfaceCardHover: "#22201D"
    readonly property color surfaceElevated: "#282623"
    readonly property color surfaceInput: "#1A1917"
    readonly property color surfaceSelected: "#252320"
    readonly property color surfaceTag: "#22201D"

    readonly property color textPrimary: "#F5F0EC"
    readonly property color textSecondary: "#A8A49E"
    readonly property color silverDim: "#918E88"
    readonly property color silver: "#C4C4C0"
    readonly property color danger: "#FF6B6B"
    readonly property color success: "#34D399"

    readonly property color borderSubtle: Qt.alpha(textPrimary, 0.05)
    readonly property color borderVariant: Qt.alpha(textPrimary, 0.09)
    readonly property color borderCard: borderVariant

    readonly property string displayFont: "Space Grotesk"
    readonly property string bodyFont: "IBM Plex Sans"
    readonly property string monoFont: "IBM Plex Mono"

    // Window navigation state
    property string page: "explore" // "explore", "queue", "library", "settings"
    property bool sidebarCollapsed: false
    readonly property real sidebarWidth: sidebarCollapsed ? 56 : 200
    property real albumArtRadius: 10
    property bool nowPlayingOpen: false
    property bool accessHintsVisible: false

    // App state
    property var searchResults: []
    property var queueJobs: []
    property var libraryTracks: []
    property int activeDownloads: 0
    property int completedDownloads: 0
    property string selectedService: "all"
    property string viewMode: "grid" // "grid" or "list"
    property bool isSearching: false
    property string searchErrorMsg: ""
    readonly property bool playerPlaying: (typeof player !== "undefined" && player) ? player.isPlaying : false
    readonly property var playerTrack: (typeof player !== "undefined" && player) ? player.currentTrack : ({})
    readonly property int playerPos: (typeof player !== "undefined" && player) ? player.position : 0
    readonly property int playerDur: (typeof player !== "undefined" && player) ? player.duration : 0
    readonly property real playerVol: (typeof player !== "undefined" && player) ? player.volume : 0.85

    // Format helper for seconds to mm:ss
    function formatTime(ms) {
        if (!ms || ms <= 0) return "0:00"
        const totalSec = Math.floor(ms / 1000)
        const mins = Math.floor(totalSec / 60)
        const secs = totalSec % 60
        return mins + ":" + (secs < 10 ? "0" : "") + secs
    }

    // Bridge connections
    Connections {
        target: bridge
        function onSearchStarted() {
            window.isSearching = true
            window.searchErrorMsg = ""
        }
        function onSearchResultsReady(results) {
            window.isSearching = false
            window.searchResults = results
            window.searchErrorMsg = results.length === 0 ? "No tracks found matching your query." : ""
        }
        function onSearchFailed(err) {
            window.isSearching = false
            window.searchErrorMsg = err
        }
        function onQueueUpdated(jobs) {
            window.queueJobs = jobs
        }
        function onActiveCountChanged(cnt) {
            window.activeDownloads = cnt
        }
        function onCompletedCountChanged(cnt) {
            window.completedDownloads = cnt
        }
        function onLibraryUpdated(tracks) {
            window.libraryTracks = tracks
        }
    }

    Component.onCompleted: {
        bridge.refreshLibrary()
    }

    // ==========================================
    // TOP BAR / TITLE BAR (60px)
    // ==========================================
    Rectangle {
        id: titleBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 60
        color: surfaceSidebar
        z: 200

        Rectangle {
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            height: 1
            color: borderSubtle
        }

        // Window drag area
        DragHandler {
            target: null
            onActiveChanged: if (active) window.startSystemMove()
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 16
            anchors.rightMargin: 0
            spacing: 12

            // Logo & Title
            RowLayout {
                spacing: 12
                Layout.alignment: Qt.AlignVCenter

                Image {
                    source: Qt.resolvedUrl("../assets/cassettecat_icon.png")
                    Layout.preferredWidth: 28
                    Layout.preferredHeight: 28
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                }

                Label {
                    text: page === "explore" ? "Explore & Download" :
                          page === "queue" ? "Download Queue" :
                          page === "library" ? "Harmonix Library" : "Settings"
                    color: textPrimary
                    font.family: displayFont
                    font.pixelSize: 18
                    font.weight: Font.Bold
                    font.letterSpacing: -0.3
                }

                Rectangle {
                    visible: window.activeDownloads > 0
                    Layout.preferredHeight: 20
                    radius: 10
                    color: recordRed
                    implicitWidth: dlCountLabel.implicitWidth + 14

                    Label {
                        id: dlCountLabel
                        anchors.centerIn: parent
                        text: window.activeDownloads + " active"
                        color: "#FFFFFF"
                        font.family: monoFont
                        font.pixelSize: 10
                        font.weight: Font.Bold
                    }
                }
            }

            Item { Layout.fillWidth: true }

            // Window caption buttons (Minimize, Maximize, Close)
            Row {
                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                spacing: 0

                // Minimize button
                Rectangle {
                    width: 48
                    height: 60
                    color: minMouse.containsMouse ? surfaceElevated : "transparent"

                    Rectangle {
                        anchors.centerIn: parent
                        width: 10
                        height: 1.5
                        color: minMouse.containsMouse ? textPrimary : silverDim
                    }

                    MouseArea {
                        id: minMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.ArrowCursor
                        onClicked: window.showMinimized()
                    }
                }

                // Maximize button
                Rectangle {
                    width: 48
                    height: 60
                    color: maxMouse.containsMouse ? surfaceElevated : "transparent"

                    Rectangle {
                        anchors.centerIn: parent
                        width: 10
                        height: 10
                        color: "transparent"
                        border.width: 1.2
                        border.color: maxMouse.containsMouse ? textPrimary : silverDim
                        radius: 1
                    }

                    MouseArea {
                        id: maxMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.ArrowCursor
                        onClicked: {
                            if (window.visibility === Window.Maximized)
                                window.showNormal()
                            else
                                window.showMaximized()
                        }
                    }
                }

                // Close button
                Rectangle {
                    width: 48
                    height: 60
                    color: closeMouse.containsMouse ? "#E53935" : "transparent"

                    LucideIcon {
                        anchors.centerIn: parent
                        width: 14
                        height: 14
                        icon: "x"
                        color: closeMouse.containsMouse ? "#FFFFFF" : silverDim
                    }

                    MouseArea {
                        id: closeMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.ArrowCursor
                        onClicked: window.close()
                    }
                }
            }
        }
    }

    // ==========================================
    // BODY AREA (Sidebar + Pages)
    // ==========================================
    Item {
        id: bodyArea
        anchors.top: titleBar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: playerDock.top

        // ------------------------------------------
        // LEFT SIDEBAR (NavRail)
        // ------------------------------------------
        Rectangle {
            id: sidebarPanel
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            width: window.sidebarWidth
            color: surfaceSidebar
            z: 50

            Behavior on width { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }

            Rectangle {
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                width: 1
                color: borderSubtle
            }

            Column {
                anchors.top: parent.top
                anchors.topMargin: 12
                anchors.left: parent.left
                anchors.right: parent.right
                spacing: 4

                NavItem {
                    appWindow: window
                    sidebarWidth: sidebarPanel.width
                    sidebarCollapsed: window.sidebarCollapsed
                    destination: "explore"
                    iconName: "search"
                    label: "Explore & Search"
                }

                NavItem {
                    appWindow: window
                    sidebarWidth: sidebarPanel.width
                    sidebarCollapsed: window.sidebarCollapsed
                    destination: "queue"
                    iconName: "arrow-down"
                    label: "Download Queue"
                }

                NavItem {
                    appWindow: window
                    sidebarWidth: sidebarPanel.width
                    sidebarCollapsed: window.sidebarCollapsed
                    destination: "library"
                    iconName: "music"
                    label: "Local Library"
                }
            }

            // Bottom Settings & Collapse toggle
            Column {
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 12
                anchors.left: parent.left
                anchors.right: parent.right
                spacing: 4

                NavItem {
                    appWindow: window
                    sidebarWidth: sidebarPanel.width
                    sidebarCollapsed: window.sidebarCollapsed
                    destination: "settings"
                    iconName: "settings"
                    label: "Settings"
                }

                // Collapse sidebar button
                Item {
                    width: sidebarPanel.width
                    height: 40

                    Rectangle {
                        anchors.centerIn: parent
                        width: window.sidebarCollapsed ? 44 : 180
                        height: 40
                        radius: 8
                        color: collapseMouse.containsMouse ? surfaceCardHover : "transparent"

                        LucideIcon {
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: parent.left
                            anchors.leftMargin: window.sidebarCollapsed ? 12 : 14
                            width: 20
                            height: 20
                            icon: "panel-left"
                            color: collapseMouse.containsMouse ? textPrimary : silverDim
                        }

                        Label {
                            anchors.left: parent.left
                            anchors.leftMargin: 46
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Collapse"
                            color: collapseMouse.containsMouse ? textPrimary : textSecondary
                            font.family: displayFont
                            font.pixelSize: 13
                            visible: !window.sidebarCollapsed
                        }

                        MouseArea {
                            id: collapseMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: window.sidebarCollapsed = !window.sidebarCollapsed
                        }
                    }
                }
            }
        }

        // ------------------------------------------
        // MAIN PAGES CONTAINER
        // ------------------------------------------
        Item {
            id: contentContainer
            anchors.top: parent.top
            anchors.left: sidebarPanel.right
            anchors.right: parent.right
            anchors.bottom: parent.bottom

            // ----------------------------------------------------
            // PAGE 1: EXPLORE / SEARCH
            // ----------------------------------------------------
            Flickable {
                id: explorePage
                visible: window.page === "explore"
                anchors.fill: parent
                contentWidth: width
                contentHeight: exploreColumn.implicitHeight + 40
                clip: true
                boundsBehavior: Flickable.StopAtBounds

                ColumnLayout {
                    id: exploreColumn
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: 28
                    spacing: 20

                    // Hero Banner Header
                    ColumnLayout {
                        spacing: 4
                        Layout.fillWidth: true

                        Label {
                            text: "MULTI-PLATFORM ENGINE • RECORD RED"
                            color: recordRedHover
                            font.family: monoFont
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            font.letterSpacing: 1.2
                        }

                        Label {
                            text: "Explore and download any music"
                            color: textPrimary
                            font.family: displayFont
                            font.pixelSize: 28
                            font.weight: Font.Bold
                            font.letterSpacing: -0.5
                        }

                        Label {
                            text: "Spotify • Apple Music • Deezer • YouTube • Lossless FLAC & Synced Lyrics"
                            color: textSecondary
                            font.family: bodyFont
                            font.pixelSize: 13
                        }
                    }

                    // Search Card
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 110
                        radius: 12
                        color: surfaceCard
                        border.width: 1
                        border.color: borderCard

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 10

                            // Filter Chips Row
                            RowLayout {
                                spacing: 8

                                FilterChip {
                                    text: "All Platforms"
                                    iconName: "globe"
                                    selected: window.selectedService === "all"
                                    onClicked: window.selectedService = "all"
                                }
                                FilterChip {
                                    text: "Spotify"
                                    iconName: "simpleicons"
                                    selected: window.selectedService === "spotify"
                                    onClicked: window.selectedService = "spotify"
                                }
                                FilterChip {
                                    text: "Apple Music"
                                    iconName: "music"
                                    selected: window.selectedService === "apple_music"
                                    onClicked: window.selectedService = "apple_music"
                                }
                                FilterChip {
                                    text: "Deezer"
                                    iconName: "zap"
                                    selected: window.selectedService === "deezer"
                                    onClicked: window.selectedService = "deezer"
                                }
                                FilterChip {
                                    text: "YouTube"
                                    iconName: "play"
                                    selected: window.selectedService === "youtube"
                                    onClicked: window.selectedService = "youtube"
                                }
                            }

                            // Search Input & Action Buttons
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 10

                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 40
                                    radius: 8
                                    color: surfaceInput
                                    border.width: 1
                                    border.color: searchInput.activeFocus ? recordRed : borderSubtle

                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.leftMargin: 12
                                        anchors.rightMargin: 12
                                        spacing: 10

                                        LucideIcon {
                                            Layout.preferredWidth: 16
                                            Layout.preferredHeight: 16
                                            icon: "search"
                                            color: silverDim
                                        }

                                        TextInput {
                                            id: searchInput
                                            Layout.fillWidth: true
                                            color: textPrimary
                                            font.family: bodyFont
                                            font.pixelSize: 13
                                            verticalAlignment: TextInput.AlignVCenter
                                            selectByMouse: true
                                            clip: true
                                            Keys.onReturnPressed: bridge.search(searchInput.text, window.selectedService)

                                            Text {
                                                text: "Paste Spotify/Apple Music/Deezer/YouTube URL, or search track, album, artist..."
                                                color: silverDim
                                                font.family: bodyFont
                                                font.pixelSize: 13
                                                visible: !searchInput.text && !searchInput.activeFocus
                                                anchors.verticalCenter: parent.verticalCenter
                                            }
                                        }

                                        // Paste Button
                                        Rectangle {
                                            Layout.preferredHeight: 28
                                            implicitWidth: pasteLabel.implicitWidth + 20
                                            radius: 6
                                            color: pasteMouse.containsMouse ? surfaceCardHover : "transparent"
                                            border.width: 1
                                            border.color: borderSubtle

                                            RowLayout {
                                                anchors.centerIn: parent
                                                spacing: 4

                                                LucideIcon {
                                                    Layout.preferredWidth: 12
                                                    Layout.preferredHeight: 12
                                                    icon: "link"
                                                    color: silverDim
                                                }

                                                Label {
                                                    id: pasteLabel
                                                    text: "Paste"
                                                    color: textSecondary
                                                    font.family: monoFont
                                                    font.pixelSize: 11
                                                }
                                            }

                                            MouseArea {
                                                id: pasteMouse
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                                    searchInput.paste()
                                                    if (searchInput.text.trim().length > 0)
                                                        bridge.search(searchInput.text, window.selectedService)
                                                }
                                            }
                                        }
                                    }
                                }

                                // Explore / Search Trigger Button
                                Rectangle {
                                    Layout.preferredHeight: 40
                                    implicitWidth: searchBtnLabel.implicitWidth + 36
                                    radius: 8
                                    color: searchBtnMouse.containsMouse ? recordRedHover : recordRed

                                    RowLayout {
                                        anchors.centerIn: parent
                                        spacing: 8

                                        LucideIcon {
                                            Layout.preferredWidth: 16
                                            Layout.preferredHeight: 16
                                            icon: "search"
                                            color: "#FFFFFF"
                                        }

                                        Label {
                                            id: searchBtnLabel
                                            text: "Explore"
                                            color: "#FFFFFF"
                                            font.family: displayFont
                                            font.pixelSize: 13
                                            font.weight: Font.DemiBold
                                        }
                                    }

                                    MouseArea {
                                        id: searchBtnMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: bridge.search(searchInput.text, window.selectedService)
                                    }
                                }
                            }
                        }
                    }

                    // Loading indicator
                    LoadingBar {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 3
                        visible: window.isSearching
                    }

                    // Error message label
                    Label {
                        visible: window.searchErrorMsg.length > 0
                        text: window.searchErrorMsg
                        color: danger
                        font.family: bodyFont
                        font.pixelSize: 12
                    }

                    // Results Header Action Bar
                    RowLayout {
                        Layout.fillWidth: true
                        visible: window.searchResults.length > 0

                        Label {
                            text: window.searchResults.length + " tracks found"
                            color: textPrimary
                            font.family: displayFont
                            font.pixelSize: 16
                            font.weight: Font.Bold
                        }

                        Item { Layout.fillWidth: true }

                        // View mode toggle
                        Row {
                            spacing: 4

                            Rectangle {
                                width: 32
                                height: 32
                                radius: 6
                                color: window.viewMode === "grid" ? surfaceSelected : "transparent"
                                border.width: 1
                                border.color: window.viewMode === "grid" ? recordRed : borderSubtle

                                LucideIcon {
                                    anchors.centerIn: parent
                                    width: 16
                                    height: 16
                                    icon: "grid-2x2"
                                    color: window.viewMode === "grid" ? recordRedHover : silverDim
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: window.viewMode = "grid"
                                }
                            }

                            Rectangle {
                                width: 32
                                height: 32
                                radius: 6
                                color: window.viewMode === "list" ? surfaceSelected : "transparent"
                                border.width: 1
                                border.color: window.viewMode === "list" ? recordRed : borderSubtle

                                LucideIcon {
                                    anchors.centerIn: parent
                                    width: 16
                                    height: 16
                                    icon: "list"
                                    color: window.viewMode === "list" ? recordRedHover : silverDim
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: window.viewMode = "list"
                                }
                            }
                        }

                        // Download All Button
                        Rectangle {
                            Layout.preferredHeight: 32
                            implicitWidth: dlAllLabel.implicitWidth + 28
                            radius: 16
                            color: dlAllMouse.containsMouse ? recordRedHover : recordRed

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 6

                                LucideIcon {
                                    Layout.preferredWidth: 14
                                    Layout.preferredHeight: 14
                                    icon: "arrow-down"
                                    color: "#FFFFFF"
                                }

                                Label {
                                    id: dlAllLabel
                                    text: "Download All"
                                    color: "#FFFFFF"
                                    font.family: monoFont
                                    font.pixelSize: 11
                                    font.weight: Font.Bold
                                }
                            }

                            MouseArea {
                                id: dlAllMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: bridge.downloadAll(window.searchResults)
                            }
                        }
                    }

                    // GRID VIEW OF CARDS
                    GridLayout {
                        id: resultsGrid
                        Layout.fillWidth: true
                        columns: Math.max(2, Math.floor((contentContainer.width - 56) / 190))
                        rowSpacing: 16
                        columnSpacing: 16
                        visible: window.viewMode === "grid" && window.searchResults.length > 0

                        Repeater {
                            model: window.searchResults

                            SongCard {
                                required property var modelData
                                track: modelData
                                cardWidth: 176
                                cardHeight: 236
                                onDownloadClicked: bridge.downloadTrack(modelData)
                                onClicked: player.playTrack(modelData)
                            }
                        }
                    }

                    // LIST VIEW OF ROWS
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        visible: window.viewMode === "list" && window.searchResults.length > 0

                        Repeater {
                            model: window.searchResults

                            SongRow {
                                required property var modelData
                                required property int index
                                Layout.fillWidth: true
                                track: modelData
                                number: index + 1
                                onDownloadClicked: bridge.downloadTrack(modelData)
                                onClicked: player.playTrack(modelData)
                            }
                        }
                    }

                    // Welcome / Empty State Card
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 220
                        radius: 12
                        color: surfaceCard
                        border.width: 1
                        border.color: borderCard
                        visible: window.searchResults.length === 0 && !window.isSearching

                        ColumnLayout {
                            anchors.centerIn: parent
                            spacing: 12

                            Rectangle {
                                Layout.alignment: Qt.AlignHCenter
                                width: 56
                                height: 56
                                radius: 28
                                color: surfaceElevated

                                LucideIcon {
                                    anchors.centerIn: parent
                                    width: 28
                                    height: 28
                                    icon: "disc"
                                    color: recordRedHover
                                }
                            }

                            Label {
                                Layout.alignment: Qt.AlignHCenter
                                text: "CassetteCat Universal Downloader"
                                color: textPrimary
                                font.family: displayFont
                                font.pixelSize: 18
                                font.weight: Font.Bold
                            }

                            Label {
                                Layout.alignment: Qt.AlignHCenter
                                text: "Paste Spotify, Apple Music, Deezer, or YouTube links directly to extract full discographies with 320kbps audio, synced lyrics, and high-res cover art."
                                color: textSecondary
                                font.family: bodyFont
                                font.pixelSize: 13
                                horizontalAlignment: Text.AlignHCenter
                                Layout.preferredWidth: Math.min(500, contentContainer.width - 80)
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                }
            }

            // ----------------------------------------------------
            // PAGE 2: DOWNLOAD QUEUE
            // ----------------------------------------------------
            Flickable {
                id: queuePage
                visible: window.page === "queue"
                anchors.fill: parent
                contentWidth: width
                contentHeight: queueCol.implicitHeight + 40
                clip: true
                boundsBehavior: Flickable.StopAtBounds

                ColumnLayout {
                    id: queueCol
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: 28
                    spacing: 20

                    // Header & Summary Stats
                    RowLayout {
                        Layout.fillWidth: true

                        ColumnLayout {
                            spacing: 2

                            Label {
                                text: "Download Manager"
                                color: textPrimary
                                font.family: displayFont
                                font.pixelSize: 24
                                font.weight: Font.Bold
                            }

                            Label {
                                text: window.activeDownloads + " active • " + window.completedDownloads + " completed"
                                color: silverDim
                                font.family: monoFont
                                font.pixelSize: 12
                            }
                        }

                        Item { Layout.fillWidth: true }

                        Rectangle {
                            Layout.preferredHeight: 34
                            implicitWidth: cancelAllLabel.implicitWidth + 24
                            radius: 8
                            color: cancelMouse.containsMouse ? surfaceElevated : surfaceCard
                            border.width: 1
                            border.color: borderCard

                            Label {
                                id: cancelAllLabel
                                anchors.centerIn: parent
                                text: "Cancel All"
                                color: danger
                                font.family: monoFont
                                font.pixelSize: 11
                                font.weight: Font.Bold
                            }

                            MouseArea {
                                id: cancelMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: bridge.cancelAll()
                            }
                        }
                    }

                    // Jobs list
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Repeater {
                            model: window.queueJobs

                            Rectangle {
                                required property var modelData
                                Layout.fillWidth: true
                                Layout.preferredHeight: 74
                                radius: 10
                                color: surfaceCard
                                border.width: 1
                                border.color: borderCard

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 12
                                    spacing: 14

                                    // Thumbnail
                                    Rectangle {
                                        Layout.preferredWidth: 50
                                        Layout.preferredHeight: 50
                                        radius: 8
                                        color: surfaceElevated
                                        clip: true

                                        Cover {
                                            anchors.fill: parent
                                            track: modelData
                                            radius: 8
                                        }
                                    }

                                    // Title & Artist
                                    ColumnLayout {
                                        Layout.preferredWidth: 220
                                        Layout.minimumWidth: 180
                                        spacing: 2

                                        Label {
                                            Layout.fillWidth: true
                                            text: modelData.title
                                            color: textPrimary
                                            font.family: displayFont
                                            font.pixelSize: 13
                                            font.weight: Font.Bold
                                            elide: Text.ElideRight
                                        }

                                        Label {
                                            Layout.fillWidth: true
                                            text: modelData.artist
                                            color: textSecondary
                                            font.family: bodyFont
                                            font.pixelSize: 11
                                            elide: Text.ElideRight
                                        }
                                    }

                                    // Progress bar & Status
                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 6

                                        RowLayout {
                                            Layout.fillWidth: true

                                            Rectangle {
                                                Layout.preferredHeight: 18
                                                radius: 4
                                                color: modelData.status === "Completed" ? Qt.alpha(success, 0.15) :
                                                       modelData.status === "Cancelled" ? Qt.alpha(danger, 0.15) :
                                                       surfaceSelected
                                                border.width: 1
                                                border.color: modelData.status === "Completed" ? success :
                                                              modelData.status === "Cancelled" ? danger : recordRed
                                                implicitWidth: stLabel.implicitWidth + 10

                                                Label {
                                                    id: stLabel
                                                    anchors.centerIn: parent
                                                    text: modelData.status.toUpperCase()
                                                    color: modelData.status === "Completed" ? success :
                                                           modelData.status === "Cancelled" ? danger : recordRedHover
                                                    font.family: monoFont
                                                    font.pixelSize: 9
                                                    font.weight: Font.Bold
                                                }
                                            }

                                            Label {
                                                text: modelData.speed ? modelData.speed + " • ETA: " + modelData.eta : ""
                                                color: silverDim
                                                font.family: monoFont
                                                font.pixelSize: 11
                                                visible: modelData.speed.length > 0
                                            }

                                            Item { Layout.fillWidth: true }

                                            Label {
                                                text: Math.round(modelData.percent) + "%"
                                                color: textPrimary
                                                font.family: monoFont
                                                font.pixelSize: 12
                                                font.weight: Font.Bold
                                            }
                                        }

                                        // Progress Bar Track
                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 5
                                            radius: 2.5
                                            color: surfaceElevated

                                            Rectangle {
                                                width: parent.width * (Math.max(0, Math.min(100, modelData.percent)) / 100.0)
                                                height: parent.height
                                                radius: 2.5
                                                color: modelData.status === "Completed" ? success : recordRed
                                            }
                                        }
                                    }

                                    // Action button
                                    Rectangle {
                                        Layout.preferredWidth: 32
                                        Layout.preferredHeight: 32
                                        radius: 16
                                        color: actMouse.containsMouse ? surfaceElevated : "transparent"

                                        LucideIcon {
                                            anchors.centerIn: parent
                                            width: 14
                                            height: 14
                                            icon: modelData.status === "Completed" ? "folder" : "x"
                                            color: modelData.status === "Completed" ? textSecondary : danger
                                        }

                                        MouseArea {
                                            id: actMouse
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                if (modelData.status === "Completed")
                                                    bridge.openFolder(modelData.filePath)
                                                else
                                                    bridge.cancelJob(modelData.id)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Empty Queue State
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 180
                        radius: 12
                        color: surfaceCard
                        border.width: 1
                        border.color: borderCard
                        visible: window.queueJobs.length === 0

                        ColumnLayout {
                            anchors.centerIn: parent
                            spacing: 8

                            LucideIcon {
                                Layout.alignment: Qt.AlignHCenter
                                width: 28
                                height: 28
                                icon: "arrow-down"
                                color: silverDim
                            }

                            Label {
                                Layout.alignment: Qt.AlignHCenter
                                text: "No active downloads"
                                color: textPrimary
                                font.family: displayFont
                                font.pixelSize: 15
                                font.weight: Font.DemiBold
                            }

                            Label {
                                Layout.alignment: Qt.AlignHCenter
                                text: "Songs added to download will appear here with live speed and progress."
                                color: textSecondary
                                font.family: bodyFont
                                font.pixelSize: 12
                            }
                        }
                    }
                }
            }

            // ----------------------------------------------------
            // PAGE 3: DOWNLOADED LIBRARY
            // ----------------------------------------------------
            Flickable {
                id: libraryPage
                visible: window.page === "library"
                anchors.fill: parent
                contentWidth: width
                contentHeight: libCol.implicitHeight + 40
                clip: true
                boundsBehavior: Flickable.StopAtBounds

                ColumnLayout {
                    id: libCol
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: 28
                    spacing: 20

                    RowLayout {
                        Layout.fillWidth: true

                        ColumnLayout {
                            spacing: 2

                            Label {
                                text: "Downloaded Tracks"
                                color: textPrimary
                                font.family: displayFont
                                font.pixelSize: 24
                                font.weight: Font.Bold
                            }

                            Label {
                                text: window.libraryTracks.length + " songs in Harmonix Library"
                                color: silverDim
                                font.family: monoFont
                                font.pixelSize: 12
                            }
                        }

                        Item { Layout.fillWidth: true }

                        Rectangle {
                            Layout.preferredHeight: 34
                            implicitWidth: openFolderLabel.implicitWidth + 30
                            radius: 8
                            color: openFolderMouse.containsMouse ? surfaceElevated : surfaceCard
                            border.width: 1
                            border.color: borderCard

                            RowLayout {
                                anchors.centerIn: parent
                                spacing: 6

                                LucideIcon {
                                    Layout.preferredWidth: 14
                                    Layout.preferredHeight: 14
                                    icon: "folder"
                                    color: textSecondary
                                }

                                Label {
                                    id: openFolderLabel
                                    text: "Open Folder"
                                    color: textPrimary
                                    font.family: displayFont
                                    font.pixelSize: 12
                                    font.weight: Font.Medium
                                }
                            }

                            MouseArea {
                                id: openFolderMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: bridge.openFolder()
                            }
                        }
                    }

                    // Songs Grid / List
                    GridLayout {
                        Layout.fillWidth: true
                        columns: Math.max(2, Math.floor((contentContainer.width - 56) / 190))
                        rowSpacing: 16
                        columnSpacing: 16
                        visible: window.libraryTracks.length > 0

                        Repeater {
                            model: window.libraryTracks

                            SongCard {
                                required property var modelData
                                track: modelData
                                cardWidth: 176
                                cardHeight: 236
                                onClicked: player.playTrack(modelData)
                            }
                        }
                    }

                    // Empty Library State
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 180
                        radius: 12
                        color: surfaceCard
                        border.width: 1
                        border.color: borderCard
                        visible: window.libraryTracks.length === 0

                        ColumnLayout {
                            anchors.centerIn: parent
                            spacing: 8

                            LucideIcon {
                                Layout.alignment: Qt.AlignHCenter
                                width: 28
                                height: 28
                                icon: "music"
                                color: silverDim
                            }

                            Label {
                                Layout.alignment: Qt.AlignHCenter
                                text: "No songs downloaded yet"
                                color: textPrimary
                                font.family: displayFont
                                font.pixelSize: 15
                                font.weight: Font.DemiBold
                            }

                            Label {
                                Layout.alignment: Qt.AlignHCenter
                                text: "Head over to Explore to download songs, full albums, or playlists."
                                color: textSecondary
                                font.family: bodyFont
                                font.pixelSize: 12
                            }
                        }
                    }
                }
            }

            // ----------------------------------------------------
            // PAGE 4: SETTINGS
            // ----------------------------------------------------
            Flickable {
                id: settingsPage
                visible: window.page === "settings"
                anchors.fill: parent
                contentWidth: width
                contentHeight: settCol.implicitHeight + 40
                clip: true
                boundsBehavior: Flickable.StopAtBounds

                ColumnLayout {
                    id: settCol
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: 28
                    spacing: 20

                    Label {
                        text: "Preferences & Audio Quality"
                        color: textPrimary
                        font.family: displayFont
                        font.pixelSize: 24
                        font.weight: Font.Bold
                    }

                    // Settings Cards
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 80
                        radius: 10
                        color: surfaceCard
                        border.width: 1
                        border.color: borderCard

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 16

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2

                                Label {
                                    text: "Download Directory"
                                    color: textPrimary
                                    font.family: displayFont
                                    font.pixelSize: 14
                                    font.weight: Font.DemiBold
                                }

                                Label {
                                    text: "C:\\Users\\ladsa\\Music\\Harmonix"
                                    color: silverDim
                                    font.family: monoFont
                                    font.pixelSize: 11
                                }
                            }

                            Rectangle {
                                Layout.preferredHeight: 32
                                implicitWidth: 100
                                radius: 6
                                color: surfaceElevated
                                border.width: 1
                                border.color: borderSubtle

                                Label {
                                    anchors.centerIn: parent
                                    text: "Open Folder"
                                    color: textPrimary
                                    font.family: monoFont
                                    font.pixelSize: 11
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    cursorShape: Qt.PointingHandCursor
                                    onClicked: bridge.openFolder()
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 80
                        radius: 10
                        color: surfaceCard
                        border.width: 1
                        border.color: borderCard

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 16

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2

                                Label {
                                    text: "Preferred Audio Codec & Bitrate"
                                    color: textPrimary
                                    font.family: displayFont
                                    font.pixelSize: 14
                                    font.weight: Font.DemiBold
                                }

                                Label {
                                    text: "320 kbps High Quality MP3 (Transcoded via FFmpeg)"
                                    color: silverDim
                                    font.family: bodyFont
                                    font.pixelSize: 12
                                }
                            }

                            Rectangle {
                                Layout.preferredHeight: 28
                                implicitWidth: 90
                                radius: 14
                                color: surfaceSelected
                                border.width: 1
                                border.color: recordRed

                                Label {
                                    anchors.centerIn: parent
                                    text: "MP3 320K"
                                    color: recordRedHover
                                    font.family: monoFont
                                    font.pixelSize: 11
                                    font.weight: Font.Bold
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 80
                        radius: 10
                        color: surfaceCard
                        border.width: 1
                        border.color: borderCard

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 16

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2

                                Label {
                                    text: "Synchronized Lyrics (LRCLIB)"
                                    color: textPrimary
                                    font.family: displayFont
                                    font.pixelSize: 14
                                    font.weight: Font.DemiBold
                                }

                                Label {
                                    text: "Automatically fetch and save timestamped .lrc files alongside songs"
                                    color: silverDim
                                    font.family: bodyFont
                                    font.pixelSize: 12
                                }
                            }

                            Rectangle {
                                Layout.preferredHeight: 26
                                implicitWidth: 60
                                radius: 13
                                color: Qt.alpha(success, 0.15)
                                border.width: 1
                                border.color: success

                                Label {
                                    anchors.centerIn: parent
                                    text: "ENABLED"
                                    color: success
                                    font.family: monoFont
                                    font.pixelSize: 10
                                    font.weight: Font.Bold
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // ==========================================
    // BOTTOM PLAYER DOCK (88px)
    // ==========================================
    Rectangle {
        id: playerDock
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 88
        color: surfaceDock
        z: 200

        Rectangle {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 1
            color: borderSubtle
        }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 20
            anchors.rightMargin: 20
            spacing: 20

            // Left: Current Track Thumbnail & Metadata
            RowLayout {
                Layout.preferredWidth: 320
                Layout.maximumWidth: 340
                spacing: 12

                Rectangle {
                    Layout.preferredWidth: 52
                    Layout.preferredHeight: 52
                    radius: 8
                    color: surfaceCard
                    border.width: 1
                    border.color: borderVariant
                    clip: true

                    Cover {
                        anchors.fill: parent
                        track: window.playerTrack
                        radius: parent.radius
                        visible: !!(window.playerTrack && (window.playerTrack.artworkUrl || window.playerTrack.filePath))
                    }

                    LucideIcon {
                        anchors.centerIn: parent
                        width: 24
                        height: 24
                        icon: "music"
                        color: silverDim
                        visible: !window.playerTrack || (!window.playerTrack.artworkUrl && !window.playerTrack.filePath)
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Label {
                        Layout.fillWidth: true
                        text: window.playerTrack && window.playerTrack.title ? window.playerTrack.title : "No track playing"
                        color: textPrimary
                        font.family: displayFont
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                        elide: Text.ElideRight
                    }

                    Label {
                        Layout.fillWidth: true
                        text: window.playerTrack && window.playerTrack.artist ? window.playerTrack.artist : "CassetteCat Engine"
                        color: textSecondary
                        font.family: bodyFont
                        font.pixelSize: 11
                        elide: Text.ElideRight
                    }
                }
            }

            // Center: Playback Controls & Timeline
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4

                // Transport Controls
                Row {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 16

                    // Shuffle
                    Rectangle {
                        width: 28
                        height: 28
                        radius: 14
                        color: "transparent"
                        anchors.verticalCenter: parent.verticalCenter

                        LucideIcon {
                            anchors.centerIn: parent
                            width: 14
                            height: 14
                            icon: "shuffle"
                            color: silverDim
                        }
                    }

                    // Previous
                    Rectangle {
                        width: 32
                        height: 32
                        radius: 16
                        color: prevMouse.containsMouse ? surfaceElevated : "transparent"
                        anchors.verticalCenter: parent.verticalCenter

                        LucideIcon {
                            anchors.centerIn: parent
                            width: 16
                            height: 16
                            icon: "skip-back"
                            color: prevMouse.containsMouse ? textPrimary : silverDim
                        }

                        MouseArea {
                            id: prevMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: player.seek(0)
                        }
                    }

                    // Play/Pause Circular Button
                    Rectangle {
                        width: 42
                        height: 42
                        radius: 21
                        color: playMouse.containsMouse ? recordRedHover : recordRed
                        anchors.verticalCenter: parent.verticalCenter

                        LucideIcon {
                            anchors.centerIn: parent
                            width: 18
                            height: 18
                            icon: window.playerPlaying ? "pause" : "play"
                            color: "#FFFFFF"
                        }

                        MouseArea {
                            id: playMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: player.togglePlay()
                        }
                    }

                    // Next
                    Rectangle {
                        width: 32
                        height: 32
                        radius: 16
                        color: nextMouse.containsMouse ? surfaceElevated : "transparent"
                        anchors.verticalCenter: parent.verticalCenter

                        LucideIcon {
                            anchors.centerIn: parent
                            width: 16
                            height: 16
                            icon: "skip-forward"
                            color: nextMouse.containsMouse ? textPrimary : silverDim
                        }

                        MouseArea {
                            id: nextMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                        }
                    }

                    // Repeat
                    Rectangle {
                        width: 28
                        height: 28
                        radius: 14
                        color: "transparent"
                        anchors.verticalCenter: parent.verticalCenter

                        LucideIcon {
                            anchors.centerIn: parent
                            width: 14
                            height: 14
                            icon: "repeat"
                            color: silverDim
                        }
                    }
                }

                // Timeline Seekbar & Timestamps
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Label {
                        text: window.formatTime(window.playerPos)
                        color: silverDim
                        font.family: monoFont
                        font.pixelSize: 11
                    }

                    // Razor thin seek slider
                    Rectangle {
                        id: seekTrack
                        Layout.fillWidth: true
                        Layout.preferredHeight: 4
                        radius: 2
                        color: surfaceElevated

                        Rectangle {
                            height: parent.height
                            radius: 2
                            color: recordRed
                            width: window.playerDur > 0 ? (parent.width * (window.playerPos / window.playerDur)) : 0
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: mouse => {
                                if (window.playerDur > 0) {
                                    const fraction = mouse.x / seekTrack.width
                                    player.seek(Math.floor(fraction * window.playerDur))
                                }
                            }
                        }
                    }

                    Label {
                        text: window.formatTime(window.playerDur)
                        color: silverDim
                        font.family: monoFont
                        font.pixelSize: 11
                    }
                }
            }

            // Right: Volume & Extras
            RowLayout {
                Layout.preferredWidth: 200
                spacing: 12

                LucideIcon {
                    Layout.preferredWidth: 16
                    Layout.preferredHeight: 16
                    icon: window.playerVol === 0 ? "volume-x" : "volume-2"
                    color: silverDim
                }

                Rectangle {
                    id: volumeTrack
                    Layout.fillWidth: true
                    Layout.preferredHeight: 4
                    radius: 2
                    color: surfaceElevated

                    Rectangle {
                        height: parent.height
                        radius: 2
                        color: recordRed
                        width: parent.width * window.playerVol
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: mouse => {
                            const fraction = Math.max(0.0, Math.min(1.0, mouse.x / volumeTrack.width))
                            player.setVolume(fraction)
                        }
                    }
                }

                Label {
                    text: Math.round(window.playerVol * 100) + "%"
                    color: silverDim
                    font.family: monoFont
                    font.pixelSize: 11
                    Layout.preferredWidth: 32
                }
            }
        }
    }
}
