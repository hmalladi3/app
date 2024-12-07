const { DataTypes } = require('sequelize');
const { sequelize } = require('../db/db');

// Account Model
const Account = sequelize.define('Account', {
  username: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true
  },
  email: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
    validate: {
      isEmail: true
    }
  },
  password: {
    type: DataTypes.STRING,
    allowNull: false
  }
});

// Service Model
const Service = sequelize.define('Service', {
  title: {
    type: DataTypes.STRING,
    allowNull: false
  },
  description: {
    type: DataTypes.TEXT
  },
  price: {
    type: DataTypes.INTEGER,
    allowNull: false
  }
});

// Review Model
const Review = sequelize.define('Review', {
  rating: {
    type: DataTypes.INTEGER,
    allowNull: false,
    validate: {
      min: 1,
      max: 5
    }
  },
  title: {
    type: DataTypes.STRING,
    allowNull: false
  },
  body: {
    type: DataTypes.TEXT
  }
});

// Hashtag Model
const Hashtag = sequelize.define('Hashtag', {
  tag: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true
  }
});

// Define relationships
Account.hasMany(Service, { foreignKey: 'accountId' });
Service.belongsTo(Account, { foreignKey: 'accountId' });

Service.hasMany(Review, { foreignKey: 'serviceId' });
Review.belongsTo(Service, { foreignKey: 'serviceId' });

Account.hasMany(Review, { foreignKey: 'clientId' });
Review.belongsTo(Account, { as: 'client', foreignKey: 'clientId' });

Account.belongsToMany(Hashtag, { through: 'AccountHashtags' });
Hashtag.belongsToMany(Account, { through: 'AccountHashtags' });

module.exports = {
  Account,
  Service,
  Review,
  Hashtag
};
