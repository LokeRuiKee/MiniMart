// to execute file, open terminal, run following commands:
// cd C:\Users\ptpmaahm\Source\Repos\MiniMart\prototypev2\dbConnection
// node server.js

// C:\Users\ptpmaahm\Source\Repos\MiniMart\prototypev2\dbConnection\server.js
const express = require('express');
const app = express();
const sql = require("mssql/msnodesqlv8");
const cors = require("cors");

app.use(cors());
app.get('/item_details',
    async function (req, res) {

        try {
            // config for database
            const config = {
                server: 'PTPNTE818',
                database: 'miniMart',
                driver: 'msnodesqlv8',
                options: {
                    trustedConnection: true,
                    trustServerCertificate: true
                },
            };
            // connect with database
            await sql.connect(config);

            // select all item IDs with name and price
            const all_items = await sql.query`SELECT * FROM [miniMart].[dbo].[item_list]`;
            console.log("1. all item details: ");
            console.log(all_items);

            for (let key in all_items) {
                if (key == "recordset") {
                    console.log("2. found recordset");
                    let recordset = all_items[key];
                    console.log("3. recordset:");
                    console.log(recordset);
                    res.send(recordset);
                    break;
                }
            }
        } catch (error) {
            console.error('Error executing:', error);
        } finally {
            // Close the connection when done
            sql.close();
        }
    });

// post data on port 5000 (localhost:5000/item_details)
app.post("/item_details",
    function (req, res) {
        let recordset = req.recordset;
        res.send(recordset);
    });

// post qr code on port 5000 (localhost:5000/qr_code)
// qr code path: C:\Users\ptpmaahm\Source\Repos\MiniMart\prototypev2\dummy qr.png
//app.post("/qr_code",
//    function (req, res) {
//        res.sendFile(
//            //__dirname + "/dummy qr.png"
//            "C:/Users/ptpmaahm/Source/Repos/MiniMart/prototypev2/dummy qr.png"
//        );
//    });

app.listen(5000, function () {
    console.log("server is running on port 5000");
})