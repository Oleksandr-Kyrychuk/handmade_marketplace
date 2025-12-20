import { IAuthApi } from "../types/auth-api.interface";
import { IAuthService } from "../types/auth-service.interface";
import { GetUserResponseDTO, LogInRequestDTO, LogInResponseDTO, SignUpRequestDTO, SignUpResponseDTO, VerifyEmailRequestDTO, VerifyEmailResponseDTO } from "../types/interfaces";


class AuthService implements IAuthService {
  private authApi: IAuthApi;

  constructor(authApi: IAuthApi) {
    this.authApi = authApi;
  } 

  async logInAuth(data: LogInRequestDTO): Promise<LogInResponseDTO> {
    return this.authApi.logInAuth(data)
  }
  
  async signUpAuth(data: SignUpRequestDTO): Promise<SignUpResponseDTO> {
    return this.authApi.signUpAuth(data)
  }

  async logOutAuth() {
    return this.authApi.logOutAuth();
  }

  async verifyEmailAuth(data: VerifyEmailRequestDTO): Promise<VerifyEmailResponseDTO> {
    return this.authApi.verifyEmailAuth(data)
  }

  async resendVerification(email: string) {
    return this.authApi.resendVerification(email)
  }

  async resetPassword(email: string) {
    return this.authApi.resetPassword(email);
  }

  async getUser(): Promise<GetUserResponseDTO> {
    return this.authApi.getUser()
  }
}

export {AuthService}