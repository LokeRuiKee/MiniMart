
// calls addItem() when content of json file changes
let previous = null;
let current = null;
setInterval(function () {
    $.getJSON("http://localhost:5000/get_json", function (json) {
        current = JSON.stringify(json);
        if (previous && current && previous !== current) {
            console.log("addItem() called from detected item, json file changed");
            addItem();
        }
        previous = current;
    }).fail(function (jqxhr, textStatus, error) {
        console.error("Request Failed: " + textStatus + ", " + error);
    });
}, 2000);

// display initial total price
$('#total').html(Number(0.00).toFixed(2));

// to count sales of each item
let salesCount = {};

function updateSalesCount(itemName) {
    if (salesCount[itemName]) {
        salesCount[itemName] += 1;
    } else {
        salesCount[itemName] = 1;
    }
    console.log("updateSalesCount is called to store", itemName, salesCount[itemName]);
    return salesCount[itemName];
}

// add item to table
// madihah: new addItem(): comparing with json array from database (added wed, 4:21pm)
// madihah: not working yet
// madihah: uncomment to test

//import { getDetails } from './dbConnection/get_item_details.js';

//let total = 0;
//const d1 = items;

//function addItem() {
//    console.log("addItem() called.")
//    const table = document.getElementById("myTable");
//    const tbodyRowCount = table.tBodies[0].rows.length;

//    const row = table.insertRow(tbodyRowCount);

//    // get item details (name, price) from database based on item id
//    // not working yet
//    getDetails();

//    // calculate total
//    calcTotal();

//    // insert new row with detected item details
//    const cell1 = row.insertCell(0);
//    const cell2 = row.insertCell(1);
//    const cell3 = row.insertCell(2);
//    const cell4 = row.insertCell(3);

//    cell1.innerHTML = obj.Item;
//    cell2.innerHTML = obj.Quantity;
//    cell3.innerHTML = obj.Price;

//    const deletebtn = '<input type="button" value="Delete" onclick="deleteItem(this)">'
//    cell4.innerHTML = deletebtn;
//}

// madihah: old addItem(): comparing with dictionary
const xmlhttp = new XMLHttpRequest();

const items = new Array();
const obj = {};
const tr;
let total = 0;
const d1 = items;

// replace dictionary to pull from database
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

// adds item to table
function addItem() {
    console.log("addItem() called.")
    const table = document.getElementById("myTable");
    const tbodyRowCount = table.tBodies[0].rows.length;

    const row = table.insertRow(tbodyRowCount);

    xmlhttp.onload = function () {
        const myObj = JSON.parse(this.responseText);
        let id = myObj.class_id;

        for (const key in object) {

            console.log("key: " + key);
            console.log("id: " + id);
            // compares id from json file to dictionary to get item details
            if (parseInt(key) === parseInt(id)) {
                console.log("key equals id")
                object[key].forEach(item => {
                    console.log(`\tName: ${item.Name}`);
                    obj.Item = item.Name;
                    obj.Quantity = "1";
                    if (item.Price) {
                        console.log(`\tPrice: ${item.Price}`);
                        obj.Price = item.Price.toFixed(2);
                    }
                    console.log();
                });
                items.push(obj);
                break;
            }
            else {
                return;
            }
        }

        console.log("items: " + items);

        // calculate total
        calcTotal();

        // insert new row with detected item details
        const cell1 = row.insertCell(0);
        const cell2 = row.insertCell(1);
        const cell3 = row.insertCell(2);
        const cell4 = row.insertCell(3);

        cell1.innerHTML = obj.Item;
        cell2.innerHTML = obj.Quantity;
        cell3.innerHTML = obj.Price;

        const deletebtn = '<input type="button" value="Delete" onclick="deleteItem(this)">'
        cell4.innerHTML = deletebtn;
    }
    // xmlhttp.open("GET", "http://localhost:5000/get_json");
    // madihah:
    xmlhttp.open("GET", "http://localhost:52202/get_json");
    xmlhttp.send();
}

// calculates total
function calcTotal() {
    console.log("calcTotal() called.")
    if (d1.length == 0) {
        $('#total').html(total);
    }
    for (const element of d1) {
        total += parseFloat(element.Price);
        console.log("total: " + total);
        $('#total').html(total.toFixed(2));
    }
    total = 0;
}

// deletes item from table
function deleteItem(r) {
    console.log("deleteItem() called.")
    const i = r.parentNode.parentNode.rowIndex;
    console.log("Index row: " + i);
    document.getElementById("myTable").deleteRow(i);
    // add code to also delete item from array
    const deleted = items.splice(i - 1, 1);
    console.log("Index array: " + i);
    console.log("Item deleted: " + deleted);
    console.log(items);
    calcTotal();
}