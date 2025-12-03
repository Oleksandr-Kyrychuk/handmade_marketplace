import * as yup from "yup"
import { SignUpRequestDTO } from "@/entities/auth/model/types/interfaces";
import {  agree_terms, email, password, password_confirm, surname, username } from "@/shared/validation/validationFields";

export const signupSchema: yup.ObjectSchema<SignUpRequestDTO> = yup.object().shape({
  username,
  surname,
  email,
  password,
  password_confirm,
  agree_terms
})