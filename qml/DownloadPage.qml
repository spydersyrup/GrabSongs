import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    required property var appWindow
    required property var downloaderBridge
    required property var libraryModel
    required property var playerController

    anchors.fill: parent

    property string currentTab: "explore"
    property string activeService: "all"
    property var searchResults: []
    property bool isSearching: false
    property string searchError: ""
    property var activeJobs: []
    property var downloadedPaths: ({})

    // Poll active download jobs periodically
    Timer {
        interval: 500
        running: true
        repeat: true
        onTriggered: {
            if (root.downloaderBridge) {
                root.activeJobs = root.downloaderBridge.getActiveJobs()
            }
        }
    }

    Connections {
        target: root.downloaderBridge
        function onSearchStarted() {
            root.isSearching = true
            root.searchError = ""
            root.searchResults = []
        }
        function onSearchFinished(tracks) {
            root.isSearching = false
            root.searchResults = tracks
        }
        function onSearchFailed(err) {
            root.isSearching = false
            root.searchError = err
        }
        function onJobFinished(jobId, success, pathOrError) {
            if (root.downloaderBridge) {
                root.activeJobs = root.downloaderBridge.getActiveJobs()
            }
        }
    }

    function triggerSearch() {
        const q = searchInput.text.trim()
        if (!q) return
        root.downloaderBridge.search(q, root.activeService)
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 28
        spacing: 16

        // Header & Tabs Bar
        RowLayout {
            Layout.fillWidth: true
            spacing: 16

            PageTabs {
                tabs: [
                    { id: "explore", label: "Explore & Download" },
                    { id: "queue", label: "Active Downloads (" + root.activeJobs.length + ")" }
                ]
                current: root.currentTab
                onSelected: id => root.currentTab = id
            }

            Item { Layout.fillWidth: true }

            // Download Folder Button
            Rectangle {
                height: 34
                width: folderRow.implicitWidth + 24
                radius: 8
                color: folderMouse.containsMouse ? appWindow.surfaceCardHover : appWindow.surfaceCard
                border.width: 1
                border.color: appWindow.borderSubtle

                RowLayout {
                    id: folderRow
                    anchors.centerIn: parent
                    spacing: 8

                    LucideIcon {
                        width: 15
                        height: 15
                        icon: "folder"
                        color: appWindow.textSecondary
                    }

                    Label {
                        text: "GrabSongs Folder"
                        font.family: appWindow.displayFont
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                        color: appWindow.textPrimary
                    }
                }

                MouseArea {
                    id: folderMouse
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                    onClicked: root.downloaderBridge.openDownloadFolder()
                }
            }
        }

        // VIEW: EXPLORE & DOWNLOAD
        Item {
            visible: root.currentTab === "explore"
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 16

                // Search Box Card
                Rectangle {
                    Layout.fillWidth: true
                    height: 52
                    radius: 12
                    color: appWindow.surfaceCard
                    border.width: 1
                    border.color: searchInput.activeFocus ? appWindow.recordRed : appWindow.borderSubtle

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 16
                        anchors.rightMargin: 12
                        spacing: 12

                        LucideIcon {
                            width: 18
                            height: 18
                            icon: "search"
                            color: searchInput.activeFocus ? appWindow.recordRed : appWindow.textSecondary
                        }

                        TextInput {
                            id: searchInput
                            Layout.fillWidth: true
                            font.family: appWindow.bodyFont
                            font.pixelSize: 14
                            color: appWindow.textPrimary
                            clip: true
                            selectByMouse: true
                            verticalAlignment: TextInput.AlignVCenter
                            onAccepted: root.triggerSearch()

                            Text {
                                anchors.fill: parent
                                verticalAlignment: Text.AlignVCenter
                                visible: !searchInput.text && !searchInput.activeFocus
                                text: "Paste Spotify, Apple Music, YouTube link or search track/artist..."
                                font.family: appWindow.bodyFont
                                font.pixelSize: 14
                                color: appWindow.silverDim
                            }
                        }

                        // Search Button
                        Rectangle {
                            height: 36
                            width: searchBtnRow.implicitWidth + 24
                            radius: 8
                            color: searchBtnMouse.containsMouse ? appWindow.recordRedHover : appWindow.recordRed

                            RowLayout {
                                id: searchBtnRow
                                anchors.centerIn: parent
                                spacing: 8

                                LucideIcon {
                                    width: 15
                                    height: 15
                                    icon: "download"
                                    color: "#FFFFFF"
                                }

                                Label {
                                    text: "Search & Fetch"
                                    font.family: appWindow.displayFont
                                    font.pixelSize: 13
                                    font.weight: Font.Bold
                                    color: "#FFFFFF"
                                }
                            }

                            MouseArea {
                                id: searchBtnMouse
                                anchors.fill: parent
                                cursorShape: Qt.PointingHandCursor
                                hoverEnabled: true
                                onClicked: root.triggerSearch()
                            }
                        }
                    }
                }

                // Service Filter Chips
                RowLayout {
                    spacing: 8

                    Repeater {
                        model: [
                            { id: "all", label: "All Platforms" },
                            { id: "spotify", label: "Spotify" },
                            { id: "apple", label: "Apple Music" },
                            { id: "youtube", label: "YouTube" },
                            { id: "deezer", label: "Deezer" }
                        ]

                        FilterChip {
                            required property var modelData
                            text: modelData.label
                            selected: root.activeService === modelData.id
                            onClicked: {
                                root.activeService = modelData.id
                                if (searchInput.text.trim().length > 0) {
                                    root.triggerSearch()
                                }
                            }
                        }
                    }

                    Item { Layout.fillWidth: true }

                    // Download All Button
                    Rectangle {
                        visible: root.searchResults.length > 1
                        height: 32
                        width: dlAllRow.implicitWidth + 20
                        radius: 8
                        color: dlAllMouse.containsMouse ? appWindow.surfaceCardHover : appWindow.surfaceCard
                        border.width: 1
                        border.color: appWindow.borderSubtle

                        RowLayout {
                            id: dlAllRow
                            anchors.centerIn: parent
                            spacing: 6

                            LucideIcon {
                                width: 14
                                height: 14
                                icon: "download"
                                color: appWindow.recordRed
                            }

                            Label {
                                text: "Download All (" + root.searchResults.length + ")"
                                font.family: appWindow.displayFont
                                font.pixelSize: 12
                                font.weight: Font.DemiBold
                                color: appWindow.textPrimary
                            }
                        }

                        MouseArea {
                            id: dlAllMouse
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            hoverEnabled: true
                            onClicked: root.downloaderBridge.downloadAll(root.searchResults)
                        }
                    }
                }

                // Content View / Results
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    // Loading State
                    ColumnLayout {
                        anchors.centerIn: parent
                        visible: root.isSearching
                        spacing: 12

                        BusyIndicator {
                            Layout.alignment: Qt.AlignHCenter
                            running: root.isSearching
                        }

                        Label {
                            Layout.alignment: Qt.AlignHCenter
                            text: "Resolving metadata and streams..."
                            font.family: appWindow.displayFont
                            font.pixelSize: 14
                            color: appWindow.textSecondary
                        }
                    }

                    // Error State
                    Label {
                        anchors.centerIn: parent
                        visible: !root.isSearching && root.searchError.length > 0
                        text: root.searchError
                        font.family: appWindow.displayFont
                        font.pixelSize: 14
                        color: appWindow.recordRed
                    }

                    // Empty / Instructions State
                    ColumnLayout {
                        anchors.centerIn: parent
                        visible: !root.isSearching && root.searchResults.length === 0 && !root.searchError
                        spacing: 12

                        LucideIcon {
                            Layout.alignment: Qt.AlignHCenter
                            width: 48
                            height: 48
                            icon: "download"
                            color: appWindow.silverDim
                        }

                        Label {
                            Layout.alignment: Qt.AlignHCenter
                            text: "Enter a query or paste a music link to begin"
                            font.family: appWindow.displayFont
                            font.pixelSize: 16
                            font.weight: Font.DemiBold
                            color: appWindow.textPrimary
                        }

                        Label {
                            Layout.alignment: Qt.AlignHCenter
                            text: "Supports Spotify tracks/playlists/albums, Apple Music, Deezer, and YouTube Music links."
                            font.family: appWindow.bodyFont
                            font.pixelSize: 13
                            color: appWindow.textSecondary
                        }
                    }

                    // Results List
                    ListView {
                        id: resultsListView
                        anchors.fill: parent
                        visible: !root.isSearching && root.searchResults.length > 0
                        model: root.searchResults
                        clip: true
                        spacing: 8

                        delegate: Rectangle {
                            required property var modelData
                            required property int index

                            width: resultsListView.width
                            height: 72
                            radius: 10
                            color: itemMouse.containsMouse ? appWindow.surfaceCardHover : appWindow.surfaceCard
                            border.width: 1
                            border.color: appWindow.borderSubtle

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 12
                                anchors.rightMargin: 16
                                spacing: 14

                                // Artwork thumbnail
                                Rectangle {
                                    width: 48
                                    height: 48
                                    radius: 6
                                    clip: true
                                    color: appWindow.surfaceDock

                                    Image {
                                        anchors.fill: parent
                                        source: modelData.artworkUrl || ""
                                        fillMode: Image.PreserveAspectCrop
                                        asynchronous: true
                                    }
                                }

                                // Track Details
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 3

                                    RowLayout {
                                        spacing: 8
                                        Label {
                                            text: modelData.title || "Unknown Title"
                                            font.family: appWindow.displayFont
                                            font.pixelSize: 14
                                            font.weight: Font.Bold
                                            color: appWindow.textPrimary
                                            elide: Text.ElideRight
                                            Layout.maximumWidth: 400
                                        }

                                        // Service Tag Badge
                                        Rectangle {
                                            height: 18
                                            width: svcBadgeText.implicitWidth + 12
                                            radius: 4
                                            color: modelData.service === "spotify" ? "#1DB954" : (modelData.service === "apple" ? "#FC3C44" : "#FF0000")
                                            opacity: 0.85

                                            Label {
                                                id: svcBadgeText
                                                anchors.centerIn: parent
                                                text: (modelData.service || "MUSIC").toUpperCase()
                                                font.family: appWindow.displayFont
                                                font.pixelSize: 10
                                                font.weight: Font.Bold
                                                color: "#FFFFFF"
                                            }
                                        }
                                    }

                                    Label {
                                        text: (modelData.artist || "Unknown Artist") + " • " + (modelData.album || "")
                                        font.family: appWindow.bodyFont
                                        font.pixelSize: 12
                                        color: appWindow.textSecondary
                                        elide: Text.ElideRight
                                    }
                                }

                                // Format badge
                                Label {
                                    text: "320 kbps MP3"
                                    font.family: appWindow.monoFont
                                    font.pixelSize: 11
                                    color: appWindow.silverDim
                                }

                                // Duration
                                Label {
                                    text: modelData.duration || "3:30"
                                    font.family: appWindow.monoFont
                                    font.pixelSize: 12
                                    color: appWindow.textSecondary
                                }

                                // Download Action Button
                                Rectangle {
                                    height: 34
                                    width: dlBtnRow.implicitWidth + 20
                                    radius: 8
                                    color: modelData.downloaded
                                           ? appWindow.surfaceElevated
                                           : (dlBtnMouse.containsMouse ? appWindow.recordRedHover : appWindow.recordRed)
                                    border.width: modelData.downloaded ? 1 : 0
                                    border.color: appWindow.borderSubtle

                                    RowLayout {
                                        id: dlBtnRow
                                        anchors.centerIn: parent
                                        spacing: 6

                                        LucideIcon {
                                            width: 14
                                            height: 14
                                            icon: modelData.downloaded ? "check" : "download"
                                            color: modelData.downloaded ? "#10B981" : "#FFFFFF"
                                        }

                                        Label {
                                            text: modelData.downloaded ? "Downloaded" : "Download"
                                            font.family: appWindow.displayFont
                                            font.pixelSize: 12
                                            font.weight: Font.Bold
                                            color: modelData.downloaded ? "#10B981" : "#FFFFFF"
                                        }
                                    }

                                    MouseArea {
                                        id: dlBtnMouse
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        hoverEnabled: true
                                        onClicked: {
                                            if (!modelData.downloaded) {
                                                root.downloaderBridge.downloadTrack(modelData)
                                            }
                                        }
                                    }
                                }
                            }

                            MouseArea {
                                id: itemMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                z: -1
                            }
                        }
                    }
                }
            }
        }

        // VIEW: DOWNLOAD QUEUE
        Item {
            visible: root.currentTab === "queue"
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                spacing: 16

                // Queue empty state
                ColumnLayout {
                    Layout.alignment: Qt.AlignCenter
                    visible: root.activeJobs.length === 0
                    spacing: 12

                    LucideIcon {
                        Layout.alignment: Qt.AlignHCenter
                        width: 48
                        height: 48
                        icon: "check"
                        color: "#10B981"
                    }

                    Label {
                        Layout.alignment: Qt.AlignHCenter
                        text: "No active downloads"
                        font.family: appWindow.displayFont
                        font.pixelSize: 16
                        font.weight: Font.DemiBold
                        color: appWindow.textPrimary
                    }

                    Label {
                        Layout.alignment: Qt.AlignHCenter
                        text: "All queued tracks have completed downloading and are in your library."
                        font.family: appWindow.bodyFont
                        font.pixelSize: 13
                        color: appWindow.textSecondary
                    }
                }

                // Active Jobs List
                ListView {
                    id: queueListView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    visible: root.activeJobs.length > 0
                    model: root.activeJobs
                    clip: true
                    spacing: 8

                    delegate: Rectangle {
                        required property var modelData
                        required property int index

                        width: queueListView.width
                        height: 76
                        radius: 10
                        color: appWindow.surfaceCard
                        border.width: 1
                        border.color: appWindow.borderSubtle

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 8

                            RowLayout {
                                Layout.fillWidth: true

                                Label {
                                    text: modelData.title || "Downloading track"
                                    font.family: appWindow.displayFont
                                    font.pixelSize: 14
                                    font.weight: Font.Bold
                                    color: appWindow.textPrimary
                                }

                                Label {
                                    text: " • " + (modelData.artist || "")
                                    font.family: appWindow.bodyFont
                                    font.pixelSize: 13
                                    color: appWindow.textSecondary
                                }

                                Item { Layout.fillWidth: true }

                                Label {
                                    text: Math.round(modelData.percent || 0) + "%"
                                    font.family: appWindow.monoFont
                                    font.pixelSize: 13
                                    font.weight: Font.Bold
                                    color: appWindow.recordRed
                                }

                                Label {
                                    text: modelData.speed ? " • " + modelData.speed : ""
                                    font.family: appWindow.monoFont
                                    font.pixelSize: 11
                                    color: appWindow.silverDim
                                }
                            }

                            // Progress Bar
                            Rectangle {
                                Layout.fillWidth: true
                                height: 6
                                radius: 3
                                color: appWindow.surfaceDock

                                Rectangle {
                                    height: parent.height
                                    width: parent.width * Math.max(0.02, Math.min(1.0, (modelData.percent || 0) / 100))
                                    radius: 3
                                    color: appWindow.recordRed
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
