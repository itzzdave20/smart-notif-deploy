const express = require('express');
const router = express.Router();
const { Configuration, OpenAIApi } = require('openai');
const Conversation = require('../models/conversation'); // mongoose model
const rateLimit = require('express-rate-limit');

const config = new Configuration({ apiKey: process.env.OPENAI_API_KEY });
const openai = new OpenAIApi(config);

const limiter = rateLimit({ windowMs: 60_000, max: 30 }); // adjust

router.post('/chat', limiter, async (req, res) => {
  try {
    const { userId, conversationId, message } = req.body;
    if (!message) return res.status(400).json({ error: 'message required' });

    // Save user message
    const conv = await Conversation.findOneAndUpdate(
      { _id: conversationId || undefined, userId },
      { $push: { messages: { role: 'user', content: message } } },
      { upsert: true, new: true, setDefaultsOnInsert: true }
    );

    // Prepare context (limit tokens)
    const messages = conv.messages.slice(-20).map(m => ({ role: m.role, content: m.content }));
    const resp = await openai.createChatCompletion({
      model: 'gpt-4o-mini', // choose model available to you
      messages,
      max_tokens: 800,
      temperature: 0.2,
    });

    const aiText = resp.data.choices[0].message.content;

    // Save AI response
    conv.messages.push({ role: 'assistant', content: aiText });
    await conv.save();

    res.json({ conversationId: conv._id, reply: aiText });
  } catch (err) {
    console.error('AI chat error', err);
    res.status(500).json({ error: 'AI chat failed' });
  }
});

module.exports = router;