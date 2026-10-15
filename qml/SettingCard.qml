import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    default property alias content: inner.data

    Layout.fillWidth: true
    implicitHeight: inner.implicitHeight + 16
    radius: 8
    clip: true
    color: surfaceCard
    border.width: 1
    border.color: borderSubtle

    ColumnLayout {
        id: inner
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.leftMargin: 20
        anchors.rightMargin: 20
        anchors.topMargin: 8
        anchors.bottomMargin: 8
        spacing: 0
    }
}
