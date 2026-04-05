export const enum ApiEndpoints {
  LOGIN = '/api/auth/login',
  SIGNUP= '/api/users/register',
  VERIFY_EMAIL= '/api/auth/verify-email',
  REFRESH_TOKEN= '/api/auth/refresh',
  RESEND_VERIFICATION= '/api/users/resend-verification',
  RESET_PASSWORD = '/api/users/password-reset',

  LOGOUT= '/api/auth/logout',
  
  GET_USER= '/api/user',
  PLATFORM_REVIEWS= '/api/platform-reviews',
  
  CATEGORY= '/api/categories',
  GET_HiTS= '/api/hits'
}