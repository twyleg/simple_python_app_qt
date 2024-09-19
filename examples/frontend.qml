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

    Text {
        id: headline

        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: parent.height * 0.2

        text: example_model.headline
        color: "white"
        font.pointSize: 32

        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    Text {
        id: counter

        anchors.top: headline.bottom
        anchors.bottom: scrollView.top
        anchors.left: parent.left
        anchors.right: parent.right

        text: example_model.counter
        color: "white"
        font.pointSize: 72

        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter

        onTextChanged: {
            console.info("Counter: ", counter.text)
        }
    }

    ScrollView {
        id: scrollView

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        height: parent.height * 0.4
        contentHeight: log.height

        clip: true

        ScrollBar.vertical.policy: ScrollBar.AlwaysOn
        ScrollBar.vertical.position: 1.0

        function scrollToBottom() {
            scrollView.ScrollBar.vertical.position = 1.0 - scrollView.ScrollBar.vertical.size
        }

        TextArea {
            id: log

            anchors.fill: parent

            color: "white"
            readOnly: true
            selectByMouse : true
            font.pixelSize: 12

            background: Rectangle {
                color: "#ff2e2f30"
            }

            onTextChanged: scrollView.scrollToBottom()
        }
    }

    Connections {
        target: log_model

        function onLogLineAdded(levelno, header, msg) {
            log.append(header + msg)
        }
    }

    Component.onCompleted: {
        console.info("Frontend started!")
        log_model.requestPrebuffer()
    }
}
