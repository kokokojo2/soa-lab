const {Sequelize, DataTypes} = require('sequelize');
const config = require("../config/config.json")['development'];

const sequelize = new Sequelize(
    config.database,
    config.username,
    config.password,
    {
        host: config.host,
        dialect: config.dialect
        // Додаткові налаштування, якщо потрібно
    }
);

const Transaction = sequelize.define('Transaction', {
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    status: {
        type: DataTypes.STRING,
        allowNull: false
    },
    type: {
        type: DataTypes.STRING,
        allowNull: false
    },
    amount: {
        type: DataTypes.FLOAT,
        allowNull: false
    },
    sender_id: {
        type: DataTypes.INTEGER,
        allowNull: true
    },
    receiver_id: {
        type: DataTypes.INTEGER,
        allowNull: true
    },
    title: {
        type: DataTypes.STRING,
        allowNull: true
    },
    failure_reason: {
        type: DataTypes.STRING,
        allowNull: true
    }
});

sequelize.sync()
    .then(() => {
        console.log('Таблиця створена успішно');
    })
    .catch(err => {
        console.error('Помилка під час створення таблиці:', err);
    });

module.exports = {Transaction};
