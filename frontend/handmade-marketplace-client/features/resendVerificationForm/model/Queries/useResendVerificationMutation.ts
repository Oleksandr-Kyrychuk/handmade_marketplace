import { authService } from "@/entities/auth/model"
import { useMutation } from "@tanstack/react-query"
import { toast } from "react-toastify";

function useResendVerificationMutation() {
  const {mutate: mutateResendVerif, isPending: mutateResendVerifPending} = useMutation({
    mutationFn: (email: string) => authService.resendVerification(email),
    onSuccess: (data: any) => {
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

  return {mutateResendVerif, mutateResendVerifPending}
}

export default useResendVerificationMutation;