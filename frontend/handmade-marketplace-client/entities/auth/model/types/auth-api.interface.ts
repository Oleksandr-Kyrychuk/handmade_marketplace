import { GetUserResponseDTO, LogInRequestDTO, LogInResponseDTO, SignUpRequestDTO, SignUpResponseDTO, VerifyEmailRequestDTO, VerifyEmailResponseDTO } from "./interfaces";

interface IAuthApi {
  logInAuth: (data: LogInRequestDTO) => Promise<LogInResponseDTO>;
  signUpAuth: (data: SignUpRequestDTO) => Promise<SignUpResponseDTO>;
  verifyEmailAuth: (data: VerifyEmailRequestDTO) => Promise<VerifyEmailResponseDTO>;
  resendVerification: (email: string) => void;
  resetPassword: (email: string) => void;
  getUser: () => Promise<GetUserResponseDTO>;
  logOutAuth: () => void;
}

export {type IAuthApi}