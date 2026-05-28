import { createHmac } from 'crypto';

// Proxy Polymarket CLOB — contorna geo-block do GitHub Actions
// Deploy em Vercel Lambda (AWS) = IP diferente = sem bloqueio

async function signL2Headers(apiKey, apiSecret, apiPassphrase, method, path, body = '') {
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const message = timestamp + method.toUpperCase() + path + body;
  const signature = createHmac('sha256', Buffer.from(apiSecret, 'base64'))
    .update(message).digest('base64');
  return {
    'POLY-ACCESS-KEY': apiKey,
    'POLY-ACCESS-SIGNATURE': signature,
    'POLY-ACCESS-TIMESTAMP': timestamp,
    'POLY-ACCESS-PASSPHRASE': apiPassphrase,
  };
}

export default async function handler(req, res) {
  // Apenas aceita POST com auth header interno
  const authHeader = req.headers['x-gravia-key'];
  const GRAVIA_KEY = process.env.GRAVIA_PROXY_KEY || 'gravia2024';
  
  if (authHeader !== GRAVIA_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { endpoint, method = 'POST', body, api_key, api_secret, api_passphrase } = req.body;
  
  if (!endpoint) {
    return res.status(400).json({ error: 'Missing endpoint' });
  }

  try {
    const path = endpoint.replace('https://clob.polymarket.com', '');
    const bodyStr = body ? JSON.stringify(body) : '';
    
    const authHeaders = await signL2Headers(api_key, api_secret, api_passphrase, method, path, bodyStr);
    
    const response = await fetch(`https://clob.polymarket.com${path}`, {
      method: method.toUpperCase(),
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
      },
      body: bodyStr || undefined,
    });

    const data = await response.json();
    return res.status(response.status).json(data);
    
  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
