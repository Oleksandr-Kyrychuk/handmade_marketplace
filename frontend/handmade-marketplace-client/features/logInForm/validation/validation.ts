import * as yup from "yup"
import { email, password } from "@/shared/validation/validationFields";
import { LogInRequestDTO } from "../../../entities/auth/model/types/interfaces";

export const logInSchema: yup.ObjectSchema<LogInRequestDTO> = yup.object().shape({
  email,
  password
})