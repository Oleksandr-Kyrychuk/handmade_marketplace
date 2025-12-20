import { authService } from "@/entities/auth/model";
import { useMutation } from "@tanstack/react-query";
import { toast } from "react-toastify";

function useResetPasswordMutation() {
  const {mutate: mutateResetPassword, isPending: mutateResetPasswordPending, isError, error} = useMutation({
    mutationFn: (email: string) => authService.resetPassword(email),
    onSuccess: (data) => {
      toast.success('We have send letter to email. Please, check it');

      console.log('Log in success')
      console.log('Log in success', data)
      if(data?.success) {
        console.log('data.access', data)
      }
    },
    onError: (error) => {
      console.log('useResetPasswordMutation error', error)
    }
  })

  return {mutateResetPassword, mutateResetPasswordPending, isError, error}

}

export default useResetPasswordMutation;