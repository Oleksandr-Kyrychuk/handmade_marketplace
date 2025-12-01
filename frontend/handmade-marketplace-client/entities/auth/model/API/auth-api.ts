
import { Request } from "@/shared/api/http/http-request"
import { IAuthApi } from "../types/auth-api.interface"
import { GetUserResponseDTO, LogInRequestDTO, LogInResponseDTO, SignUpRequestDTO, SignUpResponseDTO, VerifyEmailRequestDTO, VerifyEmailResponseDTO } from "../types/interfaces"
import { ApiEndpoints, HttpMethods } from "@/shared/api/http/enums"
import { useAuthStore } from "../Store/auth-store"


class AuthApi implements IAuthApi {
  async logInAuth(data: LogInRequestDTO): Promise<LogInResponseDTO> {
    return Request({
      url: ApiEndpoints.LOGIN,
      method: HttpMethods.POST,
      body: data
    })
  };

  async signUpAuth(data: SignUpRequestDTO): Promise<SignUpResponseDTO> {
    return Request({
      url: ApiEndpoints.SIGNUP,
      method: HttpMethods.POST,
      body: data
    })
  }

  async logOutAuth() {
    return Request({
      url: ApiEndpoints.LOGOUT,
      method: HttpMethods.POST,
    })
  }

  async verifyEmailAuth(data: VerifyEmailRequestDTO): Promise<VerifyEmailResponseDTO> {
    const { uid, token } = data
    return Request({
      url: `${ApiEndpoints.VERIFY_EMAIL}/${uid}/${token}` as ApiEndpoints,
      method: HttpMethods.POST,
      body: data
    })
  }

  async getUser(): Promise<GetUserResponseDTO> {
    const ACCESS_TOKEN = useAuthStore.getState().accessToken;

    if(!ACCESS_TOKEN) {
      throw new Error("Authorization token is missing.");
    }
    return Request({
      url: ApiEndpoints.GET_USER,
      method: HttpMethods.GET,
      headers: { Authorization: `Bearer ${ACCESS_TOKEN}` },
    })
  }
}

export {AuthApi}