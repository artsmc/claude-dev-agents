const User = require('../models/User');

// Mock data store
let users = [
  new User(1, 'John Doe', 'john@example.com'),
  new User(2, 'Jane Smith', 'jane@example.com'),
];
let nextId = 3;

/**
 * Get all users
 */
exports.getAllUsers = (req, res) => {
  res.json(users);
};

/**
 * Get user by ID
 */
exports.getUserById = (req, res) => {
  const userId = parseInt(req.params.id);
  const user = users.find(u => u.id === userId);

  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }

  res.json(user);
};

/**
 * Create a new user
 */
exports.createUser = (req, res) => {
  const { name, email } = req.body;

  if (!name || !email) {
    return res.status(400).json({ error: 'Name and email are required' });
  }

  const newUser = new User(nextId++, name, email);
  users.push(newUser);

  res.status(201).json(newUser);
};

/**
 * Update a user
 */
exports.updateUser = (req, res) => {
  const userId = parseInt(req.params.id);
  const userIndex = users.findIndex(u => u.id === userId);

  if (userIndex === -1) {
    return res.status(404).json({ error: 'User not found' });
  }

  const { name, email } = req.body;
  users[userIndex] = new User(userId, name || users[userIndex].name, email || users[userIndex].email);

  res.json(users[userIndex]);
};

/**
 * Delete a user
 */
exports.deleteUser = (req, res) => {
  const userId = parseInt(req.params.id);
  const userIndex = users.findIndex(u => u.id === userId);

  if (userIndex === -1) {
    return res.status(404).json({ error: 'User not found' });
  }

  users.splice(userIndex, 1);
  res.status(204).send();
};
