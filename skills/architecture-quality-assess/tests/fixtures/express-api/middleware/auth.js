/**
 * Simple authentication middleware
 */
function authenticate(req, res, next) {
  const token = req.headers.authorization;

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  // Mock validation
  if (token === 'Bearer valid-token') {
    next();
  } else {
    res.status(403).json({ error: 'Invalid token' });
  }
}

module.exports = { authenticate };
