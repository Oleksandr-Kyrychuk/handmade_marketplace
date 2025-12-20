export const enum ApiEndpoints {
  LOGIN = '/auth/login',
  SIGNUP= '/users/register',
  VERIFY_EMAIL= '/auth/verify-email',
  REFRESH_TOKEN= '/auth/refresh',
  RESEND_VERIFICATION= '/users/resend-verification',
  RESET_PASSWORD = '/users/password-reset',

  LOGOUT= '/auth/logout',
  
  GET_USER= '/user',
  PLATFORM_REVIEWS= '/platform-reviews',
  
  CATEGORY= '/categories',
  GET_HiTS= '/hits'
}