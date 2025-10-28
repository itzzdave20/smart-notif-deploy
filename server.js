const express = require('express');
const http = require('http');
const path = require('path');
const multer = require('multer');
const nodemailer = require('nodemailer');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const io = require('socket.io')(server);

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// upload setup -> saves to public/downloads
const uploadDir = path.join(__dirname, 'public', 'downloads');
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => cb(null, Date.now() + '-' + file.originalname)
});
const upload = multer({ storage });

// simple in-memory connected clients count (optional)
io.on('connection', socket => {
  console.log('client connected', socket.id);
  socket.on('disconnect', () => console.log('client disconnected', socket.id));
});

// upload endpoint (instructor uploads a file)
app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'no file' });
  const fileUrl = `/downloads/${req.file.filename}`;
  res.json({ url: fileUrl });
});

// send notification endpoint
app.post('/send-notification', async (req, res) => {
  try {
    const { title, message, downloadUrl, emails } = req.body;
    // 1) Emit to connected students
    io.emit('notification', { title, message, downloadUrl });

    // 2) Send email via Nodemailer (Gmail SMTP)
    const gmailUser = process.env.GMAIL_USER;
    const gmailPass = process.env.GMAIL_PASS;
    if (gmailUser && gmailPass && Array.isArray(emails) && emails.length) {
      const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: { user: gmailUser, pass: gmailPass }
      });

      const mailOptions = {
        from: gmailUser,
        to: emails.join(','),
        subject: title || 'New notification',
        html: `<p>${message}</p>${downloadUrl ? `<p><a href="${req.protocol}://${req.get('host')}${downloadUrl}">Download</a></p>` : ''}`
      };

      await transporter.sendMail(mailOptions);
    }

    res.json({ ok: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ ok: false, error: err.message });
  }
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server listening on ${PORT}`));