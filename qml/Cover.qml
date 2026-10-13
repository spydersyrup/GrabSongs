import QtQuick
import QtQuick.Effects
import QtQuick.Window

Item {
    id: root
    property var track: ({})
    property real radius: (typeof window !== "undefined" && window.albumArtRadius !== undefined) ? window.albumArtRadius : 8
    property bool keepPreviousArtwork: false
    property bool cacheArtwork: true
    property real stableSourceSize: 0
    property bool showTonearm: false
    property int fillMode: Image.PreserveAspectCrop
    readonly property int requestedLongEdge: {
        const rawDim = stableSourceSize > 0 ? stableSourceSize : Math.max(width, height)
        const target = (rawDim > 10 ? rawDim : 256) * (Screen.devicePixelRatio || 1)
        return Math.max(32, Math.min(1536, Math.ceil(target)))
    }
    readonly property size requestedSourceSize: providerRounded && width > 0 && height > 0
        ? Qt.size(Math.ceil(requestedLongEdge * width / Math.max(width, height)),
                  Math.ceil(requestedLongEdge * height / Math.max(width, height)))
        : Qt.size(requestedLongEdge, requestedLongEdge)

    function normalizeUrl(val) {
        if (!val) return ""
        const str = String(val).trim()
        if (!str || str === "null" || str === "undefined") return ""
        if (str.startsWith("file://") || str.startsWith("http://") || str.startsWith("https://") || str.startsWith("qrc:/") || str.startsWith("image://") || str.startsWith("data:")) {
            return str
        }
        return "file:///" + str.replace(/\\/g, "/")
    }

    readonly property bool providerRounded: false

    readonly property url artworkSource: rawArtworkSource

    readonly property url rawArtworkSource: {
        const currentTrack = root.track || ({})
        if (currentTrack.artworkUrl) return normalizeUrl(currentTrack.artworkUrl)
        if (currentTrack.artwork_url) return normalizeUrl(currentTrack.artwork_url)
        if (currentTrack.cover_url) return normalizeUrl(currentTrack.cover_url)
        if (currentTrack.cover) return normalizeUrl(currentTrack.cover)
        if (currentTrack.artwork) return normalizeUrl(currentTrack.artwork)
        if (currentTrack.thumbnail) return normalizeUrl(currentTrack.thumbnail)
        const path = currentTrack.filePath || ""
        if (!path) return ""
        return normalizeUrl(path)
    }

    property bool useB: false
    readonly property var activeImage: useB ? imageB : imageA
    readonly property var previousImage: useB ? imageA : imageB

    readonly property real artworkImplicitWidth: activeImage ? activeImage.implicitWidth : 0
    readonly property real artworkImplicitHeight: activeImage ? activeImage.implicitHeight : 0
    readonly property real artworkAspectRatio: (artworkImplicitHeight > 0 && artworkImplicitWidth > 0)
        ? (artworkImplicitWidth / artworkImplicitHeight)
        : 1.0

    readonly property bool hasArtwork: artworkSource.toString() !== ""
    // The cover image provider answers "no artwork" with a 1x1 image instead of an error.
    function hasNoArt(image) {
        return image.status === Image.Error || (image.status === Image.Ready && image.implicitWidth <= 1)
    }
    readonly property bool currentHasError: hasNoArt(useB ? imageB : imageA)
    readonly property bool anyArtVisible: (imageA.status === Image.Ready && !hasNoArt(imageA) && imageA.opacity > 0.01)
                                       || (imageB.status === Image.Ready && !hasNoArt(imageB) && imageB.opacity > 0.01)
    readonly property bool showingFallback: (!hasArtwork || currentHasError) && !anyArtVisible
    readonly property bool currentTrackPlaying: !!(typeof player !== "undefined" && player && player.isPlaying && root.track && player.currentTrack && root.track.filePath === player.currentTrack.filePath)

    function coverColor(value) {
        const colors = [
            "#221E1B", "#1C1F26", "#241820", "#18221D", "#201B24", "#241F18"
        ]
        let hash = 0
        const str = value || "CassetteCat"
        for (let i = 0; i < str.length; ++i) hash = (hash * 31 + str.charCodeAt(i)) >>> 0
        return colors[hash % colors.length]
    }

    onArtworkSourceChanged: {
        applyArtworkSource()
    }

    Component.onCompleted: {
        applyArtworkSource()
    }

    function applyArtworkSource() {
        const next = artworkSource.toString()
        const curr = activeImage.source.toString()

        if (next === curr && activeImage.status === Image.Ready) return

        if (!next) {
            imageA.opacity = 0
            imageB.opacity = 0
            return
        }

        if (root.keepPreviousArtwork && activeImage.status === Image.Ready && curr !== "") {
            if (useB) {
                imageA.opacity = 0
                imageA.source = next
                useB = false
                if (imageA.status === Image.Ready) {
                    imageA.opacity = 1
                    imageB.opacity = 0
                }
            } else {
                imageB.opacity = 0
                imageB.source = next
                useB = true
                if (imageB.status === Image.Ready) {
                    imageB.opacity = 1
                    imageA.opacity = 0
                }
            }
        } else {
            activeImage.opacity = 0
            activeImage.source = next
            if (activeImage.status === Image.Ready) {
                activeImage.opacity = 1
            }
        }
    }

    Rectangle {
        id: bgPlaceholder
        anchors.fill: parent
        radius: root.radius
        color: surfaceCard

        // Built only for covers without art; held on every cover, it kept three images per card.
        Loader {
            anchors.fill: parent
            active: root.showingFallback
            sourceComponent: VinylFallback {
                showTonearm: root.showTonearm
                playing: root.currentTrackPlaying && root.showingFallback
                progress: root.currentTrackPlaying && player.duration > 0 ? player.position / player.duration : 0
            }
        }
    }

    Rectangle {
        id: maskItem
        anchors.fill: parent
        radius: root.radius
        color: "#FFFFFF"
        visible: false
        layer.enabled: root.radius > 0 && !root.providerRounded
        layer.smooth: true
    }

    Item {
        id: imageContainer
        anchors.fill: parent
        layer.enabled: root.radius > 0 && root.anyArtVisible && !root.providerRounded
        layer.effect: MultiEffect {
            maskEnabled: true
            maskSource: maskItem
        }

        Image {
            id: imageA
            anchors.fill: parent
            sourceSize: root.requestedSourceSize
            fillMode: root.fillMode
            asynchronous: true
            cache: root.cacheArtwork
            smooth: true
            mipmap: false
            autoTransform: true
            opacity: 0
            visible: opacity > 0.001

            onStatusChanged: {
                if (status === Image.Ready && !root.useB) {
                    imageA.opacity = 1
                    if (imageB.opacity > 0) imageB.opacity = 0
                } else if (status === Image.Error && !root.useB) {
                    imageA.opacity = 0
                    if (imageB.opacity > 0) imageB.opacity = 0
                }
            }
            onOpacityChanged: {
                if (opacity === 0 && root.useB && status !== Image.Loading) {
                    source = ""
                }
            }
            Behavior on opacity {
                NumberAnimation { duration: UiConstants.durationStd; easing.type: UiConstants.easingStd }
            }
        }

        Image {
            id: imageB
            anchors.fill: parent
            sourceSize: root.requestedSourceSize
            fillMode: root.fillMode
            asynchronous: true
            cache: root.cacheArtwork
            smooth: true
            mipmap: false
            autoTransform: true
            opacity: 0
            visible: opacity > 0.001

            onStatusChanged: {
                if (status === Image.Ready && root.useB) {
                    imageB.opacity = 1
                    if (imageA.opacity > 0) imageA.opacity = 0
                } else if (status === Image.Error && root.useB) {
                    imageB.opacity = 0
                    if (imageA.opacity > 0) imageA.opacity = 0
                }
            }
            onOpacityChanged: {
                if (opacity === 0 && !root.useB && status !== Image.Loading) {
                    source = ""
                }
            }
            Behavior on opacity {
                NumberAnimation { duration: UiConstants.durationStd; easing.type: UiConstants.easingStd }
            }
        }
    }
}
