// Copyright (C) 2024 twyleg
import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: window

    width: 800
    height: 480
    visible: true
    title: qsTr("Frontend")

    color: "black"

    Component.onCompleted: Qt.exit(0)
}
