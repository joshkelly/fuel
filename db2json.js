#!/usr/local/bin/node

var fs = require('fs');
var sqlite3 = require('sqlite3');

var db = new sqlite3.Database("ldc_fuel.db");
var json = {'jalopynomos':{'vehicles':[], 'fuel':[], 'service':[]}};

function fuelTypes(t) {
	var val = 'X';
	switch(t.toUpperCase()){
		case 'DIESEL':
			val = 'D';
			break;
		case 'UNLEADED':
			val = 'U';
			break;
		case 'SUPER UNLEADED':
			val = 'S';
			break;
		default:
			console.log('Unknown fuel type "%s"', t);
			break;
	}
	return val;
}

function logThis(data){
	for (var i=0; i<data.length; i++){
		console.log(data[i])
	}
	var vstr = JSON.stringify(data);

	fs.writeFile('fuel.json', vstr, function (err) {
	if (err) throw err;
  		console.log('It\'s saved!');
	});
}


db.serialize(function () {
	db.all('select * from vehicles', function(err, recs){
		for (var i=0; i<recs.length; i++){
			var r = recs[i];
			var v = {};
			v.id = r.vehicle_id;
			v.regNo = r.reg_no;
			v.make = r.make;
			v.type = r.model;
			v.year = r.year;
			v.purchase = {
				date : r.purchase_date,
				price : r.purchase_price
			};
			v.fuel = {
				capacity : r.fuel_cap,
				type : fuelTypes(r.fuel_type)
			};
			v.oil = {
				capacity : r.oil_cap,
				type : r.oil_type
			};
			v.tyres = {
				front : {
					capacity : r.tyre_front_cap,
					type : r.tyre_front_type
				},
				rear : {
					capacity : r.tyre_rear_cap,
					type : r.tyre_rear_type
				}
			};
			v.notes = r.notes;

			
			json.jalopynomos.vehicles.push(v);
		}

		logThis(json);


	});

});
