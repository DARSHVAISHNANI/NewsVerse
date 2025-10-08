import axios from 'axios';

// The base URL of your FastAPI backend
const API_URL = 'http://localhost:8000';

// Define interfaces for your data structures for type safety
export interface Article {
  _id: string;
  title: string;
  source: string;
  url: string;
  content: string;
  user_has_liked: boolean;
  user_has_rated: boolean;
  sentiment?: string;
  fact_check?: {
    llm_verdict?: boolean;
    fact_check_explanation?: string;
  };
  summarization?: {
    summary?: string;
    story_summary?: string;
  };
}

export interface User {
  name: string;
  email: string;
  picture: string;
}

export interface UserPreferences {
  phone_number: string;
  preferred_time: string;
}

export const getArticles = () => {
  return axios.get<Article[]>(`${API_URL}/api/articles`, { withCredentials: true });
};

export const getCurrentUser = () => {
  return axios.get<{ authenticated: boolean; user?: User }>(`${API_URL}/api/user`, { withCredentials: true });
};

export const toggleLike = (articleId: string, articleTitle: string) => {
  const formData = new URLSearchParams();
  formData.append('article_id', articleId);
  formData.append('article_title', articleTitle);
  // Tell axios to expect a 'liked' boolean in the response data
  return axios.post<{ message: string; liked: boolean }>(`${API_URL}/toggle-like`, formData, {
    withCredentials: true,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
};

export const getRecommendations = () => {
  return axios.get<Article[]>(`${API_URL}/api/recommendations`, { withCredentials: true });
};

export const getUserPreferences = () => {
  return axios.get<UserPreferences>(`${API_URL}/api/user-preference`, { withCredentials: true });
};

export const updateUserPreferences = (phoneNumber: string, preferredTime: string) => {
  const formData = new URLSearchParams();
  formData.append('phone_number', phoneNumber);
  formData.append('preferred_time', preferredTime);
  return axios.post(`${API_URL}/api/update-preference`, formData, {
    withCredentials: true,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
};

export const scheduleNotifications = () => {
  return axios.post<{ message: string }>(`${API_URL}/api/schedule-notifications`, {}, { withCredentials: true });
};

export const rateArticle = (articleId: string, rating: number) => {
  const formData = new URLSearchParams();
  formData.append('article_id', articleId);
  formData.append('rating', rating.toString());
  return axios.post(`${API_URL}/api/rate-article`, formData, {
    withCredentials: true,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
};

// New function to trigger the pipeline
export const triggerPipeline = () => {
    return axios.get(`${API_URL}/run-pipeline`, { withCredentials: true });
};

// ADD THIS NEW FUNCTION
export const logoutUser = () => {
  return axios.post(`${API_URL}/api/logout`, {}, { withCredentials: true });
};

// ADD THIS NEW FUNCTION
export const completeOnboarding = (phoneNumber: string, preferredTime: string) => {
  const formData = new URLSearchParams();
  formData.append('phone_number', phoneNumber);
  formData.append('preferred_time', preferredTime);
  return axios.post<{ user: User }>(`${API_URL}/api/complete-onboarding`, formData, {
    withCredentials: true,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
};

export const getRandomArticles = () => {
  return axios.get<Article[]>(`${API_URL}/api/random-articles`, { withCredentials: true });
};

export const deleteAccount = () => {
  return axios.delete(`${API_URL}/api/delete-account`, { withCredentials: true });
};