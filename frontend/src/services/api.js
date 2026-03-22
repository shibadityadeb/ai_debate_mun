// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

/**
 * Generic fetch wrapper with error handling
 * @param {string} endpoint - API endpoint path
 * @param {object} options - Fetch options
 * @returns {Promise<any>} - Response data
 */
const fetchAPI = async (endpoint, options = {}) => {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    console.log(`[API] ${options.method || 'GET'} ${url}`);
    
    const response = await fetch(url, {
      headers: DEFAULT_HEADERS,
      ...options,
    });

    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');
    const data = isJson ? await response.json() : await response.text();

    // Check for HTTP error status
    if (!response.ok) {
      const errorMsg =
        (isJson && (data.detail || data.message)) ||
        (typeof data === 'string' && data.trim()) ||
        `HTTP Error: ${response.status}`;
      throw new Error(errorMsg);
    }

    return data;
  } catch (error) {
    const isNetworkError = error instanceof TypeError;
    const normalizedError = isNetworkError
      ? new Error(
          'Network request failed. If this is the deployed app, verify the backend is reachable and that CORS allows this frontend origin.'
        )
      : error;

    console.error('[API Error]', normalizedError.message);
    throw normalizedError;
  }
};

/**
 * Start a new debate
 * @param {string} topic - Debate topic
 * @param {array} countries - List of country names
 * @returns {Promise<object>} - Debate initialization response
 */
export const startDebate = async (topic, countries = []) => {
  if (!topic || topic.trim() === '') {
    throw new Error('Topic is required');
  }

  const payload = {
    topic,
    countries: Array.isArray(countries) ? countries : [],
  };

  return fetchAPI('/debate/start', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
};

/**
 * Run an ongoing debate
 * @param {string} topic - Debate topic
 * @param {array} countries - List of country names
 * @returns {Promise<object>} - Debate execution response with history, votes, verdict
 */
export const runDebate = async (topic, countries = []) => {
  if (!topic || topic.trim() === '') {
    throw new Error('Topic is required');
  }

  const payload = {
    topic,
    countries: Array.isArray(countries) ? countries : [],
  };

  return fetchAPI('/debate/run', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
};

/**
 * Get debate status
 * @param {string} debateId - Debate ID
 * @returns {Promise<object>} - Debate status
 */
export const getDebateStatus = async (debateId) => {
  if (!debateId) {
    throw new Error('Debate ID is required');
  }

  return fetchAPI(`/debate/${debateId}/status`, {
    method: 'GET',
  });
};

/**
 * Get debate messages
 * @param {string} debateId - Debate ID
 * @returns {Promise<array>} - Array of debate messages
 */
export const getDebateMessages = async (debateId) => {
  if (!debateId) {
    throw new Error('Debate ID is required');
  }

  return fetchAPI(`/debate/${debateId}/messages`, {
    method: 'GET',
  });
};

/**
 * Get current debate info
 * @returns {Promise<object>} - Current debate information
 */
export const getCurrentDebate = async () => {
  return fetchAPI('/debate/current', {
    method: 'GET',
  });
};
