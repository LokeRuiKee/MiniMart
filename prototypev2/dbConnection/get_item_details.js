const sql = require('mssql/msnodesqlv8');

const dbConfig = {
    server: 'PTPNTE818',
    port: 1433,
    database: 'miniMart',
    driver: "msnodesqlv8",
    options: {
        trustedConnection: true,
    }
}

const fs = require("fs");

const items = new Array();
const obj = {};

// madihah: need to add 'export' before async function ...
async function getDetails() {

    try {
        await sql.connect(dbConfig);

        //const myObj = fetch("http://localhost:5000/get_json")
        //    .then((res) => {
        //        if (!res.ok) {
        //            throw new Error
        //                (`HTTP error! Status: ${res.status}`);
        //        }
        //        return res.json();
        //    })
        //    .then((data) =>
        //        console.log(data))
        //    .catch((error) =>
        //        console.error("Unable to fetch data:", error));

        // madihah: currently using local file
        const myObj = fs.readFileSync("./detected_item.json");
        let parsed_myObj = JSON.parse(myObj);
        let item_id = parsed_myObj.class_id;

        console.log("item_id: " + item_id);
        const result = await sql.query`SELECT * FROM [miniMart].[dbo].[item_list] WHERE [item_id] = ${item_id}`;
        console.log("result");
        console.dir(result);

        for (let key in result) {
            if (key == "recordset") {
                console.log("found recordset");
                let recordset = result[key];
                console.log("recordset:");
                console.log(recordset);
                let name = "item_name";
                let price = "item_price";
                let i = 0;
                obj.Item = recordset[i][name];
                obj.Price = recordset[i][price].toFixed(2);
                break;
            }
        }
        
        obj.Quantity = 1;

        console.log("Name: " + obj.Item);
        console.log("Price: " + obj.Price);
        console.log("Obj");
        console.log(obj);

        items.push(obj);
        //module.exports = { items };
        console.log("items");
        console.dir(items);
    } catch (error) {
        console.error('Error executing getDetails():', error);
    } finally {
        // Close the connection when done
        sql.close();
    }
}
getDetails();
// export function addItem();