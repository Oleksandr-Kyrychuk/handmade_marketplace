import { authService } from "@/entities/auth/model";
import { useMutation } from "@tanstack/react-query";
import { toast } from "react-toastify";

function useResetVerificationMutation() {
  const {mutate: mutateResetVerif, isPending: mutateResetVerifPending, isError, error} = useMutation({
    mutationFn: (email: string) => authService.resendVerification(email),
    onSuccess: (data) => {
      toast.success('We have send letter to email. Please, check it');

      console.log('Log in success')
      console.log('Log in success', data)
      if(data?.success) {
        console.log('data.access', data)
      }
    },
    onError: (error) => [
      console.log('useResetVerificationMutation error', error)
    ]
  })

  return {mutateResetVerif, mutateResetVerifPending, isError, error}

}

export default useResetVerificationMutation;