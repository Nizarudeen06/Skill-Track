/**
 * Enhanced API client with retry logic and better error handling
 */
import axios from 'axios'
import type { AxiosError, AxiosRequestConfig } from 'axios'

const MAX_RETRIES = 3
const RETRY_DELAY = 1000 // 1 second
const RETRY_STATUS_CODES = [408, 429, 500, 502, 503, 504]

/**
 * Check if an error is retryable
 */
function isRetryableError(error: AxiosError): boolean {
  if (!error.response) {
    // Network errors are retryable
    return true
  }

  // Retry on specific status codes
  return RETRY_STATUS_CODES.includes(error.response.status)
}

/**
 * Delay execution for specified milliseconds
 */
function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Make an API request with automatic retries on failure
 */
export async function apiRequestWithRetry<T>(
  config: AxiosRequestConfig,
  retries: number = MAX_RETRIES
): Promise<T> {
  try {
    const { api } = await import('../api')
    const response = await api.request<T>(config)
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error) && retries > 0 && isRetryableError(error)) {
      console.warn(
        `Request failed, retrying... (${MAX_RETRIES - retries + 1}/${MAX_RETRIES})`,
        error.message
      )

      // Exponential backoff
      await delay(RETRY_DELAY * (MAX_RETRIES - retries + 1))

      return apiRequestWithRetry<T>(config, retries - 1)
    }

    throw error
  }
}

/**
 * Format API error for display to user
 */
export function formatApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    // Handle validation errors
    if (error.response?.status === 422 && error.response?.data?.detail) {
      const detail = error.response.data.detail
      if (Array.isArray(detail)) {
        return detail
          .map((err: { loc?: unknown[]; msg?: string }) => {
            const field = err.loc?.at(-1) ?? 'Input'
            return `${String(field)}: ${err.msg ?? 'invalid'}`
          })
          .join('; ')
      }
      if (typeof detail === 'string') {
        return detail
      }
    }

    // Handle other HTTP errors
    if (error.response?.data?.detail) {
      return String(error.response.data.detail)
    }

    // Handle network errors
    if (!error.response) {
      return `Network Error: ${error.message}. Please check your internet connection.`
    }

    // Generic HTTP error
    return `Server Error (${error.response.status}): ${error.message}`
  }

  // Handle non-Axios errors
  if (error instanceof Error) {
    return error.message
  }

  return 'An unexpected error occurred. Please try again.'
}

/**
 * Check if current session is authenticated
 */
export function isAuthenticated(): boolean {
  const TOKEN_KEY = 'skilltrack_token'
  return Boolean(localStorage.getItem(TOKEN_KEY))
}

/**
 * Logout and clear authentication
 */
export function logout(): void {
  const TOKEN_KEY = 'skilltrack_token'
  localStorage.removeItem(TOKEN_KEY)
  window.location.href = '/login'
}

/**
 * Handle 401 Unauthorized globally
 */
export function setupAuthInterceptor(): void {
  import('../api').then(({ api }) => {
    api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401 && isAuthenticated()) {
          // Token expired or invalid
          console.warn('Authentication expired, redirecting to login...')
          logout()
        }
        return Promise.reject(error)
      }
    )
  })
}
