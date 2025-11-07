const cron = require('node-cron');
const nodemailer = require('nodemailer');

// Validate SMTP config early and create transporter only if present
const smtpHost = process.env.SMTP_HOST;
const smtpPort = Number(process.env.SMTP_PORT || 587);
const smtpUser = process.env.SMTP_USER;
const smtpPass = process.env.SMTP_PASS;
const fromEmail = process.env.FROM_EMAIL;

let transporter = null;
if (smtpHost && smtpUser && smtpPass && fromEmail) {
  transporter = nodemailer.createTransport({
    host: smtpHost,
    port: smtpPort,
    secure: smtpPort === 465,
    auth: { user: smtpUser, pass: smtpPass }
  });

  // verify connection but don't throw — log result
  transporter.verify().then(() => {
    console.log('SMTP transporter verified');
  }).catch(err => {
    console.error('SMTP transporter verification failed:', err.message);
    transporter = null;
  });
} else {
  console.warn('SMTP not fully configured — scheduler reminders disabled.');
}

// Run every minute to check for reminders
cron.schedule('* * * * *', async () => {
  try {
    if (!transporter) return; // skip if no mailer

    // require the Event model here so a broken require doesn't crash startup
    const Event = require('../models/event');

    const now = new Date();
    const soon = new Date(now.getTime() + 60_000); // next minute

    const events = await Event.find({
      start: { $lte: soon }
    }).lean();

    for (const ev of events) {
      try {
        // fetch user's email using ev.userId if available; placeholder for now
        const toEmail = ev.email || 'user@example.com';

        await transporter.sendMail({
          from: fromEmail,
          to: toEmail,
          subject: `Reminder: ${ev.title}`,
          text: `Event "${ev.title}" starts at ${ev.start}.`
        });

        console.log(`Reminder sent for event ${ev._id}`);
      } catch (sendErr) {
        console.error('Failed to send reminder for event', ev._id, sendErr.message);
      }
    }
  } catch (err) {
    console.error('Scheduler job error:', err && err.message ? err.message : err);
  }
});