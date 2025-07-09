const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const unzipper = require('unzipper');
const fs = require('fs');
const path = require('path');

const app = express();
const port = 3000;

const upload = multer({ dest: 'uploads/' });

exec('which python3', (err, stdout, stderr) => {
  console.log("Using Python:", stdout);
});

app.post('/upload-folder', upload.single('folderZip'), async (req, res) => {
  const zipPath = req.file.path;
  const extractTo = path.join(__dirname, 'extracted');

  try {
    // Ensure extract directory exists
    fs.mkdirSync(extractTo, { recursive: true });

    // Extract ZIP
    fs.createReadStream(zipPath)
      .pipe(unzipper.Extract({ path: extractTo }))
      .on('close', () => {
        console.log('Folder extracted to:', extractTo);
        res.send('Folder received and extracted')
      });
    
    exec('python3 updateTflite.py', (error, stdout, stderr) => {
    if (error) {
      console.error(`Error: ${error.message}`);
      //return res.status(500).send('Script failed');
    }
    else if (stderr) {
      console.error(`Stderr: ${stderr}`);
      //return res.status(500).send(stderr);
    }

    console.log(`Output: ${stdout}`);
  });

  } catch (err) {
    console.error('Error extracting zip:', err);
    res.status(500).send('Failed to extract zip');
  }
});

app.get('/', (req, res) => {
  res.send('Server is reachable!');
});

app.get('/get-folder', (req, res) => {
  const filePath = path.join(__dirname, 'model.tflite');
  res.type('application/octet-stream'); 
  res.download(filePath, 'model.tflite')
})
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
