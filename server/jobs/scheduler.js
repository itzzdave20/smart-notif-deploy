const cron = require('node-cron');
const Event = require('../models/event');
const nodemailer = require('nodemailer');

// Minimal mail transport (configure in env)
const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: Number(process.env.SMTP_PORT || 587),
  secure: false,
  auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS }
});

// Run every minute to check for reminders
cron.schedule('* * * * *', async () => {
  const now = new Date();
  const soon = new Date(now.getTime() + 60_000); // next minute
  try {
    const events = await Event.find({
      start: { $lte: soon },
    }).lean();

    for (const ev of events) {
      // compute if reminder should be sent based on 'reminders' and timing
      // For brevity, send a single reminder if event starts within next minute
      await transporter.sendMail({
        from: process.env.FROM_EMAIL,
        to: /* fetch user's email via userId */ 'user@example.com',
        subject: `Reminder: ${ev.title}`,
        text: `Event "${ev.title}" starts at ${ev.start}.`
      });
    }
  } catch (err) {
    console.error('Scheduler error', err);
  }
});