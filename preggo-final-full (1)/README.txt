PregGo — merged frontend + CSV backend
=====================================

Contents:
- public/   -> all frontend HTML/CSS/JS, includes logo
- backend/  -> Node/Express server + data CSVs in backend/data/

Run locally:
1. Open terminal and cd into backend:
   cd backend
2. Install dependencies:
   npm install
3. Start server:
   npm run dev    (or `npm start` if nodemon not installed)
4. Open browser:
   http://localhost:5001/dashboard.html    (or index.html for login)

Notes:
- CSV files are in backend/data/*.csv
- API endpoints used by frontend:
  GET  /api/hospitals
  GET  /api/doctors
  GET  /api/appointments
  POST /api/appointments  {user,doctor,date,notes}
  POST /api/users/login   {email,password}
  POST /api/users/signup  {name,email,password}

Demo credentials: demo@preggo.com / demo123
