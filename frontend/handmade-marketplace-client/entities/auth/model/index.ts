import { AuthApi } from "./API/auth-api";
import { AuthService } from "./Services/auth-service";

const authApi = new AuthApi();
const authService = new AuthService(authApi);

export {authService};