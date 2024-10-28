
var video = document.querySelector("#videoElement");

if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
        })
        .catch(function (err0r) {
            console.log("Something went wrong!");
        });
}
// not used
function stop(e) {
    var stream = video.srcObject;
    var tracks = stream.getTracks();

    for (var i = 0; i < tracks.length; i++) {
        var track = tracks[i];
        track.stop();
    }

    video.srcObject = null;
}

var items = new Array();
var obj = {};
var tr;
var total = 0;
var d1 = items;
function addItem() {
    console.log("addItem() called.")
    var table = document.getElementById("myTable");
    var tbodyRowCount = table.tBodies[0].rows.length;

    var row = table.insertRow(tbodyRowCount);

    // not sure yet
    // var items = new Array();
    // var obj = {};

    obj.Item = "Pau Kaya";
    obj.Quantity = "1";
    obj.Price = "1.50";
    items.push(obj);
    console.log(items);

    // var tr;
    // var total = 0;
    // var d1 = items;
    calcTotal();
    // $(function calcTotal() {
    //     console.log("calcTotal() called.")
    //     for (var i = 0; i < d1.length; i++) {
    //         total += parseFloat(d1[i].Price);
    //         console.log("total: " + total);
    //         $('#total').html(total);
    //     }
    // });

    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);
    var cell3 = row.insertCell(2);
    var cell4 = row.insertCell(3);

    // change to display info from array
    cell1.innerHTML = "Pau Kaya";
    cell2.innerHTML = "1";
    cell3.innerHTML = "RM 1.50";

    var deletebtn = '<input type="button" value="Delete" onclick="deleteItem(this)">'
    cell4.innerHTML = deletebtn;
}

function calcTotal() {
    console.log("calcTotal() called.")
    if (d1.length == 0) {
        $('#total').html(total);
    }
    for (var i = 0; i < d1.length; i++) {
        total += parseFloat(d1[i].Price);
        console.log("total: " + total);
        $('#total').html(total);
    }
    total = 0;
}

function deleteItem(r) {
    console.log("deleteItem() called.")
    var i = r.parentNode.parentNode.rowIndex;
    console.log("Index row: " + i);
    document.getElementById("myTable").deleteRow(i);
    // add code to also delete item from array
    var deleted = items.splice(i - 1, 1);
    console.log("Index array: " + i);
    console.log("Item deleted: " + deleted);
    console.log(items);
    calcTotal();
}

$(function () {
    var grid = document.getElementById("myTable");
    var rows = grid.getElementsByTagName("TR");
    var amount = 0;
    for (var i = 1; i < rows.length; i++) {
        var cells = rows[i].getElementsByTagName("TD");
        amount += parseFloat(cells[2].innerHTML);
    }
    $('[id*=total]').val(amount);
});