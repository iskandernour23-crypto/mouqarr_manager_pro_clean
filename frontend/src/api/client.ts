const getToken = () => {
  if (typeof window === 'undefined') return undefined;
  const stored = localStorage.getItem('mouqarr-auth');
  if (!stored) return undefined;
  try {
    return JSON.parse(stored).token as string;
  } catch (error) {
    return undefined;
  }
};

const buildHeaders = (extra?: HeadersInit): HeadersInit => {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(extra ?? {})
  };
};

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'فشل الاتصال بالخادم');
  }
  return response.json();
};

const get = async <T>(url: string): Promise<T> => {
  const response = await fetch(url, { headers: buildHeaders() });
  return handleResponse(response);
};

const post = async <T>(url: string, body?: unknown, options?: { params?: Record<string, string> }): Promise<T> => {
  const query = options?.params
    ? `?${new URLSearchParams(options.params).toString()}`
    : '';
  const response = await fetch(`${url}${query}`, {
    method: 'POST',
    headers: buildHeaders(),
    body: body !== undefined ? JSON.stringify(body) : null
  });
  return handleResponse(response);
};

const put = async <T>(url: string, body?: unknown): Promise<T> => {
  const response = await fetch(url, {
    method: 'PUT',
    headers: buildHeaders(),
    body: body !== undefined ? JSON.stringify(body) : null
  });
  return handleResponse(response);
};

export default { get, post, put };
