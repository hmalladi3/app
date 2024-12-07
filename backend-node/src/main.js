const express = require('express');
const cors = require('cors');
const { sequelize } = require('./db/db');
const accountRoutes = require('./routes/account');
const serviceRoutes = require('./routes/service');
const reviewRoutes = require('./routes/review');
const hashtagRoutes = require('./routes/hashtag');
const searchRoutes = require('./routes/search');

require('dotenv').config();

const app = express();

// Middleware
app.use(express.json());
app.use(cors({
  origin: ['http://localhost:8082', 'exp://192.168.6.77:8082'],
  credentials: true
}));

// Routes
app.use('/api', accountRoutes);
app.use('/api', serviceRoutes);
app.use('/api', reviewRoutes);
app.use('/api', hashtagRoutes);
app.use('/api', searchRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: err.message || 'Internal Server Error'
  });
});

// Initialize database and start server
const PORT = process.env.PORT || 8000;

async function startServer() {
  try {
    await sequelize.sync();
    console.log('Database synchronized');

    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Unable to start server:', error);
    process.exit(1);
  }
}

startServer();
