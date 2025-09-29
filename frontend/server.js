#!/usr/bin/env node
/**
 * Simple static file server with health endpoint for Railway deployment
 */

const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 4173;
const HOST = '0.0.0.0'; // Railway requires binding to 0.0.0.0

// Serve static files from dist directory
app.use(express.static(path.join(__dirname, 'dist')));

// Health check endpoint required by Railway
app.get('/api/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'z2-frontend'
  });
});

// Catch all handler: send back React's index.html file for client-side routing
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, HOST, () => {
  console.log(`Z2 Frontend server running on ${HOST}:${PORT}`);
  console.log(`Health check available at http://${HOST}:${PORT}/api/health`);
});