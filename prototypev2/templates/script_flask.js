
// calls addItem() when content of json file changes
let previous = null;
let current = null;

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
// madihah: new addItem(): comparing with json array from server (added monday 11 nov, 3:35pm)
// madihah: works
const baseUrl = 'http://localhost:5000/item_details'

const items = [];
let total = 0;

async function getItemDetails() {
    // gets the response from the api and put it inside a constant
    const response = await fetch(baseUrl);
    //the response has to be converted to json type file, so it can be used
    const data = await response.json();
    //console.log("This is the value of data inside the function getItemDetails:")
    //console.log("Type: " + typeof data);
    console.log(data)

    setInterval(function () {
        $.getJSON("http://127.0.0.1:5000/get_json", function (json) {
            current = JSON.stringify(json);
            if (previous && current && previous !== current) {
                console.log("addItem() called from detected item, json file changed");
                addItem(data);
            }
            previous = current;
        }).fail(function (jqxhr, textStatus, error) {
            console.error("Request Failed: " + textStatus + ", " + error);
        });
    }, 2000);
}

function addItem(object) {

    // uncomment to check data passed to this function
    //console.log("This is the value of data inside the function addData:")
    //console.log("Type: " + typeof object);
    //console.log(data)
    //object.forEach((item) => {
    //    console.log(item);
    //    console.log('ID: ' + item.item_id);
    //    console.log('Name: ' + item.item_name);
    //    console.log('Price: ' + item.item_price);
    //});

    console.log("addItem() called.")
    const table = document.getElementById("myTable");
    const tbodyRowCount = table.tBodies[0].rows.length;
    const row = table.insertRow(tbodyRowCount);

    const xmlhttp = new XMLHttpRequest();
    xmlhttp.onload = function () {
        // from get_json
        const myObj = JSON.parse(this.responseText);
        console.log("myObj: ");
        console.log(myObj);

        let id = myObj.class_id;

        // from item_details
        const obj = {};

        for (const element of object) {
            let result_id = element.item_id;

            // compares id from json file to dictionary to get item details
            if (parseInt(result_id) === parseInt(id)) {
                console.log("result_id equals id");
                obj.Item = element.item_name;
                obj.Quantity = 1;
                obj.Price = element.item_price.toFixed(2);
                console.log("obj");
                console.log(obj);
                items.push(obj);
                break;
            }
            else {
                console.log("result_id not equal id")
            }
        }

        console.log("items: ");
        console.log(items);

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

        const deletebtn = '<button value="Delete" onclick="deleteItem(this)" class="noselect button-delete"><span class="text">Delete</span><span class="icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M24 20.188l-8.315-8.209 8.2-8.282-3.697-3.697-8.212 8.318-8.31-8.203-3.666 3.666 8.321 8.24-8.206 8.313 3.666 3.666 8.237-8.318 8.285 8.203z"></path></svg></span></button>'
        cell4.innerHTML = deletebtn;

        // to autoscroll to the bottom every time an item is added
        const elem = document.getElementById('tablecontainer');
        elem.scrollTop = elem.scrollHeight;
    }
    // change to local:5000/get_json if needed
    xmlhttp.open("GET", "http://127.0.0.1:5000/get_json");
    xmlhttp.send();
}

//Calls the function that fetches the data
getItemDetails()

function testAddItem() {
    const table = document.getElementById("myTable");
    const tbodyRowCount = table.tBodies[0].rows.length;

    const row = table.insertRow(tbodyRowCount);

    // insert new row with detected item details
    const cell1 = row.insertCell(0);
    const cell2 = row.insertCell(1);
    const cell3 = row.insertCell(2);
    const cell4 = row.insertCell(3);

    cell1.innerHTML = "Malkist Cream Crackers";
    cell2.innerHTML = 1;
    cell3.innerHTML = (3.50).toFixed(2);

    const deletebtn = '<button value="Delete" onclick="deleteItem(this)" class="noselect button-delete"><span class="text">Delete</span><span class="icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path d="M24 20.188l-8.315-8.209 8.2-8.282-3.697-3.697-8.212 8.318-8.31-8.203-3.666 3.666 8.321 8.24-8.206 8.313 3.666 3.666 8.237-8.318 8.285 8.203z"></path></svg></span></button>'
    cell4.innerHTML = deletebtn;

    // to autoscroll to the bottom every time an item is added
    const elem = document.getElementById('tablecontainer');
    elem.scrollTop = elem.scrollHeight;
}

// calculates total
const d1 = items;
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

// madihah: open popup with qr and to reset session (clear table) when pay button is clicked
// added: thur, 14/11, 2:05pm
// Get the modal
const modal = document.getElementById("modal");

// Get the button that opens the modal
const btn = document.getElementById("paybtn");

const cancelbtn = document.getElementById("cancelbtn");

const completebtn = document.getElementById("completebtn");

// When the user clicks the button, open the modal 
btn.onclick = function () {
    modal.style.display = "grid";
}

// When the user clicks on cancelbtn, close the modal
cancelbtn.onclick = function () {
    modal.style.display = "none";
}

// When the user clicks on completebtn, close the modal, clear table and reset total
completebtn.onclick = function () {
    modal.style.display = "none";
    $("#myTable").find("tr:not(:first)").remove();
    total = 0;
    $('#total').html(total.toFixed(2));
}