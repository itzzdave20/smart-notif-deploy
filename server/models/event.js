const mongoose = require('mongoose');

const EventSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, required: true, index: true },
  title: String,
  description: String,
  start: Date,
  end: Date,
  recurrence: { type: String }, // e.g., 'RRULE:FREQ=DAILY;COUNT=10' or custom
  reminders: [{ minutesBefore: Number }], // e.g., [15, 60]
  createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Event', EventSchema);