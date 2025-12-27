import * as yup from "yup"
import { EmailConfirmDTO } from "@/entities/auth/model/types/interfaces";
import { verification_code } from "@/shared/validation/validationFields";


export const emailConfirmSchema: yup.ObjectSchema<EmailConfirmDTO> = yup.object().shape({
  verification_code
})