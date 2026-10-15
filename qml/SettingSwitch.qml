import QtQuick

Rectangle {
    id: root
    property bool checked: false
    signal toggled(bool checked)

    implicitWidth: 40
    implicitHeight: 22
    radius: 11
    color: root.checked
        ? (mouseArea.containsMouse ? recordRedHover : recordRed)
        : (mouseArea.containsMouse ? surfaceElevated : surfaceCard)
    opacity: root.enabled ? 1.0 : 0.4
    border.width: 1
    border.color: root.activeFocus
        ? recordRedHover
        : (root.checked ? recordRed : borderVariant)

    activeFocusOnTab: true
    Accessible.role: Accessible.CheckBox
    Accessible.name: "Switch"
    Accessible.checked: root.checked

    Keys.onSpacePressed: event => {
        event.accepted = true
        root.toggled(!root.checked)
    }
    Keys.onReturnPressed: event => {
        event.accepted = true
        root.toggled(!root.checked)
    }

    Behavior on color { ColorAnimation { duration: 140 } }
    Behavior on border.color { ColorAnimation { duration: 140 } }

    Rectangle {
        id: thumb
        y: 3
        x: root.checked ? root.width - width - 3 : 3
        width: 14
        height: 14
        radius: 7
        color: root.checked
            ? "#FFFFFF"
            : (mouseArea.containsMouse ? textSecondary : silverDim)

        Behavior on x {
            NumberAnimation {
                duration: 140
                easing.type: Easing.OutCubic
            }
        }
        Behavior on color { ColorAnimation { duration: 140 } }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: root.enabled
        hoverEnabled: root.enabled
        cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: {
            root.forceActiveFocus()
            root.toggled(!root.checked)
        }
    }
}
