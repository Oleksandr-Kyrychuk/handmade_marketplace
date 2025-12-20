import { email } from "@/shared/validation/validationFields"
import * as yup from "yup"

export const resetEmailSchema = yup.object().shape({
  email
})