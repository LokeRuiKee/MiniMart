
var previous = null;
var current = null;
setInterval(function () {
    $.getJSON("C:\\Users\\ptplokee\\Source\\Repos\\MiniMart\\templates\\flask_detect.json", function (json) {
        current = JSON.stringify(json);
        if (previous && current && previous !== current) {
            console.log("addItem() called from detected item, json file changed")
            addItem();
        }
        previous = current;
    });
}, 2000);

$('#total').html(Number(0.00).toFixed(2));
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

const xmlhttp = new XMLHttpRequest();
// xmlhttp.onload = function () {
//     const myObj = JSON.parse(this.responseText);
//     document.getElementById("demo").innerHTML = myObj.class_id;
// }
// xmlhttp.open("GET", "./sample.json");
// xmlhttp.send();

// fetch('./data.json')
//     .then((response) => response.json())
//     .then((json) => console.log(json));

var items = new Array();
var obj = {};
var tr;
var total = 0;
var d1 = items;

const object = {
    1: [
        {
            "Name": "Luxury Chips",
            "Price": 5.50
        }
    ],
    2: [
        {
            "Name": "Cream-O Chocolate",
            "Price": 3.80
        }
    ],
    3: [
        {
            "Name": "Cream-O White Chocolate",
            "Price": 3.80
        }
    ],
    4: [
        {
            "Name": "Golden Crackers",
            "Price": 3.90
        }
    ],
    5: [
        {
            "Name": "Malkist Cream Crackers",
            "Price": 2.50
        }
    ]
};

function addItem() {
    console.log("addItem() called.")
    var table = document.getElementById("myTable");
    var tbodyRowCount = table.tBodies[0].rows.length;

    var row = table.insertRow(tbodyRowCount);

    xmlhttp.onload = function () {
        const myObj = JSON.parse(this.responseText);
        let id = myObj.class_id;
        // let text = ""
        // text += id + "<br>";
        // text += myObj.class_name + "<br>";

        // document.getElementById("demo").innerHTML = text;

        for (const key in object) {
            // console.log(`${key}:`);
            // object[key].forEach(item => {
            //     console.log(`\tName: ${item.Name}`);
            //     if (item.Price) {
            //         console.log(`\tPrice: ${item.Price}`);
            //     }
            //     console.log();
            // });

            console.log("key: " + key);
            console.log("id: " + id);
            if (parseInt(key) === parseInt(id)) {
                console.log("key equals id")
                object[key].forEach(item => {
                    console.log(`\tName: ${item.Name}`);
                    obj.Item = item.Name;
                    obj.Quantity = "1";
                    if (item.Price) {
                        console.log(`\tPrice: ${item.Price}`);
                        obj.Price = item.Price.toFixed(2);;
                    }
                    console.log();
                });
                items.push(obj);
                break;
            }
        }

        console.log("items: " + items);

        calcTotal();

        var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        var cell3 = row.insertCell(2);
        var cell4 = row.insertCell(3);

        cell1.innerHTML = obj.Item;
        cell2.innerHTML = obj.Quantity;
        cell3.innerHTML = obj.Price;

        var deletebtn = '<input type="button" value="Delete" onclick="deleteItem(this)">'
        cell4.innerHTML = deletebtn;
    }
    xmlhttp.open("GET", "./detected_item.json");
    xmlhttp.send();
}

function calcTotal() {
    console.log("calcTotal() called.")
    if (d1.length == 0) {
        $('#total').html(total);
    }
    for (var i = 0; i < d1.length; i++) {
        total += parseFloat(d1[i].Price);
        console.log("total: " + total);
        $('#total').html(total.toFixed(2));
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