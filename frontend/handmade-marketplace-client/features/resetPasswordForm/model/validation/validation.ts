import { email } from "@/shared/validation/validationFields"
import * as yup from "yup"

export const resetPasswordSchema = yup.object().shape({
  email
})