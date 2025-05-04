const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

exports.handler = async function(event, context) {
  // Set up Python path to include the installed dependencies
  const pythonPath = path.join(__dirname, 'streamlit', 'lib');
  process.env.PYTHONPATH = pythonPath;
  
  // Set Streamlit configuration to run headless
  process.env.STREAMLIT_SERVER_HEADLESS = 'true';
  process.env.STREAMLIT_SERVER_ADDRESS = '0.0.0.0';
  process.env.STREAMLIT_SERVER_PORT = '8501';
  
  try {
    // Execute Streamlit
    execSync('python -m streamlit run app.py', {
      env: process.env,
      stdio: 'inherit'
    });
    
    return {
      statusCode: 200,
      body: 'Streamlit app is running'
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to start Streamlit app' })
    };
  }
};
