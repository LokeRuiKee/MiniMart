
const express = require('express');
const app = express();

app.get('/', function (req, res) {

    const sql = require("mssql/msnodesqlv8");

    // config for your database
    const config = {
        server: 'PTPNTE818',
        database: 'miniMart',
        driver: 'msnodesqlv8',
        options: {
            trustedConnection: true,
            trustServerCertificate: true
        },
    };

    // connect to your database
    sql.connect(config, function (err) {

        if (err) console.log(err);

        // create Request object
        const request = new sql.Request();

        // query to the database and get the records
        // SELECT [item_id], [item_name], [item_price] FROM [miniMart].[dbo].[item_list]
        request.query('select * from [miniMart].[dbo].[item_list]', function (err, recordset) {

            if (err) console.log(err)

            // send records as a response
            res.send(recordset);

        });
    });
});
// C:\Users\ptpmaahm\Source\Repos\MiniMart\prototypev2\server.js
const server = app.listen(5000, function () {
    console.log('Server is running..');
});