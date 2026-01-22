\
const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '../public')));

const DATA_DIR = path.join(__dirname, 'data');

function readCSV(filename){
  const p = path.join(DATA_DIR, filename);
  if(!fs.existsSync(p)) return [];
  const raw = fs.readFileSync(p,'utf8').trim();
  if(!raw) return [];
  const lines = raw.split('\\n');
  const headers = lines[0].split(',');
  const rows = lines.slice(1).map(l=>{
    const cols = l.split(',');
    const obj = {};
    headers.forEach((h,i)=> obj[h]=cols[i] || '');
    return obj;
  });
  return rows;
}

function appendCSV(filename, obj){
  const p = path.join(DATA_DIR, filename);
  // create if not exists with headers
  if(!fs.existsSync(p)){
    const headers = Object.keys(obj).join(',') + '\\n';
    fs.writeFileSync(p, headers, 'utf8');
  }
  const line = Object.values(obj).map(v=>String(v).replace(/\\n/g,' ')).join(',') + '\\n';
  fs.appendFileSync(p, line, 'utf8');
}

function nextId(rows){
  if(!rows.length) return '1';
  const max = Math.max(...rows.map(r=>parseInt(r.id||0)));
  return String(max+1);
}

// API endpoints

app.get('/api/hospitals', (req,res)=>{
  const h = readCSV('hospitals.csv');
  res.json({hospitals: h});
});

app.get('/api/doctors', (req,res)=>{
  const d = readCSV('doctors.csv');
  res.json({doctors: d});
});

app.get('/api/appointments', (req,res)=>{
  const a = readCSV('appointments.csv');
  res.json({appointments: a});
});

app.post('/api/appointments', (req,res)=>{
  const { user, doctor, date, notes } = req.body;
  if(!user || !doctor || !date) return res.status(400).json({success:false, message:'missing fields'});
  const rows = readCSV('appointments.csv');
  const id = nextId(rows);
  appendCSV('appointments.csv', { id, user, doctor, date, notes: notes || '' });
  res.json({success:true, id});
});

app.post('/api/users/login', (req,res)=>{
  const { email, password } = req.body;
  const users = readCSV('users.csv');
  const u = users.find(x => x.email === email && x.password === password);
  if(u) return res.json({success:true, user: {email:u.email, name: u.name}});
  return res.json({success:false, message:'Invalid credentials'});
});

app.post('/api/users/signup', (req,res)=>{
  const { name, email, password } = req.body;
  if(!email || !password) return res.status(400).json({success:false, message:'missing'});
  const users = readCSV('users.csv');
  if(users.find(x=>x.email===email)) return res.json({success:false, message:'User exists'});
  const id = nextId(users);
  appendCSV('users.csv', { id, email, password, name: name || '' });
  res.json({success:true, id});
});

const PORT = process.env.PORT || 5001;
app.listen(PORT, ()=> console.log('✅ Server running on http://localhost:'+PORT));
