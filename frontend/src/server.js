const express = require('express');
const path = require('path');
const app = express();

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'build')));
// ADD THIS
var cors = require('cors');
// app.use(cors());
app.use(cors({origin: true, credentials: true}));


app.use((req, res, next) => {
  res.setHeader("Content-Security-Policy", "default-src https: data: 'self' 'unsafe-inline' 'unsafe-eval'; connect-src https: '*'");
  next();
});

app.use(function(req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
    res.header("Access-Control-Allow-Headers", "x-access-token, Origin, X-Requested-With, Content-Type, Accept");
    next();
  });

// Handle all other routes by serving the index.html file
app.get('/*', function(req, res) {
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
