#!/usr/local/bin/node

var fs = require('fs');
var sqlite3 = require('sqlite3');

var db = new sqlite3.Database("ldc_fuel.db");
var json = {'jalopynomos':{'vehicles':[], 'fuel':[], 'service':[]}};
var beautify = require('js-beautify').js_beautify


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
	var data = JSON.stringify(data);
	data = beautify(data, { indent_size: 2 });

	fs.writeFile('fuel.json', data, function (err) {
	if (err) throw err;
  		console.log('It\'s saved!');
	});
}

function findVehicle(id){
	var v =null,
		result = null;
	for (var i =0; i < json.jalopynomos.vehicles.length; i++){
		v = json.jalopynomos.vehicles[i];
		if (v.id === id){
			result = v;
			break;
		}
	}
	return result;
}

function getVehicle(rec){
		var v = {};
		v.id = rec.vehicle_id;
		v.regNo = rec.reg_no;
		v.make = rec.make;
		v.type = rec.model;
		v.year = rec.year;
		v.purchase = {
			date : rec.purchase_date,
			price : rec.purchase_price
		};
		v.fuel = {
			capacity : rec.fuel_cap,
			type : fuelTypes(rec.fuel_type)
		};
		v.oil = {
			capacity : rec.oil_cap,
			type : rec.oil_type
		};
		v.tyres = {
			front : {
				capacity : rec.tyre_front_cap,
				type : rec.tyre_front_type
			},
			rear : {
				capacity : rec.tyre_rear_cap,
				type : rec.tyre_rear_type
			}
		};
		v.notes = rec.notes;
		v.fuelIDs = [];
		v.serviceIDs = [];

		json.jalopynomos.vehicles.push(v);
}

function getFuel(rec){
	var v = findVehicle(rec.vehicle_id);
	v.fuelIDs.push(rec.fuel_id);
	rec.id = rec.fuel_id
	delete rec.fuel_id;
	delete rec.vehicle_id;
	json.jalopynomos.fuel.push(rec);
}

function getService(rec){
	var v = findVehicle(rec.vehicle_id);
	v.serviceIDs.push(rec.service_id);
	rec.id = rec.service_id
	delete rec.service_id;
	delete rec.vehicle_id;
	json.jalopynomos.fuel.push(rec);
}

db.serialize(function () {
	db.each('select * from vehicles', function(err, rec){
		getVehicle(rec);
	}, function () {
		db.each('select * from fuel', function (err, rec){
			getFuel(rec);
		}, function() {
			db.each('select * from service', function (err, rec){
				getService(rec);
			}, function () {
				logThis(json);
			});
		});
	});
});
