import QtQuick
import QtQuick.Controls

Item {
    id: root
    property string iconName: ""
    property int boxSize: 36
    property int iconSize: 18
    property color tint: silverDim
    property color hoverTint: textPrimary
    property color backgroundColor: "transparent"
    property color hoverBackgroundColor: surfaceElevated
    property color borderColor: "transparent"
    property color hoverBorderColor: "transparent"
    property bool highlighted: false
    property alias accented: root.highlighted
    property string tooltipText: ""
    property real cornerRadius: Math.round(boxSize / 2)
    signal clicked()

    implicitWidth: root.boxSize
    implicitHeight: root.boxSize

    readonly property bool isPressed: mouseArea.pressed
    readonly property bool isHovered: mouseArea.containsMouse || (root.activeFocus && !root.mouseFocused)
    property bool mouseFocused: false
    onActiveFocusChanged: if (!activeFocus) mouseFocused = false

    Accessible.role: Accessible.Button
    Accessible.name: root.tooltipText
    Accessible.onPressAction: root.clicked()
    activeFocusOnTab: root.opacity > 0
    Keys.onReturnPressed: root.clicked()
    Keys.onEnterPressed: root.clicked()

    Rectangle {
        anchors.fill: parent
        radius: root.cornerRadius
        color: root.isHovered ? root.hoverBackgroundColor : root.backgroundColor
        readonly property color currentBorderColor: root.highlighted ? recordRed : (root.isHovered ? root.hoverBorderColor : root.borderColor)
        border.width: root.highlighted ? 1.5 : (currentBorderColor.toString() === "#00000000" || currentBorderColor === "transparent" ? 0 : 1.0)
        border.color: currentBorderColor

        Behavior on color { ColorAnimation { duration: 130 } }
        Behavior on border.color { ColorAnimation { duration: 130 } }
    }

    Item {
        id: iconContainer
        anchors.centerIn: parent
        width: root.iconSize
        height: root.iconSize
        y: root.isPressed ? 1.5 : 0

        Behavior on y {
            NumberAnimation { duration: 80; easing.type: Easing.Linear }
        }

        LucideIcon {
            anchors.fill: parent
            icon: root.iconName
            color: root.highlighted ? recordRedHover : (root.isHovered ? root.hoverTint : root.tint)
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onPressed: {
            root.mouseFocused = true
            root.forceActiveFocus()
        }
        onClicked: root.clicked()
    }

    AppToolTip {
        targetItem: mouseArea
        text: root.tooltipText
        visibleTarget: mouseArea.containsMouse && root.tooltipText.length > 0
        delay: 350
    }
}
