
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function (app) {
    app.use(
        '/api',
        createProxyMiddleware({
            target: process.env.REACT_APP_API_URL || 'http://127.0.0.1:8002',
            changeOrigin: true,
            logLevel: 'debug', // Enable verbose logging to see what's happening
            onError: (err, req, res) => {
                console.error('Proxy Error:', err);
                res.status(500).send('Proxy Error');
            }
        })
    );
};
