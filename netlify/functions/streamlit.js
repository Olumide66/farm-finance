const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Netlify function
exports.handler = async function(event, context) {
  // Check if this is just a status check request
  if (event.path === '/.netlify/functions/streamlit' && event.httpMethod === 'GET') {
    try {
      // Set up environment variables
      process.env.STREAMLIT_SERVER_PORT = '8501';
      process.env.STREAMLIT_SERVER_HEADLESS = 'true';
      process.env.STREAMLIT_SERVER_ENABLE_CORS = 'true';
      process.env.STREAMLIT_SERVER_ADDRESS = '0.0.0.0';
      
      // Try to start Streamlit as a child process
      const streamlitProcess = spawn('python', ['-m', 'streamlit', 'run', 'app.py'], {
        env: process.env,
        detached: true,
        stdio: 'ignore'
      });
      
      // Unref to allow the function to exit without waiting for the process
      streamlitProcess.unref();
      
      return {
        statusCode: 200,
        body: `
          <html>
            <head>
              <title>Farm Finance Manager</title>
              <meta http-equiv="refresh" content="5;url=https://farm-finance-manager.netlify.app/.netlify/functions/streamlit/app" />
              <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .loading { text-align: center; margin-top: 20px; }
                .spinner { border: 6px solid #f3f3f3; border-radius: 50%; border-top: 6px solid #3498db; width: 40px; height: 40px; animation: spin 2s linear infinite; margin: 0 auto; }
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
              </style>
            </head>
            <body>
              <h1>Farm Finance Manager</h1>
              <p>Attempting to start Streamlit application...</p>
              <div class="loading">
                <div class="spinner"></div>
                <p>This page will automatically redirect in 5 seconds.</p>
                <p>If the redirect doesn't work, <a href="https://farm-finance-manager.netlify.app/.netlify/functions/streamlit/app">click here</a>.</p>
              </div>
              <hr>
              <p><strong>Note:</strong> Netlify has significant limitations for running Streamlit applications:</p>
              <ul>
                <li>Netlify functions have a 10-second execution timeout</li>
                <li>They're designed for short-lived processes, not long-running servers</li>
                <li>There's limited support for persistent data storage</li>
              </ul>
              <p>For a better experience, consider using:</p>
              <ul>
                <li><a href="https://streamlit.io/cloud" target="_blank">Streamlit Cloud</a> - Designed for Streamlit apps</li>
                <li><a href="https://render.com" target="_blank">Render</a> - Good support for Python web apps</li>
                <li><a href="https://replit.com" target="_blank">Replit</a> - Works well for Streamlit (your current platform)</li>
              </ul>
            </body>
          </html>
        `,
        headers: {
          'Content-Type': 'text/html'
        }
      };
    } catch (error) {
      return {
        statusCode: 500,
        body: `
          <html>
            <head>
              <title>Error - Farm Finance Manager</title>
              <style>body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }</style>
            </head>
            <body>
              <h1>Error Starting Application</h1>
              <p>There was an error starting the Streamlit application: ${error.message}</p>
              <p>Streamlit applications are difficult to run on Netlify due to architectural limitations.</p>
              <p>Please consider using <a href="https://streamlit.io/cloud">Streamlit Cloud</a> or <a href="https://render.com">Render</a> instead.</p>
            </body>
          </html>
        `,
        headers: { 'Content-Type': 'text/html' }
      };
    }
  }
  
  // Proxy requests to the Streamlit instance (this won't work in practice due to Netlify's limitations)
  try {
    // This code attempts to proxy to Streamlit but will likely fail due to Netlify's architectural limitations
    return {
      statusCode: 200,
      body: `
        <html>
          <head>
            <title>Farm Finance Manager</title>
            <style>body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }</style>
          </head>
          <body>
            <h1>Farm Finance Manager - Unable to Connect</h1>
            <p>The Streamlit application cannot be accessed through Netlify functions.</p>
            <p>This is due to fundamental limitations in how Netlify functions work:</p>
            <ul>
              <li>Netlify functions execute for a maximum of 10 seconds</li>
              <li>They're stateless and can't maintain long-running processes</li>
              <li>They can't properly proxy to web servers running in the same environment</li>
            </ul>
            <h2>Recommended Hosting Alternatives</h2>
            <ul>
              <li><a href="https://streamlit.io/cloud">Streamlit Cloud</a> - Purpose-built for Streamlit apps with a free tier</li>
              <li><a href="https://render.com">Render</a> - Free tier available, good Python web app support</li>
              <li><a href="https://replit.com">Replit</a> - Your app is already working here!</li>
            </ul>
            <p>Return to <a href="https://farm-finance-manager.netlify.app">home page</a>.</p>
          </body>
        </html>
      `,
      headers: { 'Content-Type': 'text/html' }
    };
  } catch (error) {
    return {
      statusCode: 502,
      body: `
        <html>
          <head>
            <title>Connection Error - Farm Finance Manager</title>
          </head>
          <body>
            <h1>Unable to Connect to Streamlit</h1>
            <p>Error: ${error.message}</p>
            <p>Return to <a href="https://farm-finance-manager.netlify.app">home page</a>.</p>
          </body>
        </html>
      `,
      headers: { 'Content-Type': 'text/html' }
    };
  }
};
