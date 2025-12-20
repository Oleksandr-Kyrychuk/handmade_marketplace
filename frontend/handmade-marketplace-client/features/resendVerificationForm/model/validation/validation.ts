import { email } from "@/shared/validation/validationFields"
import * as yup from "yup"

export const resendVerificationSchema = yup.object().shape({
  email
})