const express = require('express');
const app = express();
require('datejs');

const MongoClient = require('mongodb').MongoClient

var db

MongoClient.connect('mongodb://localhost:27017/deviceScanner', (err, database) => {
  if (err) return console.log(err)
  db = database
  app.listen(3000, () => {
    console.log('listening on 3000')
  })
})

app.get('/index', (req, res) => {
  var dateNow = Date.parse('now')
  console.log(parseInt(req.query.minutes))
  var dateFromInterval = Date.parse('t - '+parseInt(req.query.minutes)+' minutes')
  res.send('hello world: ' + req.query.name+ "Now: " + dateNow+ " - " + dateFromInterval)
})

app.get('/devicesForInterval', (req, res) => {
  var minutes = req.query.minutes
  var query = {}

  if (typeof minutes !== 'undefined') {
    var dateFromInterval = Date.parse('t - '+minutes+' minutes').toISOString()
    query = { "device.seen_at" : { $gt : new Date(dateFromInterval)}}
  }

  db.collection('devices').find(query).toArray(function(err, results) {
    console.log(results.length+" for interval "+ minutes)
    res.json(results);
  })
})

app.get('/isDevicePresent', (req, res) => {
  var macAddress = req.query.mac.toUpperCase()
  var query = {}
  var timeOut = 5

  var dateFromInterval = Date.parse('t - '+timeOut+' minutes').toISOString()

  var query = { "device.seen_at" : { $gt : new Date(dateFromInterval)}, "device.mac" : macAddress}
  db.collection('devices').find(query).toArray(function(err, results) {
    var isPresent = (results.length != 0)
    res.json({ 'timeout' : timeOut, 'timeout_unit' : 'minutes', 'deviceIsPresent' : isPresent, 'mac' : macAddress});
  })
})
