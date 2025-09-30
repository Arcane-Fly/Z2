#!/usr/bin/env node
/**
 * Simple static file server with health endpoint for Railway deployment
 */

import express from 'express';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import rateLimit from 'express-rate-limit';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 4173;
const HOST = '0.0.0.0'; // Railway requires binding to 0.0.0.0

// Set up rate limiter for catch-all route
const catchAllLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per window per 15 minutes
  standardHeaders: true,
  legacyHeaders: false,
});

// Serve static files from dist directory
app.use(express.static(join(__dirname, 'dist')));

// Health check endpoint required by Railway
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

app.get('/api/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'z2-frontend'
  });
});

// Catch all handler: send back React's index.html file for client-side routing
app.get('*', catchAllLimiter, (req, res) => {
  res.sendFile(join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, HOST, () => {
  console.log(`Z2 Frontend server running on ${HOST}:${PORT}`);
  console.log(`Health check available at http://${HOST}:${PORT}/api/health`);
});