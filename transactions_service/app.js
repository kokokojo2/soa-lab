const express = require('express');
const bodyParser = require('body-parser');
const {Sequelize} = require('sequelize');
const config = require("./config/config.json")['development'];
const models = require('./models/models.js');

const app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

const sequelize = new Sequelize(config.database, config.username, config.password, {
    host: config.host,
    dialect: config.dialect
});

const Transaction = models.Transaction;

const PORT = process.env.PORT || 3000;

sequelize.authenticate()
    .then(() => {
        console.log('Підключено до бази даних');
        return sequelize.sync(); // Синхронізуємо моделі з базою даних перед запуском сервера
    })
    .then(() => {
        app.listen(PORT, () => {
            console.log(`Сервер запущено на порту ${PORT}`);
        });
    })
    .catch(error => {
        console.error('Помилка при підключенні до бази даних:', error);
    });

app.get('/transactions', async (req, res) => {
    try {
        const allTransactions = await Transaction.findAll();
        res.status(200).json(allTransactions);
    } catch (error) {
        res.status(500).json({error: 'Помилка при отриманні всіх транзакцій'});
    }
});

// Обробник для створення нової транзакції
app.post('/transactions', async (req, res) => {
    try {
        const newTransaction = await Transaction.create(req.body);
        res.status(201).json(newTransaction);
    } catch (error) {
        console.log(error);
        res.status(500).json({error: 'Помилка при створенні транзакції'});
    }
});

// Обробник для отримання всіх транзакцій для конкретного користувача
app.get('/transactions/user/:id', async (req, res) => {
    try {
        const userId = req.params.id;

        const userTransactions = await Transaction.findAll({
            where: {
                [Sequelize.Op.or]: [
                    {sender_id: userId},
                    {receiver_id: userId}
                ]
            }
        });

        res.status(200).json(userTransactions);
    } catch (error) {
        res.status(500).json({error: 'Помилка при отриманні транзакцій користувача'});
    }
});


// Обробник для отримання надісланих транзакцій конкретним юзером
app.get('/transactions/sent/:sender_id', async (req, res) => {
    try {
        const sentTransactions = await Transaction.findAll({
            where: {
                sender_id: req.params.sender_id
            }
        });
        res.status(200).json(sentTransactions);
    } catch (error) {
        res.status(500).json({error: 'Помилка при отриманні надісланих транзакцій'});
    }
});

// Обробник для отримання отриманих транзакцій конкретним юзером
app.get('/transactions/received/:receiver_id', async (req, res) => {
    try {
        const receivedTransactions = await Transaction.findAll({
            where: {
                receiver_id: req.params.receiver_id
            }
        });
        res.status(200).json(receivedTransactions);
    } catch (error) {
        res.status(500).json({error: 'Помилка при отриманні отриманих транзакцій'});
    }
});

// Обробник для оновлення транзакції за її ID
app.put('/transactions/:transaction_id', async (req, res) => {
    try {
        const transaction = await Transaction.findByPk(req.params.transaction_id);
        if (!transaction) {
            return res.status(404).json({error: 'Транзакція не знайдена'});
        }
        await transaction.update(req.body);
        res.status(200).json(transaction);
    } catch (error) {
        res.status(500).json({error: 'Помилка при оновленні транзакції'});
    }
});

module.exports = app; // Якщо потрібно експортувати app для тестування або іншого використання
